#!/usr/bin/env python3
"""
Pagination Example

This script demonstrates how to use the pagination functionality
for fetching large datasets from the RentCast API.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.data_fetcher import RealEstateDataFetcher
from src.core.database import DatabaseManager, PaginationParams as DBPaginationParams
from src.config.config_manager import ConfigManager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_api_pagination():
    """Demonstrate API pagination with RentCast."""
    logger.info("=== API Pagination Demo ===")
    
    # Load configuration
    config_manager = ConfigManager('config/config.yaml')
    config = config_manager.config
    
    # Initialize data fetcher
    data_fetcher = RealEstateDataFetcher(config.get('api', {}))
    
    # Example 1: Fetch properties page by page
    search_params = {
        'city': 'Austin',
        'state': 'TX',
        'limit': 20  # Fetch 20 properties per page
    }
    
    logger.info("Fetching properties page by page...")
    page_count = 0
    total_properties = 0
    
    for page_response in data_fetcher.fetch_properties_paginated(
        search_params=search_params,
        max_pages=3  # Limit to 3 pages for demo
    ):
        page_count += 1
        page_size = len(page_response.data)
        total_properties += page_size
        
        logger.info(f"Page {page_count}: Got {page_size} properties")
        logger.info(f"  Total count: {page_response.total_count}")
        logger.info(f"  Has more: {page_response.has_more}")
        logger.info(f"  Next offset: {page_response.next_offset}")
        
        # Show sample property info
        if page_response.data:
            sample_prop = page_response.data[0]
            logger.info(f"  Sample property: {sample_prop.get('formatted_address', 'N/A')}")
    
    logger.info(f"API pagination complete. Total pages: {page_count}, Total properties: {total_properties}")


def demo_database_pagination():
    """Demonstrate database pagination."""
    logger.info("=== Database Pagination Demo ===")
    
    # Load configuration
    config_manager = ConfigManager('config/config.yaml')
    config = config_manager.config
    
    # Initialize database
    db_manager = DatabaseManager(config.get('database', {}))
    
    # Example: Paginated database query
    pagination = DBPaginationParams(limit=25, offset=0)
    
    # Search criteria
    criteria = {
        'price': {'min': 200000, 'max': 800000},
        'bedrooms': {'min': 2},
        'cities': {'in': ['Austin', 'Houston', 'Dallas']}
    }
    
    logger.info("Fetching properties from database with pagination...")
    page_num = 1
    
    while True:
        result = db_manager.get_properties_paginated(pagination, criteria)
        
        logger.info(f"Page {page_num}: Got {len(result.data)} properties")
        logger.info(f"  Total in database: {result.total_count}")
        logger.info(f"  Current offset: {result.offset}")
        logger.info(f"  Has more: {result.has_more}")
        
        if result.data:
            # Show sample property info
            sample_prop = result.data[0]
            logger.info(f"  Sample property: {sample_prop.get('address', 'N/A')} - ${sample_prop.get('price', 0):,.0f}")
        
        if not result.has_more or page_num >= 3:  # Limit to 3 pages for demo
            break
        
        # Move to next page
        pagination.offset = result.next_offset or (pagination.offset + pagination.limit)
        page_num += 1
    
    logger.info("Database pagination demo complete.")


def demo_combined_workflow():
    """Demonstrate combined API + Database pagination workflow."""
    logger.info("=== Combined Pagination Workflow ===")
    
    # Load configuration
    config_manager = ConfigManager('config/config.yaml')
    config = config_manager.config
    
    # Initialize components
    data_fetcher = RealEstateDataFetcher(config.get('api', {}))
    db_manager = DatabaseManager(config.get('database', {}))
    
    # Step 1: Fetch data from API with pagination
    search_params = {
        'city': 'San Antonio',
        'state': 'TX',
        'limit': 50
    }
    
    logger.info("Step 1: Fetching fresh data from API...")
    all_properties = data_fetcher.fetch_all_properties_paginated(
        search_params=search_params,
        max_pages=2  # Limit for demo
    )
    
    logger.info(f"Fetched {len(all_properties)} properties from API")
    
    # Step 2: Save to database
    if all_properties:
        logger.info("Step 2: Saving to database...")
        saved_count = db_manager.save_properties(all_properties)
        logger.info(f"Saved {saved_count} properties to database")
    
    # Step 3: Query database with pagination
    logger.info("Step 3: Querying database with pagination...")
    pagination = DBPaginationParams(limit=20, offset=0)
    
    recent_properties = db_manager.get_recent_properties_paginated(
        days=1,  # Properties from last day
        pagination=pagination
    )
    
    logger.info(f"Found {len(recent_properties.data)} recent properties in database")
    logger.info(f"Total recent properties: {recent_properties.total_count}")
    
    logger.info("Combined workflow complete!")


def main():
    """Run pagination demonstrations."""
    try:
        demo_api_pagination()
        print("\n" + "="*60 + "\n")
        
        demo_database_pagination()
        print("\n" + "="*60 + "\n")
        
        demo_combined_workflow()
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")


if __name__ == "__main__":
    main()
