"""
HTTP Client Module

Base HTTP client for making API requests with proper error handling, 
rate limiting, and retry logic. Includes RentCast-specific error handling.
"""

import requests
import time
import logging
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin, urlencode
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class HTTPClientError(Exception):
    """Custom exception for HTTP client errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class RateLimiter:
    """
    Rate limiter specifically designed for RentCast API's 20 requests per second limit.
    
    RentCast enforces a hard limit of 20 requests per second per API key.
    This rate limiter ensures compliance with that limit.
    """
    
    def __init__(self, max_requests: int = 20, time_window: int = 1):
        """
        Initialize rate limiter for RentCast API.
        
        Args:
            max_requests: Maximum number of requests allowed (default: 20 for RentCast)
            time_window: Time window in seconds (default: 1 second for RentCast)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        
        # Log configuration
        logger.info(f"Rate limiter configured: {max_requests} requests per {time_window} second(s)")
    
    def wait_if_needed(self) -> None:
        """
        Wait if rate limit would be exceeded.
        
        RentCast API has a hard limit of 20 requests per second.
        This method ensures we don't exceed that limit.
        """
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        # Check if we need to wait
        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = self.time_window - (now - oldest_request)
            if wait_time > 0:
                logger.info(f"Rate limit reached ({len(self.requests)}/{self.max_requests} requests), waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
                # Clear requests after waiting to start fresh
                self.requests = []
        
        # Record this request
        self.requests.append(now)


class BaseHTTPClient:
    """Base HTTP client with common functionality."""
    
    def __init__(self, base_url: str, default_headers: Optional[Dict[str, str]] = None,
                 timeout: int = 30, max_retries: int = 3, rate_limiter: Optional[RateLimiter] = None):
        """
        Initialize HTTP client.
        
        Args:
            base_url: Base URL for API endpoints
            default_headers: Default headers to include in all requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            rate_limiter: Optional rate limiter instance
        """
        self.base_url = base_url.rstrip('/')
        self.default_headers = default_headers or {}
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limiter = rate_limiter
        self.session = requests.Session()
        
        # Set default headers on session
        self.session.headers.update(self.default_headers)
        
        logger.info(f"HTTP Client initialized for {self.base_url}")
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        endpoint = endpoint.lstrip('/')
        return urljoin(f"{self.base_url}/", endpoint)
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Prepare headers for request."""
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        return request_headers
    
    def _handle_response(self, response: requests.Response, use_rentcast_errors: bool = False) -> Dict[str, Any]:
        """
        Handle HTTP response and extract data.
        
        Args:
            response: HTTP response object
            use_rentcast_errors: Whether to use RentCast-specific error handling
            
        Returns:
            Response data as dictionary
            
        Raises:
            HTTPClientError: For general HTTP errors
            RentCastAPIError: For RentCast-specific errors (if use_rentcast_errors=True)
        """
        try:
            # Log response details
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Parse response body
            response_data = None
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                logger.warning("Response is not valid JSON")
                response_data = {"data": response.text}
            
            # Check for successful status codes
            if 200 <= response.status_code < 300:
                return response_data
            
            # Handle error responses with RentCast-specific errors if requested
            if use_rentcast_errors:
                try:
                    from .rentcast_errors import create_rentcast_exception
                    raise create_rentcast_exception(response.status_code, response_data)
                except ImportError:
                    logger.warning("RentCast error handling not available, falling back to generic errors")
            
            # Generic error handling
            error_message = self._extract_error_message(response.status_code, response_data)
            raise HTTPClientError(error_message, response.status_code, response_data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            raise HTTPClientError(f"Request failed: {str(e)}")
    
    def _extract_error_message(self, status_code: int, response_data: Optional[Dict[str, Any]]) -> str:
        """Extract error message from response data."""
        if not response_data:
            return f"HTTP {status_code}: Unknown error"
        
        # Try different common error message fields
        for field in ['message', 'error', 'detail', 'error_description']:
            if field in response_data:
                error_value = response_data[field]
                if isinstance(error_value, str):
                    return f"HTTP {status_code}: {error_value}"
                elif isinstance(error_value, dict) and 'message' in error_value:
                    return f"HTTP {status_code}: {error_value['message']}"
        
        return f"HTTP {status_code}: {response_data.get('error', 'Unknown error')}"
    
    def _make_request_with_retry(self, method: str, url: str, use_rentcast_errors: bool = False, **kwargs) -> requests.Response:
        """
        Make HTTP request with retry logic and RentCast-specific error handling.
        
        Args:
            method: HTTP method
            url: Request URL
            use_rentcast_errors: Whether to use RentCast-specific error handling
            **kwargs: Additional request parameters
            
        Returns:
            HTTP response object
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if self.rate_limiter:
                    self.rate_limiter.wait_if_needed()
                
                logger.debug(f"Attempt {attempt + 1}: {method.upper()} {url}")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # For non-2xx responses, check if we should retry based on status code
                if not (200 <= response.status_code < 300):
                    should_retry = self._should_retry_status_code(response.status_code, use_rentcast_errors)
                    
                    if should_retry and attempt < self.max_retries:
                        wait_time = self._get_retry_delay(response.status_code, attempt, use_rentcast_errors)
                        logger.warning(f"HTTP {response.status_code} received (attempt {attempt + 1}), retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {self.max_retries + 1} attempts: {str(e)}")
        
        raise HTTPClientError(f"Request failed after retries: {str(last_exception)}")
    
    def _should_retry_status_code(self, status_code: int, use_rentcast_errors: bool) -> bool:
        """Determine if a status code should be retried."""
        # Always retry 5xx server errors
        if 500 <= status_code < 600:
            return True
        
        # For RentCast, retry specific error codes
        if use_rentcast_errors:
            # Retry rate limit (429), server error (500), and timeout (504) errors
            return status_code in [429, 500, 504]
        
        # Generic retry logic for server errors only
        return 500 <= status_code < 600
    
    def _get_retry_delay(self, status_code: int, attempt: int, use_rentcast_errors: bool) -> float:
        """Get retry delay based on status code and attempt."""
        if use_rentcast_errors:
            try:
                from .rentcast_errors import create_rentcast_exception, get_retry_delay
                temp_exception = create_rentcast_exception(status_code)
                return get_retry_delay(temp_exception, attempt)
            except ImportError:
                pass
        
        # Default exponential backoff
        if status_code == 429:  # Rate limit
            return min(60.0, 5.0 * (2 ** attempt))
        else:
            return min(30.0, 2.0 * (2 ** attempt))
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None, use_rentcast_errors: bool = False) -> Dict[str, Any]:
        """Make GET request."""
        url = self._build_url(endpoint)
        request_headers = self._prepare_headers(headers)
        
        response = self._make_request_with_retry(
            method='GET',
            url=url,
            params=params,
            headers=request_headers,
            use_rentcast_errors=use_rentcast_errors
        )
        
        return self._handle_response(response, use_rentcast_errors)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             json_data: Optional[Dict[str, Any]] = None, 
             headers: Optional[Dict[str, str]] = None, use_rentcast_errors: bool = False) -> Dict[str, Any]:
        """Make POST request."""
        url = self._build_url(endpoint)
        request_headers = self._prepare_headers(headers)
        
        kwargs = {}
        if json_data:
            kwargs['json'] = json_data
        elif data:
            kwargs['data'] = data
        
        response = self._make_request_with_retry(
            method='POST',
            url=url,
            headers=request_headers,
            use_rentcast_errors=use_rentcast_errors,
            **kwargs
        )
        
        return self._handle_response(response, use_rentcast_errors)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None, use_rentcast_errors: bool = False) -> Dict[str, Any]:
        """Make PUT request."""
        url = self._build_url(endpoint)
        request_headers = self._prepare_headers(headers)
        
        kwargs = {}
        if json_data:
            kwargs['json'] = json_data
        elif data:
            kwargs['data'] = data
        
        response = self._make_request_with_retry(
            method='PUT',
            url=url,
            headers=request_headers,
            use_rentcast_errors=use_rentcast_errors,
            **kwargs
        )
        
        return self._handle_response(response, use_rentcast_errors)
    
    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None, 
               use_rentcast_errors: bool = False) -> Dict[str, Any]:
        """Make DELETE request."""
        url = self._build_url(endpoint)
        request_headers = self._prepare_headers(headers)
        
        response = self._make_request_with_retry(
            method='DELETE',
            url=url,
            headers=request_headers,
            use_rentcast_errors=use_rentcast_errors
        )
        
        return self._handle_response(response, use_rentcast_errors)
    
    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
        logger.info("HTTP Client session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
