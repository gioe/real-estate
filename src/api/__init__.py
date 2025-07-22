"""
API Module

This package contains HTTP clients and API communication components.
"""

from .http_client import BaseHTTPClient, HTTPClientError, RateLimiter
from .rentcast_client import RentCastClient, RentCastClientError
from .rentcast_errors import (
    RentCastAPIError,
    RentCastInvalidParametersError,
    RentCastAuthError,
    RentCastNoResultsError,
    RentCastMethodNotAllowedError,
    RentCastRateLimitError,
    RentCastServerError,
    RentCastTimeoutError,
    RentCastUnknownError,
    create_rentcast_exception,
    is_retryable_error,
    get_error_recommendation
)

__all__ = [
    'BaseHTTPClient',
    'HTTPClientError', 
    'RateLimiter',
    'RentCastClient',
    'RentCastClientError',
    'RentCastAPIError',
    'RentCastInvalidParametersError',
    'RentCastAuthError',
    'RentCastNoResultsError',
    'RentCastMethodNotAllowedError',
    'RentCastRateLimitError',
    'RentCastServerError',
    'RentCastTimeoutError',
    'RentCastUnknownError',
    'create_rentcast_exception',
    'is_retryable_error',
    'get_error_recommendation'
]
