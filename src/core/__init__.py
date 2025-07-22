"""
Core Module

This package contains the core business logic for the real estate analyzer,
including data analysis, fetching, database operations, and structured search queries.
"""

from .data_analyzer import RealEstateAnalyzer
from .data_fetcher import RealEstateDataFetcher, PaginationManager, APIResponse
from .database import DatabaseManager, PaginationParams, PaginatedResult
from .search_queries import (
    SearchCriteria, SearchType, PropertyType,
    SpecificAddressSearch, LocationSearch, GeographicalAreaSearch,
    SearchQueryBuilder, search_by_address, search_by_location,
    search_by_coordinates, search_around_address
)

__all__ = [
    # Core classes
    'RealEstateAnalyzer',
    'RealEstateDataFetcher',
    'PaginationManager',
    'APIResponse',
    'DatabaseManager',
    'PaginationParams', 
    'PaginatedResult',
    
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
