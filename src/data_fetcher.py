"""
Data Fetcher Module

This module handles fetching real estate data from various APIs and sources.
Supports multiple data sources including MLS, Zillow, Redfin, and custom APIs.
"""

import requests
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
import json

from rentcast_client import RentCastClient, RentCastClientError
from http_client import HTTPClientError

logger = logging.getLogger(__name__)


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
                                
                                # Process response data
                                property_data = response.get('properties', []) if isinstance(response, dict) else response
                                if isinstance(property_data, list):
                                    for prop in property_data:
                                        normalized_prop = self._normalize_rentcast_property(prop)
                                        properties.append(normalized_prop)
                                        
                            except RentCastClientError as e:
                                logger.error(f"RentCast search error for {location}, {prop_type}: {e}")
                                continue
                    else:
                        # Search without property type filter
                        try:
                            logger.info(f"Searching RentCast: {location}")
                            response = client.search_properties(**search_kwargs)
                            
                            # Process response data
                            property_data = response.get('properties', []) if isinstance(response, dict) else response
                            if isinstance(property_data, list):
                                for prop in property_data:
                                    normalized_prop = self._normalize_rentcast_property(prop)
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
