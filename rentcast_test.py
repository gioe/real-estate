#!/usr/bin/env python3
"""
RENTCAST Integration Test Script

This script tests the RENTCAST API integration without making actual API calls.
Use this to verify that your configuration is set up correctly.
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.config_manager import ConfigManager
from src.data_fetcher import RealEstateDataFetcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_rentcast_config():
    """Test RENTCAST configuration setup."""
    logger.info("Testing RENTCAST configuration...")
    
    # Initialize configuration
    config = ConfigManager()
    
    # Check if RENTCAST is configured
    api_config = config.get_api_config()
    
    logger.info("RENTCAST Configuration Status:")
    logger.info(f"  Enabled: {api_config.get('rentcast_enabled', False)}")
    logger.info(f"  API Key: {'✅ Set' if api_config.get('rentcast_api_key') else '❌ Not set'}")
    logger.info(f"  Endpoint: {api_config.get('rentcast_endpoint', 'Not configured')}")
    logger.info(f"  Rate Limit: {api_config.get('rentcast_rate_limit', 'Not set')}")
    
    # Check environment variable
    env_key = os.getenv('RENTCAST_API_KEY')
    logger.info(f"  Environment Variable: {'✅ Set' if env_key else '❌ Not set'}")
    
    # Check search parameters
    search_params = api_config.get('rentcast_search_params', {})
    if search_params:
        logger.info("  Search Parameters:")
        for key, value in search_params.items():
            logger.info(f"    {key}: {value}")
    
    return api_config.get('rentcast_enabled', False) and api_config.get('rentcast_api_key')


def test_data_fetcher_initialization():
    """Test data fetcher initialization with RENTCAST support."""
    logger.info("Testing Data Fetcher initialization...")
    
    config = ConfigManager()
    api_config = config.get_api_config()
    
    try:
        data_fetcher = RealEstateDataFetcher(api_config)
        logger.info("✅ Data Fetcher initialized successfully")
        
        # Test method availability
        if hasattr(data_fetcher, 'fetch_rentcast_data'):
            logger.info("✅ fetch_rentcast_data method available")
        else:
            logger.error("❌ fetch_rentcast_data method not found")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Data Fetcher initialization failed: {str(e)}")
        return False


def show_setup_instructions():
    """Show setup instructions for RENTCAST."""
    logger.info("\n" + "="*50)
    logger.info("RENTCAST SETUP INSTRUCTIONS")
    logger.info("="*50)
    
    logger.info("\n1. Get your RENTCAST API key:")
    logger.info("   - Visit: https://app.rentcast.io/")
    logger.info("   - Sign up for an account")
    logger.info("   - Get your API key from the dashboard")
    
    logger.info("\n2. Configure your API key:")
    logger.info("   - Edit the .env file in your project root")
    logger.info("   - Replace 'your_rentcast_api_key_here' with your actual key:")
    logger.info("     RENTCAST_API_KEY=your_actual_api_key_here")
    
    logger.info("\n3. Enable RENTCAST in configuration:")
    logger.info("   - Edit config/config.yaml")
    logger.info("   - Set: rentcast_enabled: true")
    
    logger.info("\n4. Test the configuration:")
    logger.info("   - Run: python rentcast_test.py")
    logger.info("   - Run: python main.py --mode fetch --verbose")


def main():
    logger.info("RENTCAST Integration Test")
    logger.info("=" * 30)
    
    # Test configuration
    config_ok = test_rentcast_config()
    
    # Test data fetcher
    fetcher_ok = test_data_fetcher_initialization()
    
    if config_ok and fetcher_ok:
        logger.info("\n✅ RENTCAST integration is ready!")
        logger.info("You can now run: python main.py --mode fetch")
    else:
        logger.info("\n❌ RENTCAST integration needs setup")
        show_setup_instructions()
    
    logger.info("\n" + "="*30)
    logger.info("Test completed!")


if __name__ == "__main__":
    main()
