"""
Data Fetcher Module

This module handles fetching real estate listings data from various APIs and sources.
Supports multiple data sources including MLS, Zillow, Redfin, and custom APIs.
Includes comprehensive pagination support for API endpoints and structured search queries.
Focuses on active market listings (sales and rentals) rather than static property data.
"""

import logging
import requests
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any, Generator, Union

from ..api.rentcast_client import RentCastClient, RentCastClientError
from ..api.http_client import HTTPClientError
from ..schemas.rentcast_schemas import PropertiesResponse, ListingsResponse
from .search_queries import (
    SearchCriteria, SearchQueryBuilder, search_by_address, 
    search_by_location, search_by_coordinates, search_around_address
)

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Container for API response data and metadata."""
    data: List[Dict[str, Any]]
    total_count: Optional[int] = None
    has_more: bool = False
    next_offset: Optional[int] = None
    source: Optional[str] = None


class PaginationManager:
    """Manages pagination for API requests."""
    
    def __init__(self, default_limit: int = 50, max_limit: int = 500):
        """
        Initialize pagination manager.
        
        Args:
            default_limit: Default page size
            max_limit: Maximum allowed page size
        """
        self.default_limit = default_limit
        self.max_limit = max_limit
    
    def paginate_request(self, client: RentCastClient, endpoint: str,
                        params: Dict[str, Any],
                        max_pages: Optional[int] = None) -> Generator[APIResponse, None, None]:
        """
        Generator that yields paginated API responses.
        
        Args:
            client: API client instance
            endpoint: API endpoint to call
            params: Base request parameters
            max_pages: Maximum number of pages to fetch (None for unlimited)
            
        Yields:
            APIResponse objects containing page data
        """
        limit = min(params.get('limit', self.default_limit), self.max_limit)
        offset = params.get('offset', 0)
        pages_fetched = 0
        
        while max_pages is None or pages_fetched < max_pages:
            try:
                # Update pagination parameters
                request_params = params.copy()
                request_params.update({
                    'limit': limit,
                    'offset': offset
                })
                
                # Make API request
                logger.info(f"Fetching page {pages_fetched + 1} with offset "
                           f"{offset}, limit {limit}")
                
                response: Union[PropertiesResponse, ListingsResponse, Any]
                
                if endpoint == 'properties':
                    response = client.search_properties(**request_params)
                elif endpoint == 'listings_sale':
                    response = client.get_listings_sale(**request_params)
                elif endpoint == 'listings_rental_long_term':
                    response = client.get_listings_rental_long_term(**request_params)
                else:
                    logger.error(f"Unknown endpoint for pagination: {endpoint}")
                    break
                
                # Process response based on type
                data: List[Dict[str, Any]] = []
                total_count: Optional[int] = None
                has_more: bool = False
                next_offset: Optional[int] = None
                
                # Check response type and extract data
                if hasattr(response, 'properties'):
                    # This is a PropertiesResponse
                    properties = getattr(response, 'properties', [])
                    data = [prop.to_dict() for prop in properties]
                    total_count = getattr(response, 'total_count', None)
                    has_more = getattr(response, 'has_more', False) or False
                    next_offset = getattr(response, 'next_offset', None)
                elif hasattr(response, 'listings'):
                    # This is a ListingsResponse
                    listings = getattr(response, 'listings', [])
                    data = [listing.to_dict() for listing in listings]
                    total_count = getattr(response, 'total_count', None)
                    has_more = getattr(response, 'has_more', False) or False
                    next_offset = getattr(response, 'next_offset', None)
                else:
                    # Handle single property or other response types
                    if hasattr(response, 'to_dict'):
                        data = [response.to_dict()]
                    elif isinstance(response, dict):
                        data = [response]
                    else:
                        data = []
                    total_count = len(data)
                    has_more = False
                    next_offset = None
                
                # Create response object
                api_response = APIResponse(
                    data=data,
                    total_count=total_count,
                    has_more=has_more,
                    next_offset=next_offset,
                    source='rentcast'
                )
                
                yield api_response
                
                # Check if we should continue
                if not data or len(data) < limit or not has_more:
                    logger.info(f"Reached end of results after {pages_fetched + 1} pages")
                    break
                
                # Update offset for next page
                if next_offset is not None:
                    offset = next_offset
                else:
                    offset += limit
                
                pages_fetched += 1
                
                # Add delay between requests to respect rate limits
                time.sleep(0.1)
                
            except (RentCastClientError, HTTPClientError) as e:
                logger.error(f"API error during pagination: {str(e)}")
                break
            except Exception as e:
                logger.error(f"Unexpected error during pagination: {str(e)}")
                break
    
    def fetch_all_pages(self, client: RentCastClient, endpoint: str,
                       params: Dict[str, Any],
                       max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch all pages and return combined results.
        
        Args:
            client: API client instance
            endpoint: API endpoint to call
            params: Base request parameters
            max_pages: Maximum number of pages to fetch
            
        Returns:
            Combined list of all results
        """
        all_data = []
        total_fetched = 0
        
        for page_response in self.paginate_request(client, endpoint, params, max_pages):
            all_data.extend(page_response.data)
            total_fetched += len(page_response.data)
            
            logger.info(f"Fetched {len(page_response.data)} items in this page, "
                       f"{total_fetched} total so far")
        
        logger.info(f"Pagination complete. Total items fetched: {total_fetched}")
        return all_data


class RealEstateDataFetcher:
    """Main class for fetching real estate listings data from various sources."""
    
    def __init__(self, api_config: Dict[str, Any]):
        """
        Initialize the data fetcher with API configuration.
        
        Args:
            api_config: Dictionary containing API keys and endpoints
        """
        self.api_config = api_config
        self.session = requests.Session()
        self.rate_limits = {}  # Track rate limits for different APIs
        
        # Initialize pagination manager
        self.pagination_manager = PaginationManager(
            default_limit=api_config.get('default_page_size', 50),
            max_limit=api_config.get('max_page_size', 500)
        )
        
    def fetch_all_sources(self) -> List[Dict[str, Any]]:
        """
        Fetch data from all configured sources.
        
        Returns:
            List of listing dictionaries
        """
        all_listings = []
        
        try:
            # Fetch from each configured source
            if self.api_config.get('rentcast_enabled', False):
                rentcast_data = self.fetch_rentcast_data()
                all_listings.extend(rentcast_data)
                            
            # Remove duplicates based on listing ID, address, or property ID
            unique_listings = self._remove_duplicates(all_listings)
            logger.info(f"Fetched {len(unique_listings)} unique listings "
                       f"from {len(all_listings)} total")
            
            return unique_listings
            
        except Exception as e:
            logger.error(f"Error fetching data from sources: {str(e)}")
            return []
    
    def fetch_rentcast_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from RentCast API using zip codes configuration.
        Searches for both sales and rental listings based on configuration.
        
        Returns:
            List of listing dictionaries from RentCast listings
        """
        logger.info("Fetching listings data from RentCast using zip codes configuration")
        listings = []
        
        try:
            api_key = self.api_config.get('rentcast_api_key')
            if not api_key:
                logger.warning("RentCast API key not configured")
                return []
            
            endpoint = self.api_config.get('rentcast_endpoint', 'https://api.rentcast.io/v1')
            rate_limit = self.api_config.get('rentcast_rate_limit', 100)
            
            # Get zip codes configuration from api_config
            zip_codes = self.api_config.get('zip_codes', [])
            zip_processing = self.api_config.get('zip_code_processing', {})
            
            if not zip_codes:
                logger.warning("No zip codes configured for data fetching")
                return []
            
            # Initialize RentCast client
            with RentCastClient(
                api_key=api_key,
                base_url=endpoint,
                rate_limit=rate_limit
            ) as client:
                
                # Test connection first
                if not client.test_connection():
                    logger.error("RentCast API connection test failed")
                    return []
                
                # Extract configuration parameters
                listings_per_zip = zip_processing.get('listings_per_zip', zip_processing.get('properties_per_zip', 100))  # Backward compatibility
                fetch_sales = zip_processing.get('fetch_sales', True)
                fetch_rentals = zip_processing.get('fetch_rentals', True)
                delay_between_zips = zip_processing.get('delay_between_zips', 2)
                property_types = zip_processing.get('property_types', ['Single Family', 'Condo'])
                filters = zip_processing.get('filters', {})
                
                # Process each zip code
                for zip_code in zip_codes:
                    logger.info(f"Processing zip code: {zip_code}")
                    
                    # Fetch sales listings if enabled
                    if fetch_sales:
                        for prop_type in property_types:
                            # Create search kwargs for sales listings endpoint (same parameter names as rental)
                            sales_search_kwargs = {
                                'zipcode': zip_code,  # Note: zipcode (no underscore) for listings endpoint
                                'propertyType': prop_type,  # Note: propertyType (camelCase) for listings endpoint
                                'limit': listings_per_zip
                            }
                            
                            # Apply additional filters with correct parameter names for listings endpoint
                            if filters.get('min_beds'):
                                sales_search_kwargs['bedrooms'] = filters['min_beds']
                            if filters.get('min_baths'):
                                sales_search_kwargs['bathrooms'] = filters['min_baths']
                            if filters.get('max_price'):
                                sales_search_kwargs['maxPrice'] = filters['max_price']
                            
                            try:
                                logger.info(f"Searching sales listings in {zip_code} for {prop_type}")
                                response = client.get_listings_sale(**sales_search_kwargs)
                                
                                # Process response data - handle ListingsResponse object
                                listing_data = []
                                if hasattr(response, 'listings'):
                                    # ListingsResponse object
                                    listing_data = response.listings
                                elif isinstance(response, dict) and 'listings' in response:
                                    # Dict response
                                    listing_data = response['listings']
                                elif isinstance(response, list):
                                    # Direct list
                                    listing_data = response
                                
                                if listing_data:
                                    for listing in listing_data:
                                        # Convert listing object to dict if needed
                                        if hasattr(listing, 'to_dict'):
                                            listing_dict: Dict[str, Any] = listing.to_dict()
                                        else:
                                            listing_dict = listing  # type: ignore
                                        normalized_listing = self._normalize_rentcast_listing(
                                            listing_dict)
                                        listings.append(normalized_listing)
                                        
                            except RentCastClientError as e:
                                logger.error(f"RentCast sales listings error for {zip_code}, "
                                           f"{prop_type}: {e}")
                                continue
                    
                    # Fetch rental listings if enabled
                    if fetch_rentals:
                        for prop_type in property_types:
                            # Create separate search kwargs for rental endpoint (different parameter names)
                            rental_search_kwargs = {
                                'zipcode': zip_code,  # Note: zipcode (no underscore) for rental endpoint
                                'propertyType': prop_type,  # Note: propertyType (camelCase) for rental endpoint
                                'limit': listings_per_zip
                            }
                            
                            # Apply additional filters with correct parameter names for rental endpoint
                            if filters.get('min_beds'):
                                rental_search_kwargs['bedrooms'] = filters['min_beds']
                            if filters.get('min_baths'):
                                rental_search_kwargs['bathrooms'] = filters['min_baths']
                            if filters.get('max_price'):
                                rental_search_kwargs['maxRent'] = filters['max_price']
                            
                            try:
                                logger.info(f"Searching rentals in {zip_code} for {prop_type}")
                                # Use listings endpoint for rentals
                                response = client.get_listings_rental_long_term(**rental_search_kwargs)
                                
                                # Process response - rental listings endpoint returns PropertiesResponse
                                property_data = []
                                if hasattr(response, 'properties'):
                                    # PropertiesResponse object (what rental listings endpoint returns)
                                    property_data = response.properties
                                elif isinstance(response, dict) and 'properties' in response:
                                    # Dict response
                                    property_data = response['properties']
                                elif isinstance(response, list):
                                    # Direct list
                                    property_data = response
                                
                                if property_data:
                                    for listing in property_data:
                                        # Convert listing object to dict if needed
                                        if hasattr(listing, 'to_dict'):
                                            listing_dict: Dict[str, Any] = listing.to_dict()
                                        else:
                                            listing_dict = listing  # type: ignore
                                        normalized_listing = self._normalize_rentcast_listing(
                                            listing_dict)
                                        listings.append(normalized_listing)
                                        
                            except RentCastClientError as e:
                                logger.error(f"RentCast rental search error for {zip_code}, "
                                           f"{prop_type}: {e}")
                                continue
                    
                    # Add delay between zip code processing
                    if delay_between_zips > 0:
                        logger.info(f"Waiting {delay_between_zips} seconds before next zip code")
                        time.sleep(delay_between_zips)
                
                logger.info(f"Successfully fetched {len(listings)} listings from RentCast")
                
        except Exception as e:
            logger.error(f"Error fetching RentCast data: {str(e)}")
            
        return listings

    def _normalize_rentcast_listing(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize RentCast listing data to standard format."""
        return {
            'source': 'rentcast',
            'listing_id': str(listing.get('id', listing.get('listingId', ''))),
            'property_id': str(listing.get('propertyId', listing.get('property_id', ''))),
            'address': listing.get('address', listing.get('formattedAddress', '')),
            'city': listing.get('city', ''),
            'state': listing.get('state', ''),
            'zip_code': listing.get('zipCode', listing.get('zip', '')),
            'price': listing.get('price', listing.get('listPrice', listing.get('rent'))),
            'bedrooms': listing.get('bedrooms', listing.get('beds')),
            'bathrooms': listing.get('bathrooms', listing.get('baths')),
            'square_feet': listing.get('squareFootage', listing.get('sqft')),
            'lot_size': listing.get('lotSize'),
            'year_built': listing.get('yearBuilt'),
            'property_type': listing.get('propertyType', ''),
            'listing_date': listing.get('listDate', listing.get('lastSeenDate')),
            'listing_type': listing.get('listingType', 'unknown'),  # sale, rental, etc.
            'status': listing.get('status', 'active'),
            'days_on_market': listing.get('daysOnMarket'),
            'mls_number': listing.get('mlsNumber', ''),
            'url': listing.get('url', ''),
            'latitude': listing.get('latitude', listing.get('lat')),
            'longitude': listing.get('longitude', listing.get('lng')),
            'fetched_at': datetime.now().isoformat()
        }
    
    def _remove_duplicates(self, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate listings based on listing ID, address, or property ID."""
        seen = set()
        unique_listings = []
        
        for listing in listings:
            # Create a unique identifier using multiple possible keys
            identifier = (
                listing.get('listing_id', ''),
                listing.get('address', '').lower(),
                listing.get('city', '').lower(),
                listing.get('zip_code', ''),
                listing.get('property_id', '')
            )
            
            if identifier not in seen:
                seen.add(identifier)
                unique_listings.append(listing)
        
        return unique_listings
    
    def _check_rate_limit(self, api_name: str) -> None:
        """Check and enforce rate limits for API calls."""
        now = time.time()
        
        if api_name not in self.rate_limits:
            self.rate_limits[api_name] = {'calls': 0, 'reset_time': now + 60}
        
        rate_limit_info = self.rate_limits[api_name]
        
        # Reset counter if time window has passed
        if now > rate_limit_info['reset_time']:
            rate_limit_info['calls'] = 0
            rate_limit_info['reset_time'] = now + 60
        
        # Check if we've hit the limit
        max_calls = self.api_config.get(f'{api_name}_rate_limit', 60)  # Default 60 calls per minute
        
        if rate_limit_info['calls'] >= max_calls:
            sleep_time = rate_limit_info['reset_time'] - now
            logger.info(f"Rate limit reached for {api_name}, "
                       f"sleeping for {sleep_time:.1f} seconds")
            time.sleep(sleep_time)
            rate_limit_info['calls'] = 0
            rate_limit_info['reset_time'] = time.time() + 60
        
        rate_limit_info['calls'] += 1

    # Paginated fetch methods
    
    def fetch_properties_paginated(self, search_params: Dict[str, Any],
                                  max_pages: Optional[int] = None) -> Generator[APIResponse, None, None]:
        """
        Fetch properties with pagination support.
        
        Args:
            search_params: Search parameters for properties
            max_pages: Maximum number of pages to fetch
            
        Yields:
            APIResponse objects containing property data
        """
        logger.info("Starting paginated property fetch")
        
        try:
            api_key = self.api_config.get('rentcast_api_key')
            if not api_key:
                logger.warning("RentCast API key not configured")
                return
            
            endpoint = self.api_config.get('rentcast_endpoint', 'https://api.rentcast.io/v1')
            rate_limit = self.api_config.get('rentcast_rate_limit', 100)
            
            # Initialize RentCast client
            with RentCastClient(
                api_key=api_key,
                base_url=endpoint,
                rate_limit=rate_limit
            ) as client:
                
                # Test connection first
                if not client.test_connection():
                    logger.error("RentCast API connection test failed")
                    return
                
                # Use pagination manager to fetch properties
                yield from self.pagination_manager.paginate_request(
                    client, 'properties', search_params, max_pages
                )
                
        except Exception as e:
            logger.error(f"Error in paginated property fetch: {str(e)}")
    
    def fetch_listings_paginated(self, search_params: Dict[str, Any],
                                listing_type: str = 'sale',
                                max_pages: Optional[int] = None) -> Generator[APIResponse, None, None]:
        """
        Fetch listings with pagination support.
        
        Args:
            search_params: Search parameters for listings
            listing_type: Type of listings ('sale' or 'rental')
            max_pages: Maximum number of pages to fetch
            
        Yields:
            APIResponse objects containing listing data
        """
        logger.info(f"Starting paginated {listing_type} listing fetch")
        
        try:
            api_key = self.api_config.get('rentcast_api_key')
            if not api_key:
                logger.warning("RentCast API key not configured")
                return
            
            endpoint = self.api_config.get('rentcast_endpoint', 'https://api.rentcast.io/v1')
            rate_limit = self.api_config.get('rentcast_rate_limit', 100)
            
            # Initialize RentCast client
            with RentCastClient(
                api_key=api_key,
                base_url=endpoint,
                rate_limit=rate_limit
            ) as client:
                
                # Test connection first
                if not client.test_connection():
                    logger.error("RentCast API connection test failed")
                    return
                
                # Determine endpoint based on listing type
                if listing_type.lower() == 'sale':
                    endpoint_name = 'listings_sale'
                elif listing_type.lower() in ['rental', 'rent']:
                    endpoint_name = 'listings_rental_long_term'
                else:
                    logger.error(f"Unknown listing type: {listing_type}")
                    return
                
                # Use pagination manager to fetch listings
                yield from self.pagination_manager.paginate_request(
                    client, endpoint_name, search_params, max_pages
                )
                
        except Exception as e:
            logger.error(f"Error in paginated listing fetch: {str(e)}")
    
    def fetch_all_properties_paginated(self, search_params: Dict[str, Any],
                                      max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch all properties using pagination and return combined results.
        
        Args:
            search_params: Search parameters for properties
            max_pages: Maximum number of pages to fetch
            
        Returns:
            Combined list of all property data
        """
        all_properties = []
        
        for response in self.fetch_properties_paginated(search_params, max_pages):
            all_properties.extend(response.data)
            logger.info(f"Collected {len(response.data)} properties from page, "
                       f"total so far: {len(all_properties)}")
        
        logger.info(f"Paginated fetch complete. Total properties: {len(all_properties)}")
        return all_properties
    
    def fetch_all_listings_paginated(self, search_params: Dict[str, Any],
                                    listing_type: str = 'sale',
                                    max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch all listings using pagination and return combined results.
        
        Args:
            search_params: Search parameters for listings
            listing_type: Type of listings ('sale' or 'rental')
            max_pages: Maximum number of pages to fetch
            
        Returns:
            Combined list of all listing data
        """
        all_listings = []
        
        for response in self.fetch_listings_paginated(search_params, listing_type, max_pages):
            all_listings.extend(response.data)
            logger.info(f"Collected {len(response.data)} listings from page, "
                       f"total so far: {len(all_listings)}")
        
        logger.info(f"Paginated fetch complete. Total listings: {len(all_listings)}")
        return all_listings
    
    # === STRUCTURED SEARCH METHODS ===
    
    def search_properties_structured(self, search_criteria: SearchCriteria) -> List[Dict[str, Any]]:
        """
        Search for properties using structured search criteria.
        
        Args:
            search_criteria: Structured search criteria object
            
        Returns:
            List of property dictionaries matching the criteria
        """
        logger.info(f"Starting structured property search")
        logger.info(f"Search type: {getattr(search_criteria, 'search_type', 'Unknown')}")
        
        try:
            api_key = self.api_config.get('rentcast_api_key')
            if not api_key:
                logger.warning("RentCast API key not configured")
                return []
            
            endpoint = self.api_config.get('rentcast_endpoint', 'https://api.rentcast.io/v1')
            rate_limit = self.api_config.get('rentcast_rate_limit', 100)
            
            # Initialize RentCast client
            with RentCastClient(
                api_key=api_key,
                base_url=endpoint,
                rate_limit=rate_limit
            ) as client:
                
                # Test connection first
                if not client.test_connection():
                    logger.error("RentCast API connection test failed")
                    return []
                
                # Use structured search
                response = client.search_properties_structured(search_criteria)
                
                if hasattr(response, 'properties') and response.properties:
                    properties = [prop.to_dict() for prop in response.properties]
                    logger.info(f"Found {len(properties)} properties")
                    return properties
                else:
                    logger.info("No properties found matching criteria")
                    return []
                    
        except Exception as e:
            logger.error(f"Error in structured property search: {str(e)}")
            return []
    
    def search_listings_structured(self, search_criteria: SearchCriteria,
                                  listing_type: str = 'sale') -> List[Dict[str, Any]]:
        """
        Search for listings using structured search criteria.
        
        Args:
            search_criteria: Structured search criteria object
            listing_type: Type of listings ('sale' or 'rental')
            
        Returns:
            List of listing dictionaries matching the criteria
        """
        logger.info(f"Starting structured {listing_type} listing search")
        logger.info(f"Search type: {getattr(search_criteria, 'search_type', 'Unknown')}")
        
        try:
            api_key = self.api_config.get('rentcast_api_key')
            if not api_key:
                logger.warning("RentCast API key not configured")
                return []
            
            endpoint = self.api_config.get('rentcast_endpoint', 'https://api.rentcast.io/v1')
            rate_limit = self.api_config.get('rentcast_rate_limit', 100)
            
            # Initialize RentCast client
            with RentCastClient(
                api_key=api_key,
                base_url=endpoint,
                rate_limit=rate_limit
            ) as client:
                
                # Test connection first
                if not client.test_connection():
                    logger.error("RentCast API connection test failed")
                    return []
                
                # Use structured search based on listing type
                if listing_type.lower() == 'sale':
                    response_data = client.search_listings_sale_structured(search_criteria)
                elif listing_type.lower() in ['rental', 'rent']:
                    response_data = client.search_listings_rental_structured(search_criteria)
                else:
                    logger.error(f"Unknown listing type: {listing_type}")
                    return []
                
                # Extract listings from response
                listings = response_data.get('listings', [])
                logger.info(f"Found {len(listings)} {listing_type} listings")
                return listings
                    
        except Exception as e:
            logger.error(f"Error in structured {listing_type} listing search: {str(e)}")
            return []
    
    # === CONVENIENCE SEARCH METHODS ===
    
    def search_by_address(self, address: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for a specific property by address.
        
        Args:
            address: Full property address (Street, City, State, Zip format recommended)
            **kwargs: Additional search criteria
            
        Returns:
            List of property dictionaries (typically one property)
        """
        search_criteria = search_by_address(address, **kwargs)
        return self.search_properties_structured(search_criteria)
    
    def search_by_location(self, city: Optional[str] = None,
                          state: Optional[str] = None,
                          zip_code: Optional[str] = None,
                          **kwargs) -> List[Dict[str, Any]]:
        """
        Search for properties in a specific location.
        
        Args:
            city: City name
            state: State abbreviation (2 characters)
            zip_code: ZIP code (5 digits)
            **kwargs: Additional search criteria
            
        Returns:
            List of property dictionaries matching the location
        """
        search_criteria = search_by_location(city=city, state=state,
                                             zip_code=zip_code, **kwargs)
        return self.search_properties_structured(search_criteria)
    
    def search_by_coordinates(self, latitude: float, longitude: float,
                             radius: float = 5.0,
                             **kwargs) -> List[Dict[str, Any]]:
        """
        Search for properties within a radius of coordinates.
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius: Search radius in miles
            **kwargs: Additional search criteria
            
        Returns:
            List of property dictionaries within the radius
        """
        search_criteria = search_by_coordinates(latitude=latitude,
                                               longitude=longitude,
                                               radius=radius, **kwargs)
        return self.search_properties_structured(search_criteria)
    
    def search_around_address(self, address: str, radius: float = 5.0,
                             **kwargs) -> List[Dict[str, Any]]:
        """
        Search for properties within a radius of an address.
        
        Args:
            address: Center address for the search
            radius: Search radius in miles
            **kwargs: Additional search criteria
            
        Returns:
            List of property dictionaries within the radius
        """
        search_criteria = search_around_address(address=address, radius=radius, **kwargs)
        return self.search_properties_structured(search_criteria)
    
    def create_search_builder(self) -> SearchQueryBuilder:
        """
        Create a new search query builder for constructing complex searches.
        
        Returns:
            SearchQueryBuilder instance for method chaining
        """
        return SearchQueryBuilder()
    
    def search_with_builder(self, builder: SearchQueryBuilder) -> List[Dict[str, Any]]:
        """
        Execute a search using a search query builder.
        
        Args:
            builder: Configured SearchQueryBuilder instance
            
        Returns:
            List of property dictionaries matching the built criteria
        """
        search_criteria = builder.build()
        return self.search_properties_structured(search_criteria)
