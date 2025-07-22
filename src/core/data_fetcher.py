"""
Data Fetcher Module

This module handles fetching real estate data from various APIs and sources.
Supports multiple data sources including MLS, Zillow, Redfin, and custom APIs.
Includes comprehensive pagination support for API endpoints and structured search queries.
"""

import requests
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any, Generator, Tuple, Union
from datetime import datetime, timedelta
import time
import json
from dataclasses import dataclass

from ..api.rentcast_client import RentCastClient, RentCastClientError
from ..api.http_client import HTTPClientError
from ..schemas.rentcast_schemas import PropertiesResponse, ListingsResponse
from .search_queries import (
    SearchCriteria, SpecificAddressSearch, LocationSearch, GeographicalAreaSearch,
    SearchQueryBuilder, search_by_address, search_by_location, search_by_coordinates,
    search_around_address, SearchType, PropertyType
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
                        params: Dict[str, Any], max_pages: Optional[int] = None) -> Generator[APIResponse, None, None]:
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
                logger.info(f"Fetching page {pages_fetched + 1} with offset {offset}, limit {limit}")
                
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
                       params: Dict[str, Any], max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
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
    """Main class for fetching real estate data from various sources."""
    
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
            List of property dictionaries
        """
        all_properties = []
        
        try:
            # Fetch from each configured source
            if self.api_config.get('rentcast_enabled', False):
                rentcast_data = self.fetch_rentcast_data()
                all_properties.extend(rentcast_data)
                
            if self.api_config.get('zillow_enabled', False):
                zillow_data = self.fetch_zillow_data()
                all_properties.extend(zillow_data)
                
            if self.api_config.get('redfin_enabled', False):
                redfin_data = self.fetch_redfin_data()
                all_properties.extend(redfin_data)
                
            if self.api_config.get('mls_enabled', False):
                mls_data = self.fetch_mls_data()
                all_properties.extend(mls_data)
                
            if self.api_config.get('custom_apis'):
                for api_name, api_config in self.api_config['custom_apis'].items():
                    custom_data = self.fetch_custom_api_data(api_name, api_config)
                    all_properties.extend(custom_data)
            
            # Remove duplicates based on address or property ID
            unique_properties = self._remove_duplicates(all_properties)
            logger.info(f"Fetched {len(unique_properties)} unique properties from {len(all_properties)} total")
            
            return unique_properties
            
        except Exception as e:
            logger.error(f"Error fetching data from sources: {str(e)}")
            return []
    
    def fetch_zillow_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from Zillow API.
        
        Returns:
            List of property dictionaries from Zillow
        """
        logger.info("Fetching data from Zillow")
        properties = []
        
        try:
            # This is a placeholder implementation
            # In reality, you'd need to use Zillow's API or web scraping
            # Note: Zillow's API access is restricted
            
            api_key = self.api_config.get('zillow_api_key')
            if not api_key:
                logger.warning("Zillow API key not configured")
                return []
            
            # Example implementation for a hypothetical Zillow API
            search_params = self.api_config.get('zillow_search_params', {})
            
            for location in search_params.get('locations', []):
                self._check_rate_limit('zillow')
                
                url = f"{self.api_config.get('zillow_endpoint', '')}/search"
                params = {
                    'location': location,
                    'api_key': api_key,
                    'status': 'for_sale',
                    'limit': 100
                }
                
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                if 'properties' in data:
                    for prop in data['properties']:
                        normalized_prop = self._normalize_zillow_property(prop)
                        properties.append(normalized_prop)
                        
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Error fetching Zillow data: {str(e)}")
            
        return properties
    
    def fetch_rentcast_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from RentCast API using the dedicated client.
        
        Returns:
            List of property dictionaries from RentCast
        """
        logger.info("Fetching data from RentCast")
        properties = []
        
        try:
            api_key = self.api_config.get('rentcast_api_key')
            if not api_key:
                logger.warning("RentCast API key not configured")
                return []
            
            endpoint = self.api_config.get('rentcast_endpoint', 'https://api.rentcast.io/v1')
            rate_limit = self.api_config.get('rentcast_rate_limit', 100)
            search_params = self.api_config.get('rentcast_search_params', {})
            
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
                
                # Search for properties based on configured locations
                locations = search_params.get('locations', [])
                property_types = search_params.get('property_types', [])
                limit_per_location = search_params.get('limit', 50)
                
                for location in locations:
                    # Parse location string (e.g., "Austin, TX")
                    location_parts = [part.strip() for part in location.split(',')]
                    
                    search_kwargs = {
                        'limit': limit_per_location
                    }
                    
                    if len(location_parts) >= 2:
                        search_kwargs['city'] = location_parts[0]
                        search_kwargs['state'] = location_parts[1]
                    elif len(location_parts) == 1:
                        # Could be city name or ZIP code
                        if location_parts[0].isdigit():
                            search_kwargs['zip_code'] = location_parts[0]
                        else:
                            search_kwargs['city'] = location_parts[0]
                    
                    # Search for each property type if specified
                    if property_types:
                        for prop_type in property_types:
                            search_kwargs['property_type'] = prop_type
                            try:
                                logger.info(f"Searching RentCast: {location}, {prop_type}")
                                response = client.search_properties(**search_kwargs)
                                
                                # Process response data - handle PropertiesResponse object
                                property_data = []
                                if hasattr(response, 'properties'):
                                    # PropertiesResponse object
                                    property_data = response.properties
                                elif isinstance(response, dict) and 'properties' in response:
                                    # Dict response
                                    property_data = response['properties']
                                elif isinstance(response, list):
                                    # Direct list
                                    property_data = response
                                
                                if property_data:
                                    for prop in property_data:
                                        # Convert Property object to dict if needed
                                        prop_dict = prop.to_dict() if hasattr(prop, 'to_dict') else prop
                                        normalized_prop = self._normalize_rentcast_property(prop_dict)
                                        properties.append(normalized_prop)
                                        
                            except RentCastClientError as e:
                                logger.error(f"RentCast search error for {location}, {prop_type}: {e}")
                                continue
                    else:
                        # Search without property type filter
                        try:
                            logger.info(f"Searching RentCast: {location}")
                            response = client.search_properties(**search_kwargs)
                            
                            # Process response data - handle PropertiesResponse object
                            property_data = []
                            if hasattr(response, 'properties'):
                                # PropertiesResponse object
                                property_data = response.properties
                            elif isinstance(response, dict) and 'properties' in response:
                                # Dict response
                                property_data = response['properties']
                            elif isinstance(response, list):
                                # Direct list
                                property_data = response
                            
                            if property_data:
                                for prop in property_data:
                                    # Convert Property object to dict if needed
                                    prop_dict = prop.to_dict() if hasattr(prop, 'to_dict') else prop
                                    normalized_prop = self._normalize_rentcast_property(prop_dict)
                                    properties.append(normalized_prop)
                                    
                        except RentCastClientError as e:
                            logger.error(f"RentCast search error for {location}: {e}")
                            continue
                
                logger.info(f"Successfully fetched {len(properties)} properties from RentCast")
                
        except Exception as e:
            logger.error(f"Error fetching RentCast data: {str(e)}")
            
        return properties
    
    def fetch_redfin_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from Redfin API.
        
        Returns:
            List of property dictionaries from Redfin
        """
        logger.info("Fetching data from Redfin")
        properties = []
        
        try:
            # Placeholder implementation
            # Redfin has limited public API access
            api_config = self.api_config.get('redfin_config', {})
            
            # Example implementation
            logger.info("Redfin data fetching not implemented - placeholder")
            
        except Exception as e:
            logger.error(f"Error fetching Redfin data: {str(e)}")
            
        return properties
    
    def fetch_mls_data(self) -> List[Dict[str, Any]]:
        """
        Fetch data from MLS API.
        
        Returns:
            List of property dictionaries from MLS
        """
        logger.info("Fetching data from MLS")
        properties = []
        
        try:
            mls_config = self.api_config.get('mls_config', {})
            api_key = mls_config.get('api_key')
            
            if not api_key:
                logger.warning("MLS API key not configured")
                return []
            
            # Example MLS API implementation
            url = mls_config.get('endpoint', '')
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            search_params = mls_config.get('search_params', {})
            
            self._check_rate_limit('mls')
            response = self.session.get(url, headers=headers, params=search_params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if 'listings' in data:
                for listing in data['listings']:
                    normalized_prop = self._normalize_mls_property(listing)
                    properties.append(normalized_prop)
                    
        except Exception as e:
            logger.error(f"Error fetching MLS data: {str(e)}")
            
        return properties
    
    def fetch_custom_api_data(self, api_name: str, api_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch data from a custom API source.
        
        Args:
            api_name: Name of the custom API
            api_config: Configuration for the custom API
            
        Returns:
            List of property dictionaries from the custom API
        """
        logger.info(f"Fetching data from custom API: {api_name}")
        properties = []
        
        try:
            url = api_config.get('endpoint')
            if not url:
                logger.warning(f"No endpoint configured for custom API: {api_name}")
                return []
                
            headers = api_config.get('headers', {})
            params = api_config.get('params', {})
            
            self._check_rate_limit(api_name)
            response = self.session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Apply custom data transformation if specified
            transform_func = api_config.get('transform_function')
            if transform_func:
                # This would need to be implemented based on specific requirements
                pass
            else:
                # Default transformation
                properties_key = api_config.get('properties_key', 'properties')
                if properties_key in data:
                    for prop in data[properties_key]:
                        normalized_prop = self._normalize_custom_property(prop, api_config)
                        properties.append(normalized_prop)
                        
        except Exception as e:
            logger.error(f"Error fetching data from {api_name}: {str(e)}")
            
        return properties
    
    def _normalize_zillow_property(self, prop: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Zillow property data to standard format."""
        return {
            'source': 'zillow',
            'property_id': str(prop.get('zpid', '')),
            'address': prop.get('address', ''),
            'city': prop.get('city', ''),
            'state': prop.get('state', ''),
            'zip_code': prop.get('zipcode', ''),
            'price': prop.get('price'),
            'bedrooms': prop.get('bedrooms'),
            'bathrooms': prop.get('bathrooms'),
            'square_feet': prop.get('livingArea'),
            'lot_size': prop.get('lotAreaValue'),
            'year_built': prop.get('yearBuilt'),
            'property_type': prop.get('homeType', ''),
            'listing_date': prop.get('datePosted'),
            'days_on_market': prop.get('daysOnZillow'),
            'url': prop.get('detailUrl', ''),
            'latitude': prop.get('latitude'),
            'longitude': prop.get('longitude'),
            'fetched_at': datetime.now().isoformat()
        }
    
    def _normalize_mls_property(self, prop: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize MLS property data to standard format."""
        return {
            'source': 'mls',
            'property_id': str(prop.get('ListingId', '')),
            'address': prop.get('UnparsedAddress', ''),
            'city': prop.get('City', ''),
            'state': prop.get('StateOrProvince', ''),
            'zip_code': prop.get('PostalCode', ''),
            'price': prop.get('ListPrice'),
            'bedrooms': prop.get('BedroomsTotal'),
            'bathrooms': prop.get('BathroomsTotal'),
            'square_feet': prop.get('LivingArea'),
            'lot_size': prop.get('LotSizeSquareFeet'),
            'year_built': prop.get('YearBuilt'),
            'property_type': prop.get('PropertyType', ''),
            'listing_date': prop.get('OnMarketDate'),
            'days_on_market': prop.get('DaysOnMarket'),
            'url': prop.get('VirtualTourURLUnbranded', ''),
            'latitude': prop.get('Latitude'),
            'longitude': prop.get('Longitude'),
            'fetched_at': datetime.now().isoformat()
        }
    
    def _normalize_rentcast_property(self, prop: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize RentCast property data to standard format."""
        return {
            'source': 'rentcast',
            'property_id': str(prop.get('id', prop.get('propertyId', ''))),
            'address': prop.get('address', prop.get('formattedAddress', '')),
            'city': prop.get('city', ''),
            'state': prop.get('state', ''),
            'zip_code': prop.get('zipCode', prop.get('zip', '')),
            'price': prop.get('price', prop.get('listPrice', prop.get('rent'))),
            'bedrooms': prop.get('bedrooms', prop.get('beds')),
            'bathrooms': prop.get('bathrooms', prop.get('baths')),
            'square_feet': prop.get('squareFootage', prop.get('sqft')),
            'lot_size': prop.get('lotSize'),
            'year_built': prop.get('yearBuilt'),
            'property_type': prop.get('propertyType', ''),
            'listing_date': prop.get('listDate', prop.get('lastSeenDate')),
            'days_on_market': prop.get('daysOnMarket'),
            'url': prop.get('url', ''),
            'latitude': prop.get('latitude', prop.get('lat')),
            'longitude': prop.get('longitude', prop.get('lng')),
            'fetched_at': datetime.now().isoformat()
        }
    
    def _normalize_custom_property(self, prop: Dict[str, Any], api_config: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize custom API property data to standard format."""
        field_mapping = api_config.get('field_mapping', {})
        
        normalized = {
            'source': api_config.get('source_name', 'custom'),
            'fetched_at': datetime.now().isoformat()
        }
        
        # Map fields according to configuration
        for standard_field, source_field in field_mapping.items():
            if source_field in prop:
                normalized[standard_field] = prop[source_field]
        
        return normalized
    
    def _remove_duplicates(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate properties based on address or property ID."""
        seen = set()
        unique_properties = []
        
        for prop in properties:
            # Create a unique identifier
            identifier = (
                prop.get('address', '').lower(),
                prop.get('city', '').lower(),
                prop.get('zip_code', '')
            )
            
            if identifier not in seen:
                seen.add(identifier)
                unique_properties.append(prop)
        
        return unique_properties
    
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
            logger.info(f"Rate limit reached for {api_name}, sleeping for {sleep_time:.1f} seconds")
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
    
    def search_by_location(self, city: Optional[str] = None, state: Optional[str] = None,
                          zip_code: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
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
        search_criteria = search_by_location(city=city, state=state, zip_code=zip_code, **kwargs)
        return self.search_properties_structured(search_criteria)
    
    def search_by_coordinates(self, latitude: float, longitude: float, radius: float = 5.0,
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
        search_criteria = search_by_coordinates(latitude=latitude, longitude=longitude, 
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
