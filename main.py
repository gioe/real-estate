#!/usr/bin/env python3
"""
Real Estate Data Analyzer - Main Entry Point

This script orchestrates the real estate data fetching, analysis, and notification system.
It can be run manually or scheduled to run automatically at regular intervals.

Usage:
    python main.py [--config CONFIG_FILE] [--mode MODE]
    
Modes:
    - fetch: Only fetch new data
    - analyze: Analyze existing data and generate reports
    - notify: Check for properties matching criteria and send notifications
    - all: Run all operations (default)
"""

import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.data_fetcher import RealEstateDataFetcher
from src.core.data_analyzer import RealEstateAnalyzer
from src.visualization.visualization import GraphGenerator
from src.notifications.notification_system import NotificationManager
from src.config.config_manager import ConfigManager
from src.core.database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/real_estate_analyzer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Real Estate Data Analyzer')
    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Configuration file path (default: config/config.yaml)'
    )
    parser.add_argument(
        '--mode',
        choices=['fetch', 'analyze', 'notify', 'all'],
        default='all',
        help='Operation mode (default: all)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        logger.info("Starting Real Estate Data Analyzer")
        logger.info(f"Mode: {args.mode}, Config: {args.config}")
        
        # Initialize configuration
        config = ConfigManager(args.config)
        
        # Initialize database
        db = DatabaseManager(config.get_database_config())
        
        # Initialize components
        data_fetcher = RealEstateDataFetcher(config.get_api_config())
        analyzer = RealEstateAnalyzer(db)
        graph_generator = GraphGenerator(config.get_visualization_config())
        notification_manager = NotificationManager(config.get_notification_config())
        
        if args.mode in ['fetch', 'all']:
            logger.info("Fetching real estate data...")
            new_properties = data_fetcher.fetch_all_sources()
            if new_properties:
                db.save_properties(new_properties)
                logger.info(f"Saved {len(new_properties)} new properties to database")
            else:
                logger.info("No new properties found")
        
        if args.mode in ['analyze', 'all']:
            logger.info("Analyzing data and generating reports...")
            analysis_results = analyzer.run_analysis()
            
            # Generate visualizations
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = Path('output') / timestamp
            output_dir.mkdir(exist_ok=True)
            
            graphs = graph_generator.generate_all_graphs(analysis_results, str(output_dir))
            logger.info(f"Generated {len(graphs)} visualization files")
        
        if args.mode in ['notify', 'all']:
            logger.info("Checking for properties matching notification criteria...")
            matching_properties = analyzer.find_matching_properties(
                config.get_search_criteria()
            )
            
            if matching_properties:
                notification_manager.send_property_alerts(matching_properties)
                logger.info(f"Sent notifications for {len(matching_properties)} matching properties")
            else:
                logger.info("No properties match the notification criteria")
        
        logger.info("Real Estate Data Analyzer completed successfully")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
