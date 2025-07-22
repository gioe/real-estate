"""
Search Query Builder Module

This module provides classes and utilities for building search queries
for the RentCast API endpoints that support different search patterns.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class SearchType(Enum):
    """Types of searches supported by the API."""
    SPECIFIC_ADDRESS = "specific_address"
    CITY_STATE_ZIP = "city_state_zip"
    GEOGRAPHICAL_AREA = "geographical_area"


class PropertyType(Enum):
    """Property type filters for searches."""
    SINGLE_FAMILY = "Single Family"
    CONDO = "Condo"
    TOWNHOUSE = "Townhouse"
    MULTI_FAMILY = "Multi Family"
    APARTMENT = "Apartment"
    MOBILE_HOME = "Mobile Home"
    MANUFACTURED = "Manufactured"
    LAND = "Land"
    COMMERCIAL = "Commercial"
    OTHER = "Other"


@dataclass
class SearchCriteria:
    """Base class for search criteria."""
    
    # Property characteristics filters
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[float] = None
    max_bathrooms: Optional[float] = None
    min_square_feet: Optional[int] = None
    max_square_feet: Optional[int] = None
    min_lot_size: Optional[int] = None
    max_lot_size: Optional[int] = None
    min_year_built: Optional[int] = None
    max_year_built: Optional[int] = None
    
    # Price filters
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    
    # Listing filters (for listing endpoints)
    min_days_on_market: Optional[int] = None
    max_days_on_market: Optional[int] = None
    listing_type: Optional[str] = None
    
    # Pagination
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    def to_query_params(self) -> Dict[str, Any]:
        """Convert search criteria to API query parameters."""
        params = {}
        
        # Property characteristics
        if self.property_type:
            params['propertyType'] = self.property_type
        if self.bedrooms is not None:
            params['bedrooms'] = self.bedrooms
        if self.bathrooms is not None:
            params['bathrooms'] = self.bathrooms
        if self.min_bedrooms is not None:
            params['minBedrooms'] = self.min_bedrooms
        if self.max_bedrooms is not None:
            params['maxBedrooms'] = self.max_bedrooms
        if self.min_bathrooms is not None:
            params['minBathrooms'] = self.min_bathrooms
        if self.max_bathrooms is not None:
            params['maxBathrooms'] = self.max_bathrooms
        if self.min_square_feet is not None:
            params['minSquareFootage'] = self.min_square_feet
        if self.max_square_feet is not None:
            params['maxSquareFootage'] = self.max_square_feet
        if self.min_lot_size is not None:
            params['minLotSize'] = self.min_lot_size
        if self.max_lot_size is not None:
            params['maxLotSize'] = self.max_lot_size
        if self.min_year_built is not None:
            params['minYearBuilt'] = self.min_year_built
        if self.max_year_built is not None:
            params['maxYearBuilt'] = self.max_year_built
        
        # Price filters
        if self.min_price is not None:
            params['minPrice'] = self.min_price
        if self.max_price is not None:
            params['maxPrice'] = self.max_price
        
        # Listing filters
        if self.min_days_on_market is not None:
            params['minDaysOnMarket'] = self.min_days_on_market
        if self.max_days_on_market is not None:
            params['maxDaysOnMarket'] = self.max_days_on_market
        if self.listing_type:
            params['listingType'] = self.listing_type
        
        # Pagination
        if self.limit is not None:
            params['limit'] = self.limit
        if self.offset is not None:
            params['offset'] = self.offset
        
        return params


@dataclass
class SpecificAddressSearch(SearchCriteria):
    """Search for a specific property address."""
    
    address: str = ""
    search_type: SearchType = field(default=SearchType.SPECIFIC_ADDRESS, init=False)
    
    def __post_init__(self):
        """Validate the address format."""
        if not self.address:
            raise ValueError("Address is required for specific address search")
        
        # Validate address format (Street, City, State, Zip)
        if not self._is_valid_address_format(self.address):
            logger.warning(f"Address may not be in optimal format: {self.address}")
            logger.warning("Recommended format: 'Street, City, State, Zip'")
    
    def _is_valid_address_format(self, address: str) -> bool:
        """Check if address is in the recommended format."""
        # Basic check for comma-separated components
        parts = [part.strip() for part in address.split(',')]
        return len(parts) >= 3  # At least Street, City, State
    
    def to_query_params(self) -> Dict[str, Any]:
        """Convert to API query parameters."""
        params = {'address': self.address}
        
        # For specific address searches, typically don't include other filters
        # as we want data for that specific property
        
        # Add pagination if specified
        if self.limit is not None:
            params['limit'] = self.limit
        if self.offset is not None:
            params['offset'] = self.offset
        
        return params


@dataclass
class LocationSearch(SearchCriteria):
    """Search by city, state, and/or zip code."""
    
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    search_type: SearchType = field(default=SearchType.CITY_STATE_ZIP, init=False)
    
    def __post_init__(self):
        """Validate location parameters."""
        if not any([self.city, self.state, self.zip_code]):
            raise ValueError("At least one of city, state, or zip_code is required")
        
        # Validate state format (2-character abbreviation)
        if self.state and (len(self.state) != 2 or not self.state.isalpha()):
            raise ValueError("State must be a 2-character abbreviation (e.g., 'TX', 'CA')")
        
        # Validate zip code format (5 digits)
        if self.zip_code and not re.match(r'^\d{5}$', self.zip_code):
            raise ValueError("Zip code must be a 5-digit number")
    
    def to_query_params(self) -> Dict[str, Any]:
        """Convert to API query parameters."""
        params = super().to_query_params()
        
        if self.city:
            params['city'] = self.city
        if self.state:
            params['state'] = self.state.upper()
        if self.zip_code:
            params['zipCode'] = self.zip_code
        
        return params


@dataclass
class GeographicalAreaSearch(SearchCriteria):
    """Search within a geographical area (radius search)."""
    
    # Center of search area
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    center_address: Optional[str] = None
    
    # Search radius in miles
    radius: float = 5.0
    
    search_type: SearchType = field(default=SearchType.GEOGRAPHICAL_AREA, init=False)
    
    def __post_init__(self):
        """Validate geographical search parameters."""
        # Must have either lat/lng or center address
        has_coordinates = self.latitude is not None and self.longitude is not None
        has_address = self.center_address is not None
        
        if not (has_coordinates or has_address):
            raise ValueError("Must provide either latitude/longitude or center_address")
        
        if has_coordinates and has_address:
            logger.warning("Both coordinates and address provided. Address will take precedence.")
        
        # Validate coordinates
        if self.latitude is not None:
            if not -90 <= self.latitude <= 90:
                raise ValueError("Latitude must be between -90 and 90")
        
        if self.longitude is not None:
            if not -180 <= self.longitude <= 180:
                raise ValueError("Longitude must be between -180 and 180")
        
        # Validate radius
        if self.radius <= 0:
            raise ValueError("Radius must be greater than 0")
        if self.radius > 50:
            logger.warning(f"Large search radius ({self.radius} miles) may return many results")
    
    def to_query_params(self) -> Dict[str, Any]:
        """Convert to API query parameters."""
        params = super().to_query_params()
        
        # Use address as center if provided, otherwise use coordinates
        if self.center_address:
            params['address'] = self.center_address
        elif self.latitude is not None and self.longitude is not None:
            params['latitude'] = self.latitude
            params['longitude'] = self.longitude
        
        params['radius'] = self.radius
        
        return params


class SearchQueryBuilder:
    """Builder class for constructing search queries."""
    
    def __init__(self):
        """Initialize the query builder."""
        self.reset()
    
    def reset(self):
        """Reset the builder to start a new query."""
        self._search_type = None
        self._criteria = {}
        return self
    
    # Specific address search
    def for_address(self, address: str) -> 'SearchQueryBuilder':
        """Search for a specific address."""
        self._search_type = SearchType.SPECIFIC_ADDRESS
        self._criteria['address'] = address
        return self
    
    # Location-based search
    def in_city(self, city: str) -> 'SearchQueryBuilder':
        """Search within a city."""
        self._search_type = SearchType.CITY_STATE_ZIP
        self._criteria['city'] = city
        return self
    
    def in_state(self, state: str) -> 'SearchQueryBuilder':
        """Search within a state."""
        if self._search_type != SearchType.CITY_STATE_ZIP:
            self._search_type = SearchType.CITY_STATE_ZIP
        self._criteria['state'] = state
        return self
    
    def in_zip_code(self, zip_code: str) -> 'SearchQueryBuilder':
        """Search within a zip code."""
        if self._search_type != SearchType.CITY_STATE_ZIP:
            self._search_type = SearchType.CITY_STATE_ZIP
        self._criteria['zip_code'] = zip_code
        return self
    
    def in_city_state(self, city: str, state: str) -> 'SearchQueryBuilder':
        """Search within a city and state."""
        self._search_type = SearchType.CITY_STATE_ZIP
        self._criteria.update({'city': city, 'state': state})
        return self
    
    # Geographical area search
    def within_radius(self, latitude: float, longitude: float, radius: float) -> 'SearchQueryBuilder':
        """Search within a radius of coordinates."""
        self._search_type = SearchType.GEOGRAPHICAL_AREA
        self._criteria.update({
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius
        })
        return self
    
    def around_address(self, address: str, radius: float) -> 'SearchQueryBuilder':
        """Search within a radius of an address."""
        self._search_type = SearchType.GEOGRAPHICAL_AREA
        self._criteria.update({
            'center_address': address,
            'radius': radius
        })
        return self
    
    # Property filters
    def with_property_type(self, property_type: Union[str, PropertyType]) -> 'SearchQueryBuilder':
        """Filter by property type."""
        if isinstance(property_type, PropertyType):
            property_type = property_type.value
        self._criteria['property_type'] = property_type
        return self
    
    def with_bedrooms(self, bedrooms: int) -> 'SearchQueryBuilder':
        """Filter by exact number of bedrooms."""
        self._criteria['bedrooms'] = bedrooms
        return self
    
    def with_bedrooms_range(self, min_bedrooms: Optional[int] = None, 
                           max_bedrooms: Optional[int] = None) -> 'SearchQueryBuilder':
        """Filter by bedroom range."""
        if min_bedrooms is not None:
            self._criteria['min_bedrooms'] = min_bedrooms
        if max_bedrooms is not None:
            self._criteria['max_bedrooms'] = max_bedrooms
        return self
    
    def with_bathrooms(self, bathrooms: float) -> 'SearchQueryBuilder':
        """Filter by exact number of bathrooms."""
        self._criteria['bathrooms'] = bathrooms
        return self
    
    def with_bathrooms_range(self, min_bathrooms: Optional[float] = None,
                            max_bathrooms: Optional[float] = None) -> 'SearchQueryBuilder':
        """Filter by bathroom range."""
        if min_bathrooms is not None:
            self._criteria['min_bathrooms'] = min_bathrooms
        if max_bathrooms is not None:
            self._criteria['max_bathrooms'] = max_bathrooms
        return self
    
    def with_price_range(self, min_price: Optional[float] = None,
                        max_price: Optional[float] = None) -> 'SearchQueryBuilder':
        """Filter by price range."""
        if min_price is not None:
            self._criteria['min_price'] = min_price
        if max_price is not None:
            self._criteria['max_price'] = max_price
        return self
    
    def with_square_feet_range(self, min_square_feet: Optional[int] = None,
                              max_square_feet: Optional[int] = None) -> 'SearchQueryBuilder':
        """Filter by square footage range."""
        if min_square_feet is not None:
            self._criteria['min_square_feet'] = min_square_feet
        if max_square_feet is not None:
            self._criteria['max_square_feet'] = max_square_feet
        return self
    
    def with_year_built_range(self, min_year: Optional[int] = None,
                             max_year: Optional[int] = None) -> 'SearchQueryBuilder':
        """Filter by year built range."""
        if min_year is not None:
            self._criteria['min_year_built'] = min_year
        if max_year is not None:
            self._criteria['max_year_built'] = max_year
        return self
    
    # Pagination
    def with_limit(self, limit: int) -> 'SearchQueryBuilder':
        """Set result limit (1-500)."""
        if not 1 <= limit <= 500:
            raise ValueError("Limit must be between 1 and 500")
        self._criteria['limit'] = limit
        return self
    
    def with_offset(self, offset: int) -> 'SearchQueryBuilder':
        """Set result offset."""
        if offset < 0:
            raise ValueError("Offset must be non-negative")
        self._criteria['offset'] = offset
        return self
    
    def build(self) -> Union[SpecificAddressSearch, LocationSearch, GeographicalAreaSearch]:
        """Build the search criteria object."""
        if self._search_type is None:
            raise ValueError("Search type not specified. Use for_address(), in_city(), or within_radius() first.")
        
        try:
            if self._search_type == SearchType.SPECIFIC_ADDRESS:
                return SpecificAddressSearch(**self._criteria)
            elif self._search_type == SearchType.CITY_STATE_ZIP:
                return LocationSearch(**self._criteria)
            elif self._search_type == SearchType.GEOGRAPHICAL_AREA:
                return GeographicalAreaSearch(**self._criteria)
            else:
                raise ValueError(f"Unknown search type: {self._search_type}")
        except TypeError as e:
            raise ValueError(f"Invalid criteria for search type {self._search_type}: {e}")


# Convenience functions for common searches

def search_by_address(address: str, **kwargs) -> SpecificAddressSearch:
    """Create a specific address search."""
    return SpecificAddressSearch(address=address, **kwargs)


def search_by_location(city: Optional[str] = None, state: Optional[str] = None,
                      zip_code: Optional[str] = None, **kwargs) -> LocationSearch:
    """Create a location-based search."""
    return LocationSearch(city=city, state=state, zip_code=zip_code, **kwargs)


def search_by_coordinates(latitude: float, longitude: float, radius: float = 5.0,
                         **kwargs) -> GeographicalAreaSearch:
    """Create a coordinate-based geographical search."""
    return GeographicalAreaSearch(latitude=latitude, longitude=longitude, 
                                 radius=radius, **kwargs)


def search_around_address(address: str, radius: float = 5.0, 
                         **kwargs) -> GeographicalAreaSearch:
    """Create an address-based geographical search."""
    return GeographicalAreaSearch(center_address=address, radius=radius, **kwargs)
