#!/usr/bin/env python3
"""
Quick Demo Script - Test Individual Components

This script allows you to test individual components of the real estate analyzer.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config_manager import ConfigManager
from src.database import DatabaseManager
from src.data_analyzer import RealEstateAnalyzer
from src.notification_system import NotificationManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_config():
    """Test configuration loading."""
    logger.info("Testing configuration...")
    
    config = ConfigManager()
    
    # Display key config sections
    logger.info("API Configuration:")
    api_config = config.get_api_config()
    for api, settings in api_config.items():
        enabled = settings.get('enabled', False) if isinstance(settings, dict) else settings
        logger.info(f"  {api}: {'✅ enabled' if enabled else '❌ disabled'}")
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        logger.warning("Configuration validation errors:")
        for error in errors:
            logger.warning(f"  - {error}")
    else:
        logger.info("✅ Configuration is valid")


def test_database():
    """Test database operations."""
    logger.info("Testing database...")
    
    config = ConfigManager()
    db = DatabaseManager(config.get_database_config())
    
    stats = db.get_database_stats()
    logger.info("Database Statistics:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    # Test a simple query
    recent_properties = db.get_recent_properties(days=7)
    logger.info(f"Recent properties (last 7 days): {len(recent_properties)}")


def test_analysis():
    """Test analysis functionality."""
    logger.info("Testing analysis...")
    
    config = ConfigManager()
    db = DatabaseManager(config.get_database_config())
    analyzer = RealEstateAnalyzer(db)
    
    # Test property matching
    criteria = config.get_search_criteria()
    matching = analyzer.find_matching_properties(criteria)
    logger.info(f"Properties matching criteria: {len(matching)}")
    
    if matching:
        sample_prop = matching[0]
        logger.info(f"Sample match: {sample_prop.get('address', 'N/A')} - ${sample_prop.get('price', 0):,.0f}")


def test_notifications():
    """Test notification system (without sending)."""
    logger.info("Testing notification system...")
    
    config = ConfigManager()
    notification_manager = NotificationManager(config.get_notification_config())
    
    # Test with fake properties
    sample_properties = [
        {
            'address': '123 Test St',
            'city': 'San Francisco',
            'price': 650000,
            'bedrooms': 2,
            'bathrooms': 2,
            'url': 'https://example.com/test'
        }
    ]
    
    # This won't actually send notifications due to disabled config
    logger.info("Notification channels configured:")
    enabled_channels = config.get('notifications.enabled_channels', [])
    for channel in enabled_channels:
        logger.info(f"  {channel}: configured")
    
    logger.info("Note: To test actual notifications, configure credentials in .env file")


def run_full_demo():
    """Run a full demonstration."""
    logger.info("Running full demo...")
    
    # Test all components
    test_config()
    test_database()
    test_analysis()
    test_notifications()
    
    logger.info("✅ Full demo completed!")


def main():
    parser = argparse.ArgumentParser(description='Real Estate Analyzer Demo')
    parser.add_argument('--test', choices=['config', 'database', 'analysis', 'notifications', 'all'],
                       default='all', help='Which component to test')
    
    args = parser.parse_args()
    
    try:
        if args.test == 'config':
            test_config()
        elif args.test == 'database':
            test_database()
        elif args.test == 'analysis':
            test_analysis()
        elif args.test == 'notifications':
            test_notifications()
        else:
            run_full_demo()
            
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
