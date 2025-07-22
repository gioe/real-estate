"""
RentCast API Client

Specialized client for interacting with RentCast API endpoints.
Handles authentication, request formatting, and response parsing.
"""

import logging
from typing import Dict, List, Any, Optional, Union, TYPE_CHECKING
from datetime import datetime
import json

from .http_client import BaseHTTPClient, RateLimiter, HTTPClientError
from ..schemas.rentcast_schemas import Property, PropertiesResponse, parse_property_response

if TYPE_CHECKING:
    from ..core.search_queries import SearchCriteria

logger = logging.getLogger(__name__)


class RentCastClientError(HTTPClientError):
    """Custom exception for RentCast API errors."""
    pass


class RentCastClient:
    """Client for interacting with RentCast API."""
    
    # API endpoint mappings
    ENDPOINTS = {
        # Properties endpoints
        'properties': '/properties',
        'properties_random': '/properties/random',
        'property_details': '/properties/{id}',
        
        # AVM endpoints
        'avm_value': '/avm/value',
        'avm_rent_long_term': '/avm/rent/long-term',
        
        # Listings endpoints
        'listings_sale': '/listings/sale',
        'listings_sale_details': '/listings/sale/{id}',
        'listings_rental_long_term': '/listings/rental/long-term',
        'listings_rental_long_term_details': '/listings/rental/long-term/{id}',
        
        # Markets endpoint
        'markets': '/markets',
        }
    
    def __init__(self, api_key: str, base_url: str = "https://api.rentcast.io/v1",
                 rate_limit: int = 100, timeout: int = 30, max_retries: int = 3):
        """
        Initialize RentCast client.
        
        Args:
            api_key: RentCast API key
            base_url: Base URL for RentCast API
            rate_limit: Maximum requests per minute
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key
        
        # Set up default headers based on curl example
        default_headers = {
            'Accept': 'application/json',
            'X-Api-Key': self.api_key,
            'User-Agent': 'RealEstateAnalyzer/1.0'
        }
        
        # Create rate limiter (RentCast typically limits to 100 requests per minute)
        rate_limiter = RateLimiter(max_requests=rate_limit, time_window=60)
        
        # Initialize base HTTP client
        self.client = BaseHTTPClient(
            base_url=base_url,
            default_headers=default_headers,
            timeout=timeout,
            max_retries=max_retries,
            rate_limiter=rate_limiter
        )
        
        logger.info(f"RentCast client initialized with rate limit: {rate_limit} req/min")
    
    def _validate_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate RentCast API response."""
        if 'error' in response_data:
            error_msg = response_data.get('error', {})
            if isinstance(error_msg, dict):
                message = error_msg.get('message', 'Unknown RentCast API error')
                code = error_msg.get('code', 'UNKNOWN')
            else:
                message = str(error_msg)
                code = 'UNKNOWN'
            
            raise RentCastClientError(f"RentCast API error [{code}]: {message}")
        
        return response_data
    
    def search_properties_structured(self, search_criteria: 'SearchCriteria') -> PropertiesResponse:
        """
        Search for properties using structured search criteria.
        
        Args:
            search_criteria: Structured search criteria object
            
        Returns:
            PropertiesResponse containing matching properties
        """
        params = search_criteria.to_query_params()
        
        # Convert numeric values to strings for API
        params = {k: str(v) if isinstance(v, (int, float)) else v 
                 for k, v in params.items() if v is not None}
        
        logger.info(f"Structured property search with params: {params}")
        search_type_name = getattr(search_criteria, 'search_type', 'Unknown')
        logger.info(f"Search type: {search_type_name}")
        
        try:
            response_data = self.client.get(self.ENDPOINTS['properties'], params=params)
            validated_response = self._validate_response(response_data)
            return PropertiesResponse.from_dict(validated_response)
        
        except HTTPClientError as e:
            logger.error(f"Failed to search properties with structured criteria: {e}")
            raise RentCastClientError(f"Structured property search failed: {e}")
    
    def search_listings_sale_structured(self, search_criteria: 'SearchCriteria') -> Dict[str, Any]:
        """
        Search for sale listings using structured search criteria.
        
        Args:
            search_criteria: Structured search criteria object
            
        Returns:
            Dict containing sale listings response
        """
        params = search_criteria.to_query_params()
        
        # Convert numeric values to strings for API
        params = {k: str(v) if isinstance(v, (int, float)) else v 
                 for k, v in params.items() if v is not None}
        
        logger.info(f"Structured sale listings search with params: {params}")
        search_type_name = getattr(search_criteria, 'search_type', 'Unknown')
        logger.info(f"Search type: {search_type_name}")
        
        try:
            response_data = self.client.get(self.ENDPOINTS['listings_sale'], params=params)
            return self._validate_response(response_data)
        
        except HTTPClientError as e:
            logger.error(f"Failed to search sale listings with structured criteria: {e}")
            raise RentCastClientError(f"Structured sale listings search failed: {e}")
    
    def search_listings_rental_structured(self, search_criteria: 'SearchCriteria') -> Dict[str, Any]:
        """
        Search for long-term rental listings using structured search criteria.
        
        Args:
            search_criteria: Structured search criteria object
            
        Returns:
            Dict containing rental listings response
        """
        params = search_criteria.to_query_params()
        
        # Convert numeric values to strings for API
        params = {k: str(v) if isinstance(v, (int, float)) else v 
                 for k, v in params.items() if v is not None}
        
        logger.info(f"Structured rental listings search with params: {params}")
        search_type_name = getattr(search_criteria, 'search_type', 'Unknown')
        logger.info(f"Search type: {search_type_name}")
        
        try:
            response_data = self.client.get(self.ENDPOINTS['listings_rental_long_term'], params=params)
            return self._validate_response(response_data)
        
        except HTTPClientError as e:
            logger.error(f"Failed to search rental listings with structured criteria: {e}")
            raise RentCastClientError(f"Structured rental listings search failed: {e}")
    
    # Convenience methods for common search patterns
    
    def search_property_by_address(self, address: str, **kwargs) -> PropertiesResponse:
        """
        Search for a specific property by address.
        
        Args:
            address: Full property address (Street, City, State, Zip format recommended)
            **kwargs: Additional search criteria
            
        Returns:
            PropertiesResponse containing the property data
        """
        from ..core.search_queries import SpecificAddressSearch
        search_criteria = SpecificAddressSearch(address=address, **kwargs)
        return self.search_properties_structured(search_criteria)
    
    def search_properties_in_location(self, city: Optional[str] = None, state: Optional[str] = None,
                                    zip_code: Optional[str] = None, **kwargs) -> PropertiesResponse:
        """
        Search for properties in a specific location.
        
        Args:
            city: City name
            state: State abbreviation (2 characters)
            zip_code: ZIP code (5 digits)
            **kwargs: Additional search criteria
            
        Returns:
            PropertiesResponse containing matching properties
        """
        from ..core.search_queries import LocationSearch
        search_criteria = LocationSearch(city=city, state=state, zip_code=zip_code, **kwargs)
        return self.search_properties_structured(search_criteria)
    
    def search_properties_in_area(self, latitude: Optional[float] = None, longitude: Optional[float] = None,
                                center_address: Optional[str] = None, radius: float = 5.0,
                                **kwargs) -> PropertiesResponse:
        """
        Search for properties within a geographical area.
        
        Args:
            latitude: Center latitude (if not using center_address)
            longitude: Center longitude (if not using center_address)
            center_address: Center address (if not using lat/lng)
            radius: Search radius in miles
            **kwargs: Additional search criteria
            
        Returns:
            PropertiesResponse containing matching properties
        """
        from ..core.search_queries import GeographicalAreaSearch
        search_criteria = GeographicalAreaSearch(
            latitude=latitude, longitude=longitude, 
            center_address=center_address, radius=radius, **kwargs
        )
        return self.search_properties_structured(search_criteria)

    def search_properties(self, address: Optional[str] = None, city: Optional[str] = None,
                         state: Optional[str] = None, zip_code: Optional[str] = None,
                         property_type: Optional[str] = None, bedrooms: Optional[int] = None,
                         bathrooms: Optional[float] = None, min_rent: Optional[float] = None,
                         max_rent: Optional[float] = None, limit: int = 100, offset: int = 0,
                         **kwargs) -> PropertiesResponse:
        """
        Search for properties using RentCast API.
        
        Args:
            address: Specific address
            city: City name
            state: State abbreviation (e.g., 'TX', 'CA')
            zip_code: ZIP code
            property_type: Type of property (e.g., 'Single Family', 'Condo')
            bedrooms: Number of bedrooms
            bathrooms: Number of bathrooms
            min_rent: Minimum rent amount
            max_rent: Maximum rent amount
            limit: Maximum number of results (max 500)
            offset: Number of results to skip
            **kwargs: Additional query parameters
            
        Returns:
            PropertiesResponse containing property search results
        """
        params: Dict[str, Any] = {
            'limit': min(limit, 500),  # RentCast max limit
            'offset': offset
        }
        
        # Add location parameters
        if city:
            params['city'] = city
        if state:
            params['state'] = state
        if zip_code:
            params['zipCode'] = zip_code
        if address:
            params['address'] = address
        
        # Add property filters
        if property_type:
            params['propertyType'] = property_type
        if bedrooms is not None:
            params['bedrooms'] = bedrooms
        if bathrooms is not None:
            params['bathrooms'] = bathrooms
        if min_rent is not None:
            params['minRent'] = min_rent
        if max_rent is not None:
            params['maxRent'] = max_rent
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        logger.info(f"Searching properties with params: {params}")
        
        try:
            response_data = self.client.get(self.ENDPOINTS['properties'], params=params)
            validated_response = self._validate_response(response_data)
            return PropertiesResponse.from_dict(validated_response)
        
        except HTTPClientError as e:
            logger.error(f"Failed to search properties: {e}")
            raise RentCastClientError(f"Property search failed: {e}")
    
    def get_property_details(self, property_id: str) -> Property:
        """
        Get detailed information about a specific property.
        
        Args:
            property_id: Property ID
            
        Returns:
            Property containing property details
        """
        endpoint = self.ENDPOINTS['property_details'].format(id=property_id)
        
        logger.info(f"Fetching details for property: {property_id}")
        
        try:
            response_data = self.client.get(endpoint)
            validated_response = self._validate_response(response_data)
            return Property.from_dict(validated_response)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get property details for {property_id}: {e}")
            raise RentCastClientError(f"Property details fetch failed: {e}")
    
    def get_random_properties(self, **kwargs) -> PropertiesResponse:
        """
        Get random properties from the API.
        
        Args:
            **kwargs: Query parameters for filtering
            
        Returns:
            PropertiesResponse containing random properties
        """
        logger.info("Fetching random properties")
        
        try:
            response_data = self.client.get(self.ENDPOINTS['properties_random'], params=kwargs)
            validated_response = self._validate_response(response_data)
            return PropertiesResponse.from_dict(validated_response)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get random properties: {e}")
            raise RentCastClientError(f"Random properties fetch failed: {e}")

    def get_avm_value(self, address: Optional[str] = None, zipcode: Optional[str] = None,
                      city: Optional[str] = None, state: Optional[str] = None,
                      propertyType: Optional[str] = None, bedrooms: Optional[int] = None,
                      bathrooms: Optional[float] = None, squareFootage: Optional[int] = None,
                      **kwargs) -> Dict[str, Any]:
        """
        Get Automated Valuation Model (AVM) property value estimate.
        
        Args:
            address: Property address
            zipcode: Property ZIP code
            city: Property city
            state: Property state
            propertyType: Type of property
            bedrooms: Number of bedrooms
            bathrooms: Number of bathrooms
            squareFootage: Property square footage
            **kwargs: Additional query parameters
            
        Returns:
            Dict containing AVM value estimate
        """
        params: Dict[str, Union[str, int, float]] = {}
        
        # Add location parameters
        if address:
            params['address'] = address
        if zipcode:
            params['zipcode'] = zipcode
        if city:
            params['city'] = city
        if state:
            params['state'] = state
        
        # Add property characteristics
        if propertyType:
            params['propertyType'] = propertyType
        if bedrooms is not None:
            params['bedrooms'] = bedrooms
        if bathrooms is not None:
            params['bathrooms'] = bathrooms
        if squareFootage is not None:
            params['squareFootage'] = squareFootage
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        logger.info(f"Fetching AVM value with params: {params}")
        
        try:
            response_data = self.client.get(self.ENDPOINTS['avm_value'], params=params)
            return self._validate_response(response_data)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get AVM value: {e}")
            raise RentCastClientError(f"AVM value fetch failed: {e}")

    def get_avm_rent_long_term(self, address: Optional[str] = None, zipcode: Optional[str] = None,
                               city: Optional[str] = None, state: Optional[str] = None,
                               propertyType: Optional[str] = None, bedrooms: Optional[int] = None,
                               bathrooms: Optional[float] = None, squareFootage: Optional[int] = None,
                               **kwargs) -> Dict[str, Any]:
        """
        Get Automated Valuation Model (AVM) long-term rent estimate.
        
        Args:
            address: Property address
            zipcode: Property ZIP code
            city: Property city
            state: Property state
            propertyType: Type of property
            bedrooms: Number of bedrooms
            bathrooms: Number of bathrooms
            squareFootage: Property square footage
            **kwargs: Additional query parameters
            
        Returns:
            Dict containing AVM rent estimate
        """
        params: Dict[str, Union[str, int, float]] = {}
        
        # Add location parameters
        if address:
            params['address'] = address
        if zipcode:
            params['zipcode'] = zipcode
        if city:
            params['city'] = city
        if state:
            params['state'] = state
        
        # Add property characteristics
        if propertyType:
            params['propertyType'] = propertyType
        if bedrooms is not None:
            params['bedrooms'] = bedrooms
        if bathrooms is not None:
            params['bathrooms'] = bathrooms
        if squareFootage is not None:
            params['squareFootage'] = squareFootage
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        logger.info(f"Fetching AVM long-term rent with params: {params}")
        
        try:
            response_data = self.client.get(self.ENDPOINTS['avm_rent_long_term'], params=params)
            return self._validate_response(response_data)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get AVM rent estimate: {e}")
            raise RentCastClientError(f"AVM rent estimate fetch failed: {e}")

    def get_listings_sale(self, city: Optional[str] = None, state: Optional[str] = None,
                          zipcode: Optional[str] = None, address: Optional[str] = None,
                          propertyType: Optional[str] = None, bedrooms: Optional[int] = None,
                          bathrooms: Optional[float] = None, minPrice: Optional[int] = None,
                          maxPrice: Optional[int] = None, limit: int = 20, offset: int = 0,
                          **kwargs) -> PropertiesResponse:
        """
        Get properties for sale listings.
        
        Args:
            city: City name
            state: State abbreviation
            zipcode: ZIP code
            address: Specific address
            propertyType: Type of property
            bedrooms: Number of bedrooms
            bathrooms: Number of bathrooms
            minPrice: Minimum price
            maxPrice: Maximum price
            limit: Maximum number of results
            offset: Number of results to skip
            **kwargs: Additional query parameters
            
        Returns:
            PropertiesResponse containing sale listings
        """
        params: Dict[str, Union[str, int, float]] = {
            'limit': min(limit, 500),
            'offset': offset
        }
        
        # Add location parameters
        if city:
            params['city'] = city
        if state:
            params['state'] = state
        if zipcode:
            params['zipcode'] = zipcode
        if address:
            params['address'] = address
        
        # Add property filters
        if propertyType:
            params['propertyType'] = propertyType
        if bedrooms is not None:
            params['bedrooms'] = bedrooms
        if bathrooms is not None:
            params['bathrooms'] = bathrooms
        if minPrice is not None:
            params['minPrice'] = minPrice
        if maxPrice is not None:
            params['maxPrice'] = maxPrice
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        logger.info(f"Fetching sale listings with params: {params}")
        
        try:
            response_data = self.client.get(self.ENDPOINTS['listings_sale'], params=params)
            validated_response = self._validate_response(response_data)
            return PropertiesResponse.from_dict(validated_response)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get sale listings: {e}")
            raise RentCastClientError(f"Sale listings fetch failed: {e}")

    def get_listing_sale_details(self, listing_id: str) -> Property:
        """
        Get detailed information about a specific sale listing.
        
        Args:
            listing_id: Sale listing ID
            
        Returns:
            Property containing sale listing details
        """
        endpoint = self.ENDPOINTS['listings_sale_details'].format(id=listing_id)
        
        logger.info(f"Fetching details for sale listing: {listing_id}")
        
        try:
            response_data = self.client.get(endpoint)
            validated_response = self._validate_response(response_data)
            return Property.from_dict(validated_response)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get sale listing details for {listing_id}: {e}")
            raise RentCastClientError(f"Sale listing details fetch failed: {e}")

    def get_listings_rental_long_term(self, city: Optional[str] = None, state: Optional[str] = None,
                                      zipcode: Optional[str] = None, address: Optional[str] = None,
                                      propertyType: Optional[str] = None, bedrooms: Optional[int] = None,
                                      bathrooms: Optional[float] = None, minRent: Optional[int] = None,
                                      maxRent: Optional[int] = None, limit: int = 20, offset: int = 0,
                                      **kwargs) -> PropertiesResponse:
        """
        Get long-term rental listings.
        
        Args:
            city: City name
            state: State abbreviation
            zipcode: ZIP code
            address: Specific address
            propertyType: Type of property
            bedrooms: Number of bedrooms
            bathrooms: Number of bathrooms
            minRent: Minimum rent amount
            maxRent: Maximum rent amount
            limit: Maximum number of results
            offset: Number of results to skip
            **kwargs: Additional query parameters
            
        Returns:
            PropertiesResponse containing long-term rental listings
        """
        params: Dict[str, Union[str, int, float]] = {
            'limit': min(limit, 500),
            'offset': offset
        }
        
        # Add location parameters
        if city:
            params['city'] = city
        if state:
            params['state'] = state
        if zipcode:
            params['zipcode'] = zipcode
        if address:
            params['address'] = address
        
        # Add property filters
        if propertyType:
            params['propertyType'] = propertyType
        if bedrooms is not None:
            params['bedrooms'] = bedrooms
        if bathrooms is not None:
            params['bathrooms'] = bathrooms
        if minRent is not None:
            params['minRent'] = minRent
        if maxRent is not None:
            params['maxRent'] = maxRent
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        logger.info(f"Fetching long-term rental listings with params: {params}")
        
        try:
            response_data = self.client.get(self.ENDPOINTS['listings_rental_long_term'], params=params)
            validated_response = self._validate_response(response_data)
            return PropertiesResponse.from_dict(validated_response)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get long-term rental listings: {e}")
            raise RentCastClientError(f"Long-term rental listings fetch failed: {e}")

    def get_listing_rental_long_term_details(self, listing_id: str) -> Property:
        """
        Get detailed information about a specific long-term rental listing.
        
        Args:
            listing_id: Long-term rental listing ID
            
        Returns:
            Property containing long-term rental listing details
        """
        endpoint = self.ENDPOINTS['listings_rental_long_term_details'].format(id=listing_id)
        
        logger.info(f"Fetching details for long-term rental listing: {listing_id}")
        
        try:
            response_data = self.client.get(endpoint)
            validated_response = self._validate_response(response_data)
            return Property.from_dict(validated_response)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get long-term rental listing details for {listing_id}: {e}")
            raise RentCastClientError(f"Long-term rental listing details fetch failed: {e}")

    def get_markets(self, city: Optional[str] = None, state: Optional[str] = None,
                    zipcode: Optional[str] = None, limit: int = 50, **kwargs) -> Dict[str, Any]:
        """
        Get market data for specified locations.
        
        Args:
            city: City name
            state: State abbreviation
            zipcode: ZIP code
            limit: Maximum number of results
            **kwargs: Additional query parameters
            
        Returns:
            Dict containing market data
        """
        params: Dict[str, Union[str, int]] = {
            'limit': min(limit, 500)
        }
        
        # Add location parameters
        if city:
            params['city'] = city
        if state:
            params['state'] = state
        if zipcode:
            params['zipcode'] = zipcode
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        logger.info(f"Fetching market data with params: {params}")
        
        try:
            response_data = self.client.get(self.ENDPOINTS['markets'], params=params)
            return self._validate_response(response_data)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get market data: {e}")
            raise RentCastClientError(f"Market data fetch failed: {e}")
    
    def test_connection(self) -> bool:
        """
        Test the connection to RentCast API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Make a simple request with minimal parameters to test connection
            response = self.search_properties(limit=1)
            logger.info("RentCast API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"RentCast API connection test failed: {e}")
            return False
    
    def close(self) -> None:
        """Close the HTTP client connection."""
        if hasattr(self, 'client'):
            self.client.close()
            logger.info("RentCast client closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
