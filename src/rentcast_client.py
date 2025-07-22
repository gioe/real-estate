"""
RentCast API Client

Specialized client for interacting with RentCast API endpoints.
Handles authentication, request formatting, and response parsing.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json

from http_client import BaseHTTPClient, RateLimiter, HTTPClientError

logger = logging.getLogger(__name__)


class RentCastClientError(HTTPClientError):
    """Custom exception for RentCast API errors."""
    pass


class RentCastClient:
    """Client for interacting with RentCast API."""
    
    # API endpoint mappings
    ENDPOINTS = {
        'properties': '/properties',
        'property_details': '/properties/{property_id}',
        'rental_estimates': '/rentals/properties/{property_id}',
        'market_data': '/markets/{market_id}',
        'comparables': '/properties/{property_id}/comparables',
        'neighborhoods': '/neighborhoods',
        'property_history': '/properties/{property_id}/history',
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
    
    def search_properties(self, city: Optional[str] = None, state: Optional[str] = None,
                         zip_code: Optional[str] = None, address: Optional[str] = None,
                         property_type: Optional[str] = None, bedrooms: Optional[int] = None,
                         bathrooms: Optional[float] = None, min_rent: Optional[int] = None,
                         max_rent: Optional[int] = None, limit: int = 20, 
                         offset: int = 0, **kwargs) -> Dict[str, Any]:
        """
        Search for properties using RentCast API.
        
        Args:
            city: City name
            state: State abbreviation (e.g., 'TX', 'CA')
            zip_code: ZIP code
            address: Specific address
            property_type: Type of property (e.g., 'Single Family', 'Condo')
            bedrooms: Number of bedrooms
            bathrooms: Number of bathrooms
            min_rent: Minimum rent amount
            max_rent: Maximum rent amount
            limit: Maximum number of results (max 500)
            offset: Number of results to skip
            **kwargs: Additional query parameters
            
        Returns:
            Dict containing property search results
        """
        params: Dict[str, Union[str, int, float]] = {
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
            return self._validate_response(response_data)
        
        except HTTPClientError as e:
            logger.error(f"Failed to search properties: {e}")
            raise RentCastClientError(f"Property search failed: {e}")
    
    def get_property_details(self, property_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific property.
        
        Args:
            property_id: RentCast property ID
            
        Returns:
            Dict containing property details
        """
        endpoint = self.ENDPOINTS['property_details'].format(property_id=property_id)
        
        logger.info(f"Fetching details for property: {property_id}")
        
        try:
            response_data = self.client.get(endpoint)
            return self._validate_response(response_data)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get property details for {property_id}: {e}")
            raise RentCastClientError(f"Property details fetch failed: {e}")
    
    def get_rental_estimate(self, property_id: str) -> Dict[str, Any]:
        """
        Get rental estimate for a property.
        
        Args:
            property_id: RentCast property ID
            
        Returns:
            Dict containing rental estimate data
        """
        endpoint = self.ENDPOINTS['rental_estimates'].format(property_id=property_id)
        
        logger.info(f"Fetching rental estimate for property: {property_id}")
        
        try:
            response_data = self.client.get(endpoint)
            return self._validate_response(response_data)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get rental estimate for {property_id}: {e}")
            raise RentCastClientError(f"Rental estimate fetch failed: {e}")
    
    def get_comparables(self, property_id: str, property_type: Optional[str] = None,
                       bedrooms: Optional[int] = None, bathrooms: Optional[float] = None,
                       radius: float = 1.0, limit: int = 10) -> Dict[str, Any]:
        """
        Get comparable properties for a given property.
        
        Args:
            property_id: RentCast property ID
            property_type: Filter by property type
            bedrooms: Filter by number of bedrooms
            bathrooms: Filter by number of bathrooms
            radius: Search radius in miles
            limit: Maximum number of comparables
            
        Returns:
            Dict containing comparable properties
        """
        endpoint = self.ENDPOINTS['comparables'].format(property_id=property_id)
        
        params: Dict[str, Union[str, int, float]] = {
            'radius': radius,
            'limit': min(limit, 100)  # Reasonable limit for comparables
        }
        
        if property_type:
            params['propertyType'] = property_type
        if bedrooms is not None:
            params['bedrooms'] = bedrooms
        if bathrooms is not None:
            params['bathrooms'] = bathrooms
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        logger.info(f"Fetching comparables for property {property_id} with params: {params}")
        
        try:
            response_data = self.client.get(endpoint, params=params)
            return self._validate_response(response_data)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get comparables for {property_id}: {e}")
            raise RentCastClientError(f"Comparables fetch failed: {e}")
    
    def get_neighborhoods(self, city: Optional[str] = None, state: Optional[str] = None,
                         zip_code: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Get neighborhood information for a location.
        
        Args:
            city: City name
            state: State abbreviation
            zip_code: ZIP code
            limit: Maximum number of neighborhoods
            
        Returns:
            Dict containing neighborhood data
        """
        params: Dict[str, Union[str, int]] = {
            'limit': min(limit, 100)
        }
        
        if city:
            params['city'] = city
        if state:
            params['state'] = state
        if zip_code:
            params['zipCode'] = zip_code
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        logger.info(f"Fetching neighborhoods with params: {params}")
        
        try:
            response_data = self.client.get(self.ENDPOINTS['neighborhoods'], params=params)
            return self._validate_response(response_data)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get neighborhoods: {e}")
            raise RentCastClientError(f"Neighborhoods fetch failed: {e}")
    
    def get_property_history(self, property_id: str) -> Dict[str, Any]:
        """
        Get historical data for a property.
        
        Args:
            property_id: RentCast property ID
            
        Returns:
            Dict containing property history
        """
        endpoint = self.ENDPOINTS['property_history'].format(property_id=property_id)
        
        logger.info(f"Fetching history for property: {property_id}")
        
        try:
            response_data = self.client.get(endpoint)
            return self._validate_response(response_data)
        
        except HTTPClientError as e:
            logger.error(f"Failed to get property history for {property_id}: {e}")
            raise RentCastClientError(f"Property history fetch failed: {e}")
    
    def test_connection(self) -> bool:
        """
        Test the connection to RentCast API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Make a simple request with minimal parameters
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
