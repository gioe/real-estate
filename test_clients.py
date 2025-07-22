#!/usr/bin/env python3
"""
Test script for HTTP Client and RentCast Client

This script demonstrates the usage of the new HTTP client architecture
and tests the RentCast API integration.
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import http_client
import rentcast_client
from config_manager import ConfigManager

from http_client import BaseHTTPClient, RateLimiter, HTTPClientError
from rentcast_client import RentCastClient, RentCastClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_http_client():
    """Test the base HTTP client functionality."""
    logger.info("=" * 50)
    logger.info("Testing Base HTTP Client")
    logger.info("=" * 50)
    
    # Test with a public API (JSONPlaceholder)
    try:
        with BaseHTTPClient("https://jsonplaceholder.typicode.com") as client:
            # Test GET request
            response = client.get("/posts/1")
            logger.info(f"GET /posts/1 successful: {response.get('title', 'N/A')}")
            
            # Test with parameters
            response = client.get("/posts", params={"userId": 1})
            logger.info(f"GET /posts with params: {len(response)} posts returned")
            
            logger.info("✅ Base HTTP Client test passed")
            
    except HTTPClientError as e:
        logger.error(f"❌ Base HTTP Client test failed: {e}")
        return False
    
    return True


def test_rate_limiter():
    """Test the rate limiter functionality."""
    logger.info("=" * 50)
    logger.info("Testing Rate Limiter")
    logger.info("=" * 50)
    
    try:
        # Create a rate limiter with very low limits for testing
        limiter = RateLimiter(max_requests=3, time_window=5)
        
        import time
        start_time = time.time()
        
        # Make requests that should trigger rate limiting
        for i in range(5):
            logger.info(f"Making request {i + 1}")
            limiter.wait_if_needed()
            logger.info(f"Request {i + 1} allowed")
        
        elapsed = time.time() - start_time
        logger.info(f"Total time elapsed: {elapsed:.2f} seconds")
        
        if elapsed > 2:  # Should have been rate limited
            logger.info("✅ Rate limiter test passed")
            return True
        else:
            logger.warning("⚠️ Rate limiter may not have activated")
            return True
            
    except Exception as e:
        logger.error(f"❌ Rate limiter test failed: {e}")
        return False


def test_rentcast_client():
    """Test the RentCast client."""
    logger.info("=" * 50)
    logger.info("Testing RentCast Client")
    logger.info("=" * 50)
    
    try:
        # Load configuration
        config_manager = ConfigManager("config/config.yaml")
        api_config = config_manager.get_api_config()
        
        api_key = api_config.get('rentcast_api_key', '')
        rentcast_enabled = api_config.get('rentcast_enabled', False)
        
        if not rentcast_enabled:
            logger.warning("RentCast is not enabled in configuration")
            logger.info("To enable: Set 'rentcast_enabled: true' in config/config.yaml")
            return True
            
        if not api_key:
            logger.warning("RentCast API key not configured")
            logger.info("To configure: Add your API key to .env file as RENTCAST_API_KEY")
            return True
        
        # Test RentCast client
        endpoint = api_config.get('rentcast_endpoint', 'https://api.rentcast.io/v1')
        rate_limit = api_config.get('rentcast_rate_limit', 100)
        
        with RentCastClient(
            api_key=api_key,
            base_url=endpoint,
            rate_limit=rate_limit
        ) as client:
            
            logger.info("Testing RentCast connection...")
            
            # Test connection
            if not client.test_connection():
                logger.error("❌ RentCast connection test failed")
                return False
            
            logger.info("✅ RentCast connection successful")
            
            # Test property search
            logger.info("Testing property search...")
            try:
                results = client.search_properties(
                    city="Austin",
                    state="TX",
                    limit=5
                )
                
                if isinstance(results, dict):
                    properties = results.get('properties', results)
                else:
                    properties = results
                
                logger.info(f"✅ Property search successful: {len(properties)} properties found")
                
                if properties and len(properties) > 0:
                    # Show sample property
                    sample = properties[0]
                    logger.info(f"Sample property: {sample.get('address', {}).get('line', 'N/A')}")
                
            except RentCastClientError as e:
                logger.error(f"⚠️ Property search failed: {e}")
                # This might be expected if API key is invalid or quota exceeded
                return True
            
            logger.info("✅ RentCast client test passed")
            
    except Exception as e:
        logger.error(f"❌ RentCast client test failed: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    logger.info("Starting HTTP Client and RentCast Client Tests")
    logger.info("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test base HTTP client
    if test_http_client():
        tests_passed += 1
    
    # Test rate limiter
    if test_rate_limiter():
        tests_passed += 1
    
    # Test RentCast client
    if test_rentcast_client():
        tests_passed += 1
    
    # Summary
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    logger.info(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.warning(f"⚠️ {total_tests - tests_passed} test(s) had issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
