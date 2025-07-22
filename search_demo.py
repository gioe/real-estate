#!/usr/bin/env python3
"""
Search Query Demo

This demo shows how to use the new structured search functionality
to query the RentCast API in different ways.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from typing import List, Dict, Any

from src.config.config_manager import ConfigManager
from src.core.data_fetcher import RealEstateDataFetcher
from src.core.search_queries import (
    SearchQueryBuilder, SearchType, PropertyType,
    SpecificAddressSearch, LocationSearch, GeographicalAreaSearch,
    search_by_address, search_by_location, search_by_coordinates, search_around_address
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_specific_address_search(fetcher: RealEstateDataFetcher):
    """Demonstrate searching for a specific address."""
    print("\n" + "="*60)
    print("DEMO 1: Specific Address Search")
    print("="*60)
    
    # Example 1: Using convenience function
    print("\n--- Using convenience function ---")
    address = "5500 Grand Lake Dr, San Antonio, TX, 78244"
    properties = fetcher.search_by_address(address)
    print(f"Found {len(properties)} properties for address: {address}")
    
    if properties:
        prop = properties[0]
        print(f"Property: {prop.get('address', 'Unknown Address')}")
        print(f"Type: {prop.get('propertyType', 'Unknown')}")
        print(f"Bedrooms: {prop.get('bedrooms', 'N/A')}")
        print(f"Bathrooms: {prop.get('bathrooms', 'N/A')}")
    
    # Example 2: Using search criteria class directly
    print("\n--- Using search criteria class ---")
    search_criteria = SpecificAddressSearch(address=address)
    properties = fetcher.search_properties_structured(search_criteria)
    print(f"Found {len(properties)} properties using SpecificAddressSearch")


def demo_location_search(fetcher: RealEstateDataFetcher):
    """Demonstrate searching by city, state, zip code."""
    print("\n" + "="*60)
    print("DEMO 2: Location-Based Search")
    print("="*60)
    
    # Example 1: Search by city and state
    print("\n--- Search by city and state ---")
    properties = fetcher.search_by_location(
        city="Austin", 
        state="TX", 
        bedrooms=3, 
        bathrooms=2, 
        limit=10
    )
    print(f"Found {len(properties)} 3BR/2BA properties in Austin, TX")
    
    # Example 2: Search by zip code with filters
    print("\n--- Search by zip code with filters ---")
    search_criteria = LocationSearch(
        zip_code="78744",
        property_type=PropertyType.SINGLE_FAMILY.value,
        min_bedrooms=2,
        max_bedrooms=4,
        min_price=200000,
        max_price=500000,
        limit=15
    )
    properties = fetcher.search_properties_structured(search_criteria)
    print(f"Found {len(properties)} single family homes in 78744")
    
    # Show some results
    for i, prop in enumerate(properties[:3]):
        print(f"  Property {i+1}: {prop.get('address', 'Unknown Address')}")
        print(f"    Price: ${prop.get('price', 'N/A'):,}")
        print(f"    Bedrooms: {prop.get('bedrooms', 'N/A')}")
        print(f"    Type: {prop.get('propertyType', 'Unknown')}")


def demo_geographical_search(fetcher: RealEstateDataFetcher):
    """Demonstrate geographical area searches."""
    print("\n" + "="*60)
    print("DEMO 3: Geographical Area Search")
    print("="*60)
    
    # Example 1: Search by coordinates
    print("\n--- Search by coordinates (downtown Phoenix) ---")
    properties = fetcher.search_by_coordinates(
        latitude=33.45141,
        longitude=-112.073827,
        radius=5,
        bedrooms=3,
        bathrooms=2,
        limit=10
    )
    print(f"Found {len(properties)} 3BR/2BA properties within 5 miles of downtown Phoenix")
    
    # Example 2: Search around an address
    print("\n--- Search around an address ---")
    center_address = "1600 Amphitheatre Parkway, Mountain View, CA"
    properties = fetcher.search_around_address(
        address=center_address,
        radius=3,
        property_type=PropertyType.CONDO.value,
        min_price=800000,
        limit=5
    )
    print(f"Found {len(properties)} condos within 3 miles of Google headquarters")
    
    # Example 3: Using search criteria class with custom radius
    print("\n--- Using GeographicalAreaSearch class ---")
    search_criteria = GeographicalAreaSearch(
        center_address="Space Needle, Seattle, WA",
        radius=2,
        min_square_feet=1000,
        max_square_feet=3000,
        min_year_built=2000,
        limit=8
    )
    properties = fetcher.search_properties_structured(search_criteria)
    print(f"Found {len(properties)} properties near Space Needle")


def demo_search_builder(fetcher: RealEstateDataFetcher):
    """Demonstrate using the search query builder."""
    print("\n" + "="*60)
    print("DEMO 4: Search Query Builder")
    print("="*60)
    
    # Example 1: Build a complex city search
    print("\n--- Building complex city search ---")
    builder = fetcher.create_search_builder()
    search_criteria = (builder
                      .in_city_state("Denver", "CO")
                      .with_property_type(PropertyType.SINGLE_FAMILY)
                      .with_bedrooms_range(min_bedrooms=3, max_bedrooms=5)
                      .with_bathrooms_range(min_bathrooms=2)
                      .with_price_range(min_price=400000, max_price=800000)
                      .with_square_feet_range(min_square_feet=1500, max_square_feet=4000)
                      .with_year_built_range(min_year=1990)
                      .with_limit(12)
                      .build())
    
    properties = fetcher.search_properties_structured(search_criteria)
    print(f"Found {len(properties)} properties matching complex criteria in Denver, CO")
    print(f"Search type: {search_criteria.search_type}")
    
    # Example 2: Build a geographical search
    print("\n--- Building geographical search with builder ---")
    builder = fetcher.create_search_builder()
    search_criteria = (builder
                      .around_address("Times Square, New York, NY", 1)
                      .with_property_type(PropertyType.CONDO)
                      .with_bedrooms(2)
                      .with_bathrooms_range(min_bathrooms=1, max_bathrooms=3)
                      .with_price_range(min_price=500000)
                      .with_limit(5)
                      .build())
    
    properties = fetcher.search_properties_structured(search_criteria)
    print(f"Found {len(properties)} 2BR condos within 1 mile of Times Square")
    print(f"Search type: {search_criteria.search_type}")


def demo_listing_searches(fetcher: RealEstateDataFetcher):
    """Demonstrate searching for listings (for sale and rental)."""
    print("\n" + "="*60)
    print("DEMO 5: Listing Searches")
    print("="*60)
    
    # Example 1: Sale listings in a city
    print("\n--- Sale listings in Miami ---")
    search_criteria = LocationSearch(
        city="Miami",
        state="FL",
        min_price=300000,
        max_price=1000000,
        limit=8
    )
    
    sale_listings = fetcher.search_listings_structured(search_criteria, listing_type='sale')
    print(f"Found {len(sale_listings)} sale listings in Miami, FL")
    
    # Example 2: Rental listings around an area
    print("\n--- Rental listings around downtown Austin ---")
    search_criteria = GeographicalAreaSearch(
        center_address="Austin, TX",
        radius=10,
        bedrooms=2,
        min_price=1500,  # Monthly rent
        max_price=3000,
        limit=6
    )
    
    rental_listings = fetcher.search_listings_structured(search_criteria, listing_type='rental')
    print(f"Found {len(rental_listings)} rental listings around Austin")


def demo_error_handling():
    """Demonstrate error handling in search queries."""
    print("\n" + "="*60)
    print("DEMO 6: Error Handling")
    print("="*60)
    
    # Example 1: Invalid state abbreviation
    print("\n--- Invalid state abbreviation ---")
    try:
        search_criteria = LocationSearch(city="Boston", state="Massachusetts")  # Should be MA
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    # Example 2: Invalid zip code
    print("\n--- Invalid zip code ---")
    try:
        search_criteria = LocationSearch(zip_code="1234")  # Should be 5 digits
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    # Example 3: Invalid coordinates
    print("\n--- Invalid coordinates ---")
    try:
        search_criteria = GeographicalAreaSearch(latitude=100, longitude=200, radius=5)
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    # Example 4: Missing search parameters
    print("\n--- Missing search parameters ---")
    try:
        search_criteria = LocationSearch()  # No city, state, or zip
    except ValueError as e:
        print(f"Caught expected error: {e}")


def main():
    """Main demo function."""
    print("Real Estate Search Query Demo")
    print("="*60)
    
    try:
        # Load configuration
        config_manager = ConfigManager()
        api_config = config_manager.get_api_config()
        
        if not api_config.get('rentcast_api_key'):
            print("Warning: RentCast API key not configured. Some searches may not return results.")
            print("Please set RENTCAST_API_KEY in your environment or config file.")
        
        # Initialize data fetcher
        fetcher = RealEstateDataFetcher(api_config)
        
        # Run demos
        demo_specific_address_search(fetcher)
        demo_location_search(fetcher)
        demo_geographical_search(fetcher)
        demo_search_builder(fetcher)
        demo_listing_searches(fetcher)
        demo_error_handling()
        
        print("\n" + "="*60)
        print("Demo completed successfully!")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\nDemo failed with error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
