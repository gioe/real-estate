#!/usr/bin/env python3
"""
RentCast Endpoints Test Script

This script demonstrates all the RentCast API endpoints that are now supported.
It provides examples of how to use each endpoint and what parameters they accept.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, Any

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.config_manager import ConfigManager
from src.api.rentcast_client import RentCastClient, RentCastClientError
from src.schemas.rentcast_schemas import Property, PropertiesResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demonstrate_properties_endpoints(client: RentCastClient) -> None:
    """Demonstrate /properties endpoints."""
    logger.info("\n" + "="*50)
    logger.info("PROPERTIES ENDPOINTS")
    logger.info("="*50)
    
    try:
        # /properties - Search for properties
        logger.info("\n1. GET /properties - Search properties")
        logger.info("   Parameters: city, state, zipcode, propertyType, bedrooms, bathrooms, etc.")
        response = client.search_properties(
            state="TX", 
            city="Austin", 
            propertyType="Single Family",
            bedrooms=3,
            limit=5
        )
        logger.info(f"   ✅ Found {len(response.properties)} properties")
        if response.properties:
            logger.info(f"   First property: {response.properties[0].formatted_address}")
        
        # /properties/random - Get random properties
        logger.info("\n2. GET /properties/random - Get random properties")
        logger.info("   Parameters: various filters available")
        response = client.get_random_properties(limit=3)
        logger.info(f"   ✅ Found {len(response.properties)} random properties")
        
        # /properties/{id} - Get specific property details
        logger.info("\n3. GET /properties/{id} - Get property details")
        logger.info("   Parameters: property ID in URL path")
        logger.info("   ⚠️  Requires valid property ID - skipping demo")
        # response = client.get_property_details("sample-property-id")
        
    except RentCastClientError as e:
        logger.error(f"Properties endpoint error: {e}")


def demonstrate_avm_endpoints(client: RentCastClient) -> None:
    """Demonstrate /avm endpoints."""
    logger.info("\n" + "="*50)
    logger.info("AVM (AUTOMATED VALUATION MODEL) ENDPOINTS")
    logger.info("="*50)
    
    try:
        # /avm/value - Get property value estimate
        logger.info("\n1. GET /avm/value - Get property value estimate")
        logger.info("   Parameters: address, zipcode, city, state, propertyType, bedrooms, bathrooms, squareFootage")
        response = client.get_avm_value(
            address="1234 Main St",
            city="Austin",
            state="TX",
            propertyType="Single Family",
            bedrooms=3,
            bathrooms=2,
            squareFootage=1800
        )
        logger.info(f"   ✅ AVM response received - property value estimated")
        
        # /avm/rent/long-term - Get rent estimate
        logger.info("\n2. GET /avm/rent/long-term - Get long-term rent estimate")
        logger.info("   Parameters: address, zipcode, city, state, propertyType, bedrooms, bathrooms, squareFootage")
        response = client.get_avm_rent_long_term(
            address="1234 Main St",
            city="Austin", 
            state="TX",
            propertyType="Single Family",
            bedrooms=3,
            bathrooms=2,
            squareFootage=1800
        )
        logger.info(f"   ✅ AVM rent response received - rent estimate calculated")
        
    except RentCastClientError as e:
        logger.error(f"AVM endpoint error: {e}")


def demonstrate_listings_endpoints(client: RentCastClient) -> None:
    """Demonstrate /listings endpoints."""
    logger.info("\n" + "="*50)
    logger.info("LISTINGS ENDPOINTS")
    logger.info("="*50)
    
    try:
        # /listings/sale - Get sale listings
        logger.info("\n1. GET /listings/sale - Get properties for sale")
        logger.info("   Parameters: city, state, zipcode, propertyType, bedrooms, bathrooms, minPrice, maxPrice, etc.")
        response = client.get_listings_sale(
            state="TX",
            city="Austin",
            propertyType="Single Family",
            bedrooms=3,
            minPrice=300000,
            maxPrice=600000,
            limit=5
        )
        logger.info(f"   ✅ Found {len(response.properties)} sale listings")
        
        # /listings/sale/{id} - Get specific sale listing details
        logger.info("\n2. GET /listings/sale/{id} - Get sale listing details")
        logger.info("   Parameters: listing ID in URL path")
        logger.info("   ⚠️  Requires valid listing ID - skipping demo")
        # response = client.get_listing_sale_details("sample-listing-id")
        
        # /listings/rental/long-term - Get rental listings
        logger.info("\n3. GET /listings/rental/long-term - Get long-term rental listings")
        logger.info("   Parameters: city, state, zipcode, propertyType, bedrooms, bathrooms, minRent, maxRent, etc.")
        response = client.get_listings_rental_long_term(
            state="TX",
            city="Austin",
            propertyType="Single Family",
            bedrooms=3,
            minRent=2000,
            maxRent=4000,
            limit=5
        )
        logger.info(f"   ✅ Found {len(response.properties)} rental listings")
        
        # /listings/rental/long-term/{id} - Get specific rental listing details
        logger.info("\n4. GET /listings/rental/long-term/{id} - Get rental listing details")
        logger.info("   Parameters: listing ID in URL path")
        logger.info("   ⚠️  Requires valid listing ID - skipping demo")
        # response = client.get_listing_rental_long_term_details("sample-listing-id")
        
    except RentCastClientError as e:
        logger.error(f"Listings endpoint error: {e}")


def demonstrate_markets_endpoints(client: RentCastClient) -> None:
    """Demonstrate /markets endpoints."""
    logger.info("\n" + "="*50)
    logger.info("MARKETS ENDPOINTS")
    logger.info("="*50)
    
    try:
        # /markets - Get market data
        logger.info("\n1. GET /markets - Get market data")
        logger.info("   Parameters: city, state, zipcode, limit")
        response = client.get_markets(
            state="TX",
            city="Austin",
            limit=10
        )
        logger.info(f"   ✅ Market data retrieved successfully")
        
    except RentCastClientError as e:
        logger.error(f"Markets endpoint error: {e}")


def show_endpoint_summary() -> None:
    """Show a summary of all available endpoints."""
    logger.info("\n" + "="*70)
    logger.info("RENTCAST API ENDPOINTS SUMMARY")
    logger.info("="*70)
    
    endpoints_info = [
        ("GET /properties", "Search for properties", "city, state, zipcode, propertyType, bedrooms, etc."),
        ("GET /properties/random", "Get random properties", "various filters"),
        ("GET /properties/{id}", "Get specific property details", "property ID in path"),
        ("GET /avm/value", "Get property value estimate", "address, city, state, propertyType, etc."),
        ("GET /avm/rent/long-term", "Get rent estimate", "address, city, state, propertyType, etc."),
        ("GET /listings/sale", "Get sale listings", "city, state, minPrice, maxPrice, etc."),
        ("GET /listings/sale/{id}", "Get sale listing details", "listing ID in path"),
        ("GET /listings/rental/long-term", "Get rental listings", "city, state, minRent, maxRent, etc."),
        ("GET /listings/rental/long-term/{id}", "Get rental listing details", "listing ID in path"),
        ("GET /markets", "Get market data", "city, state, zipcode, limit"),
    ]
    
    for endpoint, description, params in endpoints_info:
        logger.info(f"\n{endpoint}")
        logger.info(f"  Description: {description}")
        logger.info(f"  Parameters:  {params}")


def main():
    """Main function to demonstrate all endpoints."""
    logger.info("RentCast API Endpoints Demonstration")
    logger.info("=" * 50)
    
    # Initialize configuration and client
    try:
        config = ConfigManager()
        api_config = config.get_api_config()
        
        # Check if RentCast is configured
        if not api_config.get('rentcast_enabled'):
            logger.error("❌ RentCast is not enabled in configuration")
            logger.info("Please set 'rentcast_enabled: true' in config/config.yaml")
            return
        
        if not api_config.get('rentcast_api_key'):
            logger.error("❌ RentCast API key is not configured")
            logger.info("Please set your API key in the .env file or configuration")
            return
        
        # Create RentCast client
        client = RentCastClient(
            api_key=api_config['rentcast_api_key'],
            base_url=api_config.get('rentcast_endpoint', 'https://api.rentcast.io/v1'),
            rate_limit=api_config.get('rentcast_rate_limit', 100)
        )
        
        # Test connection first
        logger.info("Testing API connection...")
        if not client.test_connection():
            logger.error("❌ Failed to connect to RentCast API")
            return
        logger.info("✅ API connection successful")
        
        # Show endpoint summary
        show_endpoint_summary()
        
        # Demonstrate each group of endpoints
        # Note: Some demos may fail if you don't have the right API plan or if data doesn't exist
        demonstrate_properties_endpoints(client)
        demonstrate_avm_endpoints(client)
        demonstrate_listings_endpoints(client)
        demonstrate_markets_endpoints(client)
        
        logger.info("\n" + "="*70)
        logger.info("ENDPOINT DEMONSTRATION COMPLETE")
        logger.info("="*70)
        logger.info("✅ All endpoint methods are now available in RentCastClient")
        logger.info("💡 Ready for schema definition and implementation!")
        
    except Exception as e:
        logger.error(f"❌ Demonstration failed: {e}")
        logger.exception("Full error details:")
    
    finally:
        if 'client' in locals():
            client.close()


if __name__ == "__main__":
    main()
