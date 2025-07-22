"""
RentCast API Error Handling

Comprehensive error handling for RentCast API response codes based on RFC 9110 specification.
Provides specific exceptions for each response code type with detailed error information.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RentCastErrorResponse:
    """Represents a RentCast API error response."""
    status: int
    error: str
    message: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RentCastErrorResponse':
        """Parse error response from API data."""
        return cls(
            status=data.get('status', 0),
            error=data.get('error', 'unknown'),
            message=data.get('message', 'Unknown error occurred')
        )


class RentCastAPIError(Exception):
    """Base exception for RentCast API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 error_response: Optional[RentCastErrorResponse] = None):
        self.message = message
        self.status_code = status_code
        self.error_response = error_response
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.error_response:
            return f"RentCast API Error {self.status_code}: {self.error_response.message}"
        return f"RentCast API Error: {self.message}"


class RentCastSuccessResponse(RentCastAPIError):
    """200 - Success: Request completed successfully."""
    pass


class RentCastInvalidParametersError(RentCastAPIError):
    """400 - Invalid parameters: Request parameters were missing or improperly formatted."""
    
    def __init__(self, message: str = "Invalid request parameters", 
                 error_response: Optional[RentCastErrorResponse] = None):
        super().__init__(message, 400, error_response)
        logger.warning(f"Invalid parameters error: {message}")


class RentCastAuthError(RentCastAPIError):
    """401 - Auth or billing error: Authentication failed or billing issues."""
    
    def __init__(self, message: str = "Authentication or billing error", 
                 error_response: Optional[RentCastErrorResponse] = None):
        super().__init__(message, 401, error_response)
        logger.error(f"Authentication/billing error: {message}")


class RentCastNoResultsError(RentCastAPIError):
    """404 - No results: No data found matching query parameters."""
    
    def __init__(self, message: str = "No results found for query", 
                 error_response: Optional[RentCastErrorResponse] = None):
        super().__init__(message, 404, error_response)
        logger.info(f"No results found: {message}")


class RentCastMethodNotAllowedError(RentCastAPIError):
    """405 - Method not allowed: Endpoint doesn't support the HTTP method."""
    
    def __init__(self, message: str = "HTTP method not allowed for this endpoint", 
                 error_response: Optional[RentCastErrorResponse] = None):
        super().__init__(message, 405, error_response)
        logger.error(f"Method not allowed: {message}")


class RentCastRateLimitError(RentCastAPIError):
    """
    429 - Rate limit error: Too many requests, exceeded 20 requests per second.
    
    RentCast API has a hard limit of 20 requests per second per API key.
    Error format: {"status": 429, "error": "auth/rate-limit-exceeded", 
                   "message": "The rate limit of 20 requests per second has been exceeded"}
    """
    
    def __init__(self, message: str = "The rate limit of 20 requests per second has been exceeded", 
                 error_response: Optional[RentCastErrorResponse] = None):
        super().__init__(message, 429, error_response)
        logger.warning(f"RentCast rate limit exceeded: {message}")
        logger.info("Recommendation: Consider using separate API keys for different applications or implementing request throttling")


class RentCastServerError(RentCastAPIError):
    """500 - Server error: Internal server error occurred."""
    
    def __init__(self, message: str = "Internal server error", 
                 error_response: Optional[RentCastErrorResponse] = None):
        super().__init__(message, 500, error_response)
        logger.error(f"Server error: {message}")


class RentCastTimeoutError(RentCastAPIError):
    """504 - Timeout error: Server timed out processing the request."""
    
    def __init__(self, message: str = "Server timeout error", 
                 error_response: Optional[RentCastErrorResponse] = None):
        super().__init__(message, 504, error_response)
        logger.warning(f"Timeout error: {message}")


class RentCastUnknownError(RentCastAPIError):
    """Unknown error: Unexpected response code."""
    
    def __init__(self, message: str, status_code: int, 
                 error_response: Optional[RentCastErrorResponse] = None):
        super().__init__(message, status_code, error_response)
        logger.error(f"Unknown error (status {status_code}): {message}")


def create_rentcast_exception(status_code: int, response_data: Optional[Dict[str, Any]] = None) -> RentCastAPIError:
    """
    Create appropriate RentCast exception based on status code.
    
    Args:
        status_code: HTTP status code from response
        response_data: Optional response data containing error details
        
    Returns:
        Appropriate RentCast exception instance
    """
    # Parse error response if available
    error_response = None
    if response_data:
        try:
            error_response = RentCastErrorResponse.from_dict(response_data)
        except Exception as e:
            logger.warning(f"Failed to parse error response: {e}")
    
    # Extract message from error response or use default
    message = error_response.message if error_response else f"HTTP {status_code} error"
    
    # Map status codes to specific exceptions
    error_map = {
        200: RentCastSuccessResponse,
        400: RentCastInvalidParametersError,
        401: RentCastAuthError,
        404: RentCastNoResultsError,
        405: RentCastMethodNotAllowedError,
        429: RentCastRateLimitError,
        500: RentCastServerError,
        504: RentCastTimeoutError,
    }
    
    exception_class = error_map.get(status_code, RentCastUnknownError)
    
    if status_code in error_map:
        return exception_class(message, error_response)
    else:
        return RentCastUnknownError(message, status_code, error_response)


def is_retryable_error(exception: RentCastAPIError) -> bool:
    """
    Determine if an error is retryable.
    
    Args:
        exception: RentCast API exception
        
    Returns:
        True if the error should be retried
    """
    # Retryable errors: rate limit, server error, timeout
    retryable_types = (
        RentCastRateLimitError,
        RentCastServerError,
        RentCastTimeoutError
    )
    
    return isinstance(exception, retryable_types)


def get_retry_delay(exception: RentCastAPIError, attempt: int) -> float:
    """
    Get appropriate retry delay based on error type and attempt number.
    
    Args:
        exception: RentCast API exception
        attempt: Current retry attempt number (0-based)
        
    Returns:
        Delay in seconds before retrying
    """
    if isinstance(exception, RentCastRateLimitError):
        # For rate limit errors, use longer delays
        return min(60.0, 5.0 * (2 ** attempt))  # Max 60 seconds
    elif isinstance(exception, RentCastTimeoutError):
        # For timeout errors, use moderate delays
        return min(30.0, 2.0 * (2 ** attempt))  # Max 30 seconds
    elif isinstance(exception, RentCastServerError):
        # For server errors, use exponential backoff
        return min(20.0, 1.0 * (2 ** attempt))  # Max 20 seconds
    else:
        # Default exponential backoff
        return min(10.0, 1.0 * (2 ** attempt))  # Max 10 seconds


def log_error_details(exception: RentCastAPIError) -> None:
    """
    Log detailed error information for debugging.
    
    Args:
        exception: RentCast API exception to log
    """
    error_details = {
        'error_type': type(exception).__name__,
        'status_code': exception.status_code,
        'message': exception.message,
    }
    
    if exception.error_response:
        error_details.update({
            'api_error_code': exception.error_response.error,
            'api_message': exception.error_response.message,
        })
    
    logger.error(f"RentCast API Error Details: {error_details}")


# Error handling recommendations for different error types
ERROR_HANDLING_RECOMMENDATIONS = {
    400: "Check request parameters and format. Ensure all required fields are provided.",
    401: "Verify API key is valid and active subscription exists. Check billing status.",
    404: "Modify query parameters to broaden search criteria. Check if location exists.",
    405: "Use GET method only. RentCast API endpoints only support GET requests.",
    429: "RentCast hard limit: 20 requests per second per API key. Use separate API keys for different applications and implement request throttling.",
    500: "Retry request. If persistent, contact RentCast support.",
    504: "Retry with different parameters or smaller result set. Reduce query complexity."
}


def get_error_recommendation(status_code: int) -> str:
    """
    Get error handling recommendation for a specific status code.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        Recommendation string for handling the error
    """
    return ERROR_HANDLING_RECOMMENDATIONS.get(
        status_code, 
        "Check RentCast API documentation for error details."
    )
