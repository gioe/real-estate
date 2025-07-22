#!/usr/bin/env python3
"""
Example Script - Real Estate Data Analyzer Demo

This script demonstrates the real estate analyzer with sample data,
so you can see how it works without needing real API keys.

Usage:
    python example.py
"""

import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import random

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.data_analyzer import RealEstateAnalyzer
from src.visualization.visualization import GraphGenerator
from src.config.config_manager import ConfigManager
from src.core.database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def generate_sample_properties(count: int = 50) -> list:
    """Generate sample property data for demonstration."""
    
    cities = ['San Francisco', 'Oakland', 'San Jose', 'Berkeley', 'Palo Alto', 'Mountain View']
    property_types = ['house', 'condo', 'townhome']
    
    properties = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(count):
        # Generate realistic-looking sample data
        city = random.choice(cities)
        prop_type = random.choice(property_types)
        
        # Price varies by city and type
        base_price = {
            'San Francisco': 850000,
            'Oakland': 650000,
            'San Jose': 750000,
            'Berkeley': 700000,
            'Palo Alto': 950000,
            'Mountain View': 800000
        }[city]
        
        price = base_price + random.randint(-200000, 300000)
        bedrooms = random.randint(1, 5)
        bathrooms = random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4])
        sqft = random.randint(800, 3000)
        
        # Generate listing date within last 30 days
        days_ago = random.randint(0, 30)
        listing_date = (base_date + timedelta(days=days_ago)).isoformat()
        
        property_data = {
            'property_id': f'SAMPLE_{i+1:03d}',
            'source': 'sample_data',
            'address': f'{random.randint(100, 9999)} {random.choice(["Main", "Oak", "Pine", "Elm", "Market"])} St',
            'city': city,
            'state': 'CA',
            'zip_code': f'9{random.randint(4000, 4999)}',
            'price': price,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'square_feet': sqft,
            'lot_size': random.randint(2000, 8000) if prop_type == 'house' else None,
            'year_built': random.randint(1950, 2023),
            'property_type': prop_type,
            'listing_date': listing_date,
            'days_on_market': days_ago,
            'url': f'https://example.com/property/{i+1}',
            'latitude': 37.7749 + random.uniform(-0.2, 0.2),
            'longitude': -122.4194 + random.uniform(-0.2, 0.2),
            'fetched_at': datetime.now().isoformat()
        }
        
        properties.append(property_data)
    
    return properties


def run_example_analysis():
    """Run the example analysis with sample data."""
    
    logger.info("Starting Real Estate Data Analyzer Example")
    
    try:
        # Initialize configuration
        config = ConfigManager()
        
        # Initialize database
        db = DatabaseManager(config.get_database_config())
        
        # Generate and save sample properties
        logger.info("Generating sample property data...")
        sample_properties = generate_sample_properties(50)
        
        saved_count = db.save_properties(sample_properties)
        logger.info(f"Saved {saved_count} sample properties to database")
        
        # Initialize analyzer and run analysis
        logger.info("Running market analysis...")
        analyzer = RealEstateAnalyzer(db)
        analysis_results = analyzer.run_analysis()
        
        if analysis_results:
            logger.info("Analysis completed successfully!")
            
            # Display some key results
            if 'market_summary' in analysis_results:
                summary = analysis_results['market_summary']
                logger.info(f"Market Summary:")
                logger.info(f"  Total Properties: {summary.get('total_properties', 'N/A')}")
                logger.info(f"  Median Price: ${summary.get('price_summary', {}).get('median_price', 0):,.0f}")
                logger.info(f"  Average Price: ${summary.get('price_summary', {}).get('average_price', 0):,.0f}")
            
            # Generate visualizations
            logger.info("Generating visualizations...")
            graph_generator = GraphGenerator(config.get_visualization_config())
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = Path('output') / f'example_{timestamp}'
            
            try:
                graphs = graph_generator.generate_all_graphs(analysis_results, str(output_dir))
                logger.info(f"Generated {len(graphs)} visualization files in {output_dir}")
                
                # List generated files
                for graph_file in graphs:
                    logger.info(f"  📊 {Path(graph_file).name}")
                    
            except Exception as viz_error:
                logger.warning(f"Visualization generation failed: {str(viz_error)}")
                logger.info("This is expected if matplotlib backend is not configured properly")
            
            # Test property matching
            logger.info("Testing property matching for notifications...")
            search_criteria = config.get_search_criteria()
            matching_properties = analyzer.find_matching_properties(search_criteria)
            
            logger.info(f"Found {len(matching_properties)} properties matching your criteria")
            
            if matching_properties:
                logger.info("Sample matching properties:")
                for i, prop in enumerate(matching_properties[:3], 1):
                    logger.info(f"  {i}. {prop.get('address', 'N/A')} - ${prop.get('price', 0):,.0f}")
            
            # Save analysis results
            db.save_analysis_results('example_run', analysis_results)
            
            # Display database stats
            stats = db.get_database_stats()
            logger.info("Database Statistics:")
            logger.info(f"  Properties: {stats.get('property_count', 0)}")
            logger.info(f"  Analysis Records: {stats.get('analysis_count', 0)}")
            logger.info(f"  Database Size: {stats.get('database_size_mb', 0):.2f} MB")
            
        else:
            logger.error("Analysis failed - no results generated")
            
    except Exception as e:
        logger.error(f"Example analysis failed: {str(e)}", exc_info=True)
        return False
    
    logger.info("Example completed successfully! ✅")
    logger.info("\nNext steps:")
    logger.info("1. Configure real API keys in your .env file")
    logger.info("2. Customize search criteria in config/config.yaml")
    logger.info("3. Run: python main.py --mode fetch")
    logger.info("4. Check output/ directory for generated visualizations")
    
    return True


if __name__ == "__main__":
    success = run_example_analysis()
    sys.exit(0 if success else 1)
