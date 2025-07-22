"""
Mock Data Loader

Provides utilities to load realistic test data for the real estate analysis pipeline
without making any external API calls. All data is schema-compliant and designed
to test different deal scenarios.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .schemas.rentcast_schemas import PropertyListing, AVMValueResponse, MarketStatistics
from .core.deal_analyzer import DealScore


logger = logging.getLogger(__name__)


class MockDataLoader:
    """Loads and provides mock data for testing the deal analysis pipeline."""
    
    def __init__(self, mock_data_dir: str = "mock_data"):
        """
        Initialize the mock data loader.
        
        Args:
            mock_data_dir: Directory containing mock data files
        """
        self.mock_data_dir = Path(mock_data_dir)
        self._properties_cache = None
        self._avm_cache = None
        self._market_cache = None
        self._scenarios_cache = None
    
    def get_mock_properties(self) -> List[PropertyListing]:
        """
        Load mock property listings.
        
        Returns:
            List of PropertyListing objects
        """
        if self._properties_cache is None:
            try:
                properties_file = self.mock_data_dir / "property_listings.json"
                with open(properties_file, 'r') as f:
                    data = json.load(f)
                
                self._properties_cache = [
                    PropertyListing.from_dict(prop) 
                    for prop in data['properties']
                ]
                
                logger.info(f"Loaded {len(self._properties_cache)} mock properties")
                
            except Exception as e:
                logger.error(f"Failed to load mock properties: {e}")
                self._properties_cache = []
        
        return self._properties_cache
    
    def _load_avm_data(self) -> Dict[str, Any]:
        """Load AVM data from file."""
        if self._avm_cache is None:
            try:
                avm_file = self.mock_data_dir / "avm_valuations.json"
                with open(avm_file, 'r') as f:
                    data = json.load(f)
                self._avm_cache = data['avm_valuations']
                logger.info(f"Loaded {len(self._avm_cache)} AVM valuations")
            except Exception as e:
                logger.error(f"Failed to load AVM data: {e}")
                self._avm_cache = {}
        return self._avm_cache
    
    def _load_market_data(self) -> Dict[str, Any]:
        """Load market statistics from file."""
        if self._market_cache is None:
            try:
                market_file = self.mock_data_dir / "market_statistics.json"
                with open(market_file, 'r') as f:
                    data = json.load(f)
                self._market_cache = data['market_statistics']
                logger.info(f"Loaded market data for {len(self._market_cache)} ZIP codes")
            except Exception as e:
                logger.error(f"Failed to load market data: {e}")
                self._market_cache = {}
        return self._market_cache
    
    def _load_scenarios(self) -> List[Dict[str, Any]]:
        """Load test scenarios from file."""
        if self._scenarios_cache is None:
            try:
                scenarios_file = self.mock_data_dir / "test_scenarios.json"
                with open(scenarios_file, 'r') as f:
                    data = json.load(f)
                self._scenarios_cache = data['scenarios']
                logger.info(f"Loaded {len(self._scenarios_cache)} test scenarios")
            except Exception as e:
                logger.error(f"Failed to load test scenarios: {e}")
                self._scenarios_cache = []
        return self._scenarios_cache
    
    def get_mock_avm_value(self, address: str) -> Optional[AVMValueResponse]:
        """
        Get mock AVM valuation for a property address.
        
        Args:
            address: Property address to get valuation for
            
        Returns:
            AVMValueResponse object or None if not found
        """
        avm_data = self._load_avm_data()
        
        if address in avm_data:
            data = avm_data[address]
            return AVMValueResponse.from_dict(data)
        
        return None
    
    def get_mock_market_statistics(self, zip_code: str) -> Optional[MarketStatistics]:
        """
        Get mock market statistics for a zip code.
        
        Args:
            zip_code: ZIP code to get market data for
            
        Returns:
            MarketStatistics or None if not found
        """
        if self._market_cache is None:
            try:
                market_file = self.mock_data_dir / "market_statistics.json"
                with open(market_file, 'r') as f:
                    data = json.load(f)
                
                self._market_cache = data['market_statistics']
                logger.debug(f"Loaded market data for {len(self._market_cache)} zip codes")
                
            except Exception as e:
                logger.error(f"Failed to load mock market data: {e}")
                self._market_cache = {}
        
        market_data = self._market_cache.get(zip_code)
        if market_data:
            return MarketStatistics.from_dict(market_data)
        else:
            logger.warning(f"No mock market data found for zip code: {zip_code}")
            return None
    
    def get_test_scenarios(self) -> List[Dict[str, Any]]:
        """
        Get predefined test scenarios with expected outcomes.
        
        Returns:
            List of test scenario dictionaries
        """
        if self._scenarios_cache is None:
            try:
                scenarios_file = self.mock_data_dir / "test_scenarios.json"
                with open(scenarios_file, 'r') as f:
                    data = json.load(f)
                
                self._scenarios_cache = data['deal_scenarios']
                logger.info(f"Loaded {len(self._scenarios_cache)} test scenarios")
                
            except Exception as e:
                logger.error(f"Failed to load test scenarios: {e}")
                self._scenarios_cache = []
        
        return self._scenarios_cache
    
    def get_property_by_id(self, property_id: str) -> Optional[PropertyListing]:
        """
        Get a specific property by its ID.
        
        Args:
            property_id: Property ID to search for
            
        Returns:
            PropertyListing or None if not found
        """
        properties = self.get_mock_properties()
        for prop in properties:
            if prop.id == property_id:
                return prop
        
        logger.warning(f"Property not found with ID: {property_id}")
        return None
    
    def get_properties_by_zip(self, zip_code: str) -> List[PropertyListing]:
        """
        Get all properties in a specific zip code.
        
        Args:
            zip_code: ZIP code to filter by
            
        Returns:
            List of PropertyListing objects in the zip code
        """
        properties = self.get_mock_properties()
        return [prop for prop in properties if prop.zip_code == zip_code]
    
    def get_properties_by_price_range(self, min_price: int, max_price: int) -> List[PropertyListing]:
        """
        Get properties within a price range.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            
        Returns:
            List of PropertyListing objects in the price range
        """
        properties = self.get_mock_properties()
        return [
            prop for prop in properties 
            if prop.price and min_price <= prop.price <= max_price
        ]
    
    def get_excellent_deal_properties(self) -> List[PropertyListing]:
        """
        Get properties that should score as excellent deals.
        
        Returns:
            List of PropertyListing objects expected to be excellent deals
        """
        scenarios = self.get_test_scenarios()
        excellent_scenarios = [
            s for s in scenarios 
            if s['expected_deal_type'] in ['Excellent', 'Good']
        ]
        
        properties = []
        for scenario in excellent_scenarios:
            prop = self.get_property_by_id(scenario['property']['id'])
            if prop:
                properties.append(prop)
        
        return properties
    
    def create_complete_analysis_data(self, property_id: str) -> Dict[str, Any]:
        """
        Create complete data package for a property analysis.
        
        Args:
            property_id: Property ID to get complete data for
            
        Returns:
            Dictionary with property, AVM, and market data
        """
        property_listing = self.get_property_by_id(property_id)
        if not property_listing:
            return {}
        
        avm_value = self.get_mock_avm_value(property_listing.formatted_address)
        market_stats = self.get_mock_market_statistics(property_listing.zip_code)
        
        return {
            'property': property_listing,
            'avm_value': avm_value,
            'market_stats': market_stats,
            'has_complete_data': all([property_listing, avm_value, market_stats])
        }
    
    def get_data_coverage_report(self) -> Dict[str, Any]:
        """
        Generate a report on mock data coverage.
        
        Returns:
            Dictionary with coverage statistics
        """
        properties = self.get_mock_properties()
        
        # Check AVM coverage
        avm_coverage = 0
        market_coverage = 0
        zip_codes = set()
        
        for prop in properties:
            if self.get_mock_avm_value(prop.formatted_address):
                avm_coverage += 1
            
            if prop.zip_code:
                zip_codes.add(prop.zip_code)
                if self.get_mock_market_statistics(prop.zip_code):
                    market_coverage += 1
        
        scenarios = self.get_test_scenarios()
        
        return {
            'total_properties': len(properties),
            'avm_coverage': {
                'count': avm_coverage,
                'percentage': (avm_coverage / len(properties)) * 100 if properties else 0
            },
            'market_coverage': {
                'count': market_coverage,
                'percentage': (market_coverage / len(properties)) * 100 if properties else 0
            },
            'unique_zip_codes': len(zip_codes),
            'zip_codes': sorted(list(zip_codes)),
            'test_scenarios': len(scenarios),
            'complete_data_properties': sum(
                1 for prop in properties 
                if self.get_mock_avm_value(prop.formatted_address) and 
                   self.get_mock_market_statistics(prop.zip_code)
            )
        }


class MockRentCastClient:
    """
    Mock RentCast client that returns mock data instead of making API calls.
    Drop-in replacement for the real RentCastClient during testing.
    """
    
    def __init__(self, config_manager=None):
        """Initialize mock client."""
        self.mock_loader = MockDataLoader()
        logger.info("Initialized MockRentCastClient - no API calls will be made")
    
    def get_avm_value(self, address: str) -> Optional[AVMValueResponse]:
        """
        Get mock AVM valuation for an address.
        
        Args:
            address: Property address
            
        Returns:
            Mock AVMValueResponse or None
        """
        logger.debug(f"MockRentCastClient: Getting AVM value for {address}")
        return self.mock_loader.get_mock_avm_value(address)
    
    def get_market_statistics(self, zip_code: str) -> Optional[MarketStatistics]:
        """
        Get mock market statistics for a zip code.
        
        Args:
            zip_code: ZIP code
            
        Returns:
            Mock MarketStatistics or None
        """
        logger.debug(f"MockRentCastClient: Getting market stats for {zip_code}")
        return self.mock_loader.get_mock_market_statistics(zip_code)
    
    def get_properties(self, **kwargs) -> List[PropertyListing]:
        """
        Get mock properties based on search criteria.
        
        Returns:
            List of mock PropertyListing objects
        """
        logger.debug("MockRentCastClient: Getting mock properties")
        return self.mock_loader.get_mock_properties()


def create_mock_config() -> Dict[str, Any]:
    """
    Create a mock configuration for testing.
    
    Returns:
        Mock configuration dictionary
    """
    return {
        'database': {
            'type': 'sqlite',
            'sqlite_path': 'data/test_real_estate.db'
        },
        'api': {
            'rentcast_api_key': 'mock-api-key',
            'rentcast_endpoint': 'https://mock.api.endpoint'
        },
        'mock_mode': True
    }
