"""
Real Estate Analyzer Source Package

This package contains all the core functionality for the real estate data analyzer,
organized into logical subdirectories for better maintainability.

Package Structure:
- api/: HTTP clients and API communication
- core/: Core business logic (analysis, data fetching, database)
- config/: Configuration management
- notifications/: Alert and notification system
- schemas/: Data schemas and models
- visualization/: Chart and graph generation
"""

# Import main classes for convenience
from .api import (
    RentCastClient, BaseHTTPClient, HTTPClientError,
    RentCastAPIError, RentCastInvalidParametersError, RentCastAuthError,
    RentCastNoResultsError, RentCastRateLimitError, RentCastServerError,
    RentCastTimeoutError, get_error_recommendation
)
from .core import (
    RealEstateAnalyzer, RealEstateDataFetcher, DatabaseManager,
    PaginationManager, APIResponse, PaginationParams, PaginatedResult
)
from .search import (
    SearchCriteria, SearchType, PropertyType,
    SpecificAddressSearch, LocationSearch, GeographicalAreaSearch,
    SearchQueryBuilder, search_by_address, search_by_location,
    search_by_coordinates, search_around_address
)
from .config import ConfigManager
from .schemas import Property, PropertiesResponse, PropertyListing, ListingsResponse
from .visualization import GraphGenerator

__version__ = "1.0.0"

__all__ = [
    # API classes
    'RentCastClient',
    'BaseHTTPClient', 
    'HTTPClientError',
    
    # RentCast Error Handling
    'RentCastAPIError',
    'RentCastInvalidParametersError',
    'RentCastAuthError',
    'RentCastNoResultsError',
    'RentCastRateLimitError',
    'RentCastServerError',
    'RentCastTimeoutError',
    'get_error_recommendation',
    
    # Core classes
    'RealEstateAnalyzer',
    'RealEstateDataFetcher',
    'DatabaseManager',
    
    # Pagination classes
    'PaginationManager',
    'APIResponse',
    'PaginationParams',
    'PaginatedResult',
    
    # Search query classes
    'SearchQueryBuilder',
    'SearchCriteria',
    'SearchType',
    'PropertyType',
    'SpecificAddressSearch',
    'LocationSearch',
    'GeographicalAreaSearch',
    
    # Search convenience functions
    'search_by_address',
    'search_by_location',
    'search_by_coordinates',
    'search_around_address',
    
    # Configuration
    'ConfigManager',
    
    # Main schemas
    'Property',
    'PropertiesResponse', 
    'PropertyListing',
    'ListingsResponse',
    
    # Visualization
    'GraphGenerator'
]
