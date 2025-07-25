"""
Search Module

This package contains search query builders and criteria classes
that can be used by API clients without creating circular dependencies.
"""

from .search_queries import (
    SearchCriteria, SearchType, PropertyType,
    SpecificAddressSearch, LocationSearch, GeographicalAreaSearch,
    SearchQueryBuilder, search_by_address, search_by_location,
    search_by_coordinates, search_around_address
)

__all__ = [
    # Search query classes
    'SearchCriteria',
    'SearchType',
    'PropertyType',
    'SpecificAddressSearch',
    'LocationSearch', 
    'GeographicalAreaSearch',
    'SearchQueryBuilder',
    
    # Search convenience functions
    'search_by_address',
    'search_by_location',
    'search_by_coordinates',
    'search_around_address'
]
