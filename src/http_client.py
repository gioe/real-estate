"""
HTTP Client Module

Base HTTP client for making API requests with proper error handling, 
rate limiting, and retry logic.
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
    """Simple rate limiter to control API request frequency."""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        # Check if we need to wait
        if len(self.requests) >= self.max_requests:
            oldest_request = min(self.requests)
            wait_time = self.time_window - (now - oldest_request)
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
                self.requests = []  # Clear after waiting
        
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
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle HTTP response and extract data."""
        try:
            # Log response details
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Check for successful status codes
            if 200 <= response.status_code < 300:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    logger.warning("Response is not valid JSON, returning text")
                    return {"data": response.text}
            
            # Handle error responses
            error_data = None
            try:
                error_data = response.json()
            except json.JSONDecodeError:
                error_data = {"error": response.text}
            
            error_message = f"HTTP {response.status_code}: {error_data.get('message', 'Unknown error')}"
            raise HTTPClientError(error_message, response.status_code, error_data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            raise HTTPClientError(f"Request failed: {str(e)}")
    
    def _make_request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make HTTP request with retry logic."""
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
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make GET request."""
        url = self._build_url(endpoint)
        request_headers = self._prepare_headers(headers)
        
        response = self._make_request_with_retry(
            method='GET',
            url=url,
            params=params,
            headers=request_headers
        )
        
        return self._handle_response(response)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             json_data: Optional[Dict[str, Any]] = None, 
             headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
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
            **kwargs
        )
        
        return self._handle_response(response)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            json_data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
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
            **kwargs
        )
        
        return self._handle_response(response)
    
    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Make DELETE request."""
        url = self._build_url(endpoint)
        request_headers = self._prepare_headers(headers)
        
        response = self._make_request_with_retry(
            method='DELETE',
            url=url,
            headers=request_headers
        )
        
        return self._handle_response(response)
    
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
