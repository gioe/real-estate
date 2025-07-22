#!/usr/bin/env python3
"""
Test suite for RentCast Markets endpoint schemas.

This module contains comprehensive tests for all market statistics schemas including:
- Sale and rental statistics
- Property type and bedroom breakdowns
- Historical data
- Complete market response structure

Usage:
    python test_markets_schemas.py
"""

import unittest
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rentcast_schemas import (
    SaleStatistics,
    RentalStatistics,
    SaleDataByPropertyType,
    SaleDataByBedrooms,
    RentalDataByPropertyType,
    RentalDataByBedrooms,
    SaleHistoryEntry,
    RentalHistoryEntry,
    MarketSaleData,
    MarketRentalData,
    MarketStatistics
)


class TestMarketStatistics(unittest.TestCase):
    """Test cases for market statistics schemas."""

    def setUp(self):
        """Set up test data for market statistics."""
        self.sample_sale_data = {
            "lastUpdatedDate": "2024-07-15T10:30:00.000Z",
            "averagePrice": 450000.0,
            "medianPrice": 425000.0,
            "minPrice": 200000.0,
            "maxPrice": 850000.0,
            "averagePricePerSquareFoot": 225.0,
            "medianPricePerSquareFoot": 215.0,
            "minPricePerSquareFoot": 150.0,
            "maxPricePerSquareFoot": 320.0,
            "averageSquareFootage": 2000.0,
            "medianSquareFootage": 1950.0,
            "minSquareFootage": 800.0,
            "maxSquareFootage": 4500.0,
            "averageDaysOnMarket": 45.0,
            "medianDaysOnMarket": 42.0,
            "minDaysOnMarket": 5,
            "maxDaysOnMarket": 180,
            "newListings": 25,
            "totalListings": 150,
            "dataByPropertyType": [
                {
                    "propertyType": "Single Family",
                    "averagePrice": 475000.0,
                    "medianPrice": 450000.0,
                    "minPrice": 250000.0,
                    "maxPrice": 850000.0,
                    "totalListings": 85
                },
                {
                    "propertyType": "Condo",
                    "averagePrice": 350000.0,
                    "medianPrice": 325000.0,
                    "minPrice": 200000.0,
                    "maxPrice": 550000.0,
                    "totalListings": 65
                }
            ],
            "dataByBedrooms": [
                {
                    "bedrooms": "2",
                    "averagePrice": 375000.0,
                    "medianPrice": 350000.0,
                    "minPrice": 200000.0,
                    "maxPrice": 550000.0,
                    "totalListings": 45
                },
                {
                    "bedrooms": "3",
                    "averagePrice": 485000.0,
                    "medianPrice": 465000.0,
                    "minPrice": 300000.0,
                    "maxPrice": 750000.0,
                    "totalListings": 75
                }
            ],
            "history": {
                "2024-06": {
                    "averagePrice": 440000.0,
                    "medianPrice": 415000.0,
                    "newListings": 22,
                    "totalListings": 145,
                    "dataByPropertyType": [
                        {
                            "propertyType": "Single Family",
                            "averagePrice": 465000.0,
                            "totalListings": 80
                        }
                    ]
                },
                "2024-05": {
                    "averagePrice": 435000.0,
                    "medianPrice": 410000.0,
                    "newListings": 28,
                    "totalListings": 140
                }
            }
        }
        
        self.sample_rental_data = {
            "lastUpdatedDate": "2024-07-15T10:30:00.000Z",
            "averageRent": 2500.0,
            "medianRent": 2400.0,
            "minRent": 1200.0,
            "maxRent": 4800.0,
            "averageRentPerSquareFoot": 1.25,
            "medianRentPerSquareFoot": 1.20,
            "minRentPerSquareFoot": 0.85,
            "maxRentPerSquareFoot": 2.10,
            "averageSquareFootage": 2000.0,
            "medianSquareFootage": 1950.0,
            "minSquareFootage": 600.0,
            "maxSquareFootage": 3500.0,
            "averageDaysOnMarket": 25.0,
            "medianDaysOnMarket": 22.0,
            "minDaysOnMarket": 3,
            "maxDaysOnMarket": 90,
            "newListings": 18,
            "totalListings": 95,
            "dataByPropertyType": [
                {
                    "propertyType": "Apartment",
                    "averageRent": 2200.0,
                    "medianRent": 2100.0,
                    "minRent": 1200.0,
                    "maxRent": 3500.0,
                    "totalListings": 55
                },
                {
                    "propertyType": "Single Family",
                    "averageRent": 3200.0,
                    "medianRent": 3000.0,
                    "minRent": 2000.0,
                    "maxRent": 4800.0,
                    "totalListings": 40
                }
            ],
            "dataByBedrooms": [
                {
                    "bedrooms": "1",
                    "averageRent": 1800.0,
                    "medianRent": 1750.0,
                    "minRent": 1200.0,
                    "maxRent": 2500.0,
                    "totalListings": 25
                },
                {
                    "bedrooms": "2",
                    "averageRent": 2400.0,
                    "medianRent": 2300.0,
                    "minRent": 1800.0,
                    "maxRent": 3200.0,
                    "totalListings": 45
                }
            ],
            "history": {
                "2024-06": {
                    "averageRent": 2450.0,
                    "medianRent": 2350.0,
                    "newListings": 16,
                    "totalListings": 92
                }
            }
        }
        
        self.sample_market_data = {
            "id": "market_12345",
            "zipCode": "90210",
            "saleData": self.sample_sale_data,
            "rentalData": self.sample_rental_data
        }

    def test_sale_statistics_creation(self):
        """Test SaleStatistics creation from dictionary."""
        stats = SaleStatistics.from_dict(self.sample_sale_data)
        
        self.assertEqual(stats.average_price, 450000.0)
        self.assertEqual(stats.median_price, 425000.0)
        self.assertEqual(stats.new_listings, 25)
        self.assertEqual(stats.total_listings, 150)
        self.assertEqual(stats.average_days_on_market, 45.0)

    def test_rental_statistics_creation(self):
        """Test RentalStatistics creation from dictionary."""
        stats = RentalStatistics.from_dict(self.sample_rental_data)
        
        self.assertEqual(stats.average_rent, 2500.0)
        self.assertEqual(stats.median_rent, 2400.0)
        self.assertEqual(stats.new_listings, 18)
        self.assertEqual(stats.total_listings, 95)
        self.assertEqual(stats.average_rent_per_square_foot, 1.25)

    def test_sale_data_by_property_type(self):
        """Test SaleDataByPropertyType parsing."""
        property_type_data = self.sample_sale_data['dataByPropertyType'][0]
        breakdown = SaleDataByPropertyType.from_dict(property_type_data)
        
        self.assertEqual(breakdown.property_type, "Single Family")
        self.assertEqual(breakdown.average_price, 475000.0)
        self.assertEqual(breakdown.median_price, 450000.0)
        self.assertEqual(breakdown.total_listings, 85)

    def test_rental_data_by_bedrooms(self):
        """Test RentalDataByBedrooms parsing."""
        bedrooms_data = self.sample_rental_data['dataByBedrooms'][0]
        breakdown = RentalDataByBedrooms.from_dict(bedrooms_data)
        
        self.assertEqual(breakdown.bedrooms, "1")
        self.assertEqual(breakdown.average_rent, 1800.0)
        self.assertEqual(breakdown.median_rent, 1750.0)
        self.assertEqual(breakdown.total_listings, 25)

    def test_sale_history_entry(self):
        """Test SaleHistoryEntry parsing."""
        date_key = "2024-06"
        history_data = self.sample_sale_data['history'][date_key]
        history_entry = SaleHistoryEntry.from_dict(date_key, history_data)
        
        self.assertEqual(history_entry.date, f"{date_key}-01T00:00:00.000Z")
        self.assertEqual(history_entry.average_price, 440000.0)
        self.assertEqual(history_entry.median_price, 415000.0)
        self.assertEqual(history_entry.new_listings, 22)
        self.assertEqual(len(history_entry.data_by_property_type), 1)
        
        # Test property type breakdown within history
        property_breakdown = history_entry.data_by_property_type[0]
        self.assertEqual(property_breakdown.property_type, "Single Family")
        self.assertEqual(property_breakdown.average_price, 465000.0)

    def test_rental_history_entry(self):
        """Test RentalHistoryEntry parsing."""
        date_key = "2024-06"
        history_data = self.sample_rental_data['history'][date_key]
        history_entry = RentalHistoryEntry.from_dict(date_key, history_data)
        
        self.assertEqual(history_entry.date, f"{date_key}-01T00:00:00.000Z")
        self.assertEqual(history_entry.average_rent, 2450.0)
        self.assertEqual(history_entry.median_rent, 2350.0)
        self.assertEqual(history_entry.new_listings, 16)

    def test_market_sale_data_complete(self):
        """Test complete MarketSaleData parsing."""
        sale_data = MarketSaleData.from_dict(self.sample_sale_data)
        
        # Test main statistics
        self.assertEqual(sale_data.average_price, 450000.0)
        self.assertEqual(sale_data.total_listings, 150)
        self.assertEqual(sale_data.last_updated_date, "2024-07-15T10:30:00.000Z")
        
        # Test breakdowns
        self.assertEqual(len(sale_data.data_by_property_type), 2)
        self.assertEqual(len(sale_data.data_by_bedrooms), 2)
        
        # Test first property type breakdown
        first_property_type = sale_data.data_by_property_type[0]
        self.assertEqual(first_property_type.property_type, "Single Family")
        self.assertEqual(first_property_type.average_price, 475000.0)
        
        # Test history
        self.assertEqual(len(sale_data.history), 2)
        self.assertIn("2024-06", sale_data.history)
        self.assertIn("2024-05", sale_data.history)
        
        june_history = sale_data.history["2024-06"]
        self.assertEqual(june_history.average_price, 440000.0)
        self.assertEqual(len(june_history.data_by_property_type), 1)

    def test_market_rental_data_complete(self):
        """Test complete MarketRentalData parsing."""
        rental_data = MarketRentalData.from_dict(self.sample_rental_data)
        
        # Test main statistics
        self.assertEqual(rental_data.average_rent, 2500.0)
        self.assertEqual(rental_data.total_listings, 95)
        self.assertEqual(rental_data.last_updated_date, "2024-07-15T10:30:00.000Z")
        
        # Test breakdowns
        self.assertEqual(len(rental_data.data_by_property_type), 2)
        self.assertEqual(len(rental_data.data_by_bedrooms), 2)
        
        # Test first property type breakdown
        first_property_type = rental_data.data_by_property_type[0]
        self.assertEqual(first_property_type.property_type, "Apartment")
        self.assertEqual(first_property_type.average_rent, 2200.0)
        
        # Test history
        self.assertEqual(len(rental_data.history), 1)
        self.assertIn("2024-06", rental_data.history)

    def test_complete_market_statistics(self):
        """Test complete MarketStatistics parsing."""
        market_stats = MarketStatistics.from_dict(self.sample_market_data)
        
        # Test top-level fields
        self.assertEqual(market_stats.id, "market_12345")
        self.assertEqual(market_stats.zip_code, "90210")
        
        # Test sale data presence and basic stats
        self.assertIsNotNone(market_stats.sale_data)
        if market_stats.sale_data:
            self.assertEqual(market_stats.sale_data.average_price, 450000.0)
            self.assertEqual(market_stats.sale_data.total_listings, 150)
        
        # Test rental data presence and basic stats
        self.assertIsNotNone(market_stats.rental_data)
        if market_stats.rental_data:
            self.assertEqual(market_stats.rental_data.average_rent, 2500.0)
            self.assertEqual(market_stats.rental_data.total_listings, 95)

    def test_to_dict_serialization(self):
        """Test to_dict serialization for all market schemas."""
        # Test MarketStatistics serialization
        market_stats = MarketStatistics.from_dict(self.sample_market_data)
        serialized = market_stats.to_dict()
        
        # Test basic fields
        self.assertEqual(serialized['id'], "market_12345")
        self.assertEqual(serialized['zipCode'], "90210")
        
        # Test sale data serialization
        self.assertIn('saleData', serialized)
        sale_data_dict = serialized['saleData']
        self.assertEqual(sale_data_dict['averagePrice'], 450000.0)
        self.assertEqual(sale_data_dict['totalListings'], 150)
        
        # Test rental data serialization
        self.assertIn('rentalData', serialized)
        rental_data_dict = serialized['rentalData']
        self.assertEqual(rental_data_dict['averageRent'], 2500.0)
        self.assertEqual(rental_data_dict['totalListings'], 95)
        
        # Test breakdown serialization
        self.assertIn('dataByPropertyType', sale_data_dict)
        self.assertEqual(len(sale_data_dict['dataByPropertyType']), 2)
        
        # Test history serialization
        self.assertIn('history', sale_data_dict)
        self.assertEqual(len(sale_data_dict['history']), 2)
        self.assertIn('2024-06', sale_data_dict['history'])

    def test_round_trip_conversion(self):
        """Test that from_dict and to_dict are inverse operations."""
        # Create MarketStatistics from dictionary
        market_stats = MarketStatistics.from_dict(self.sample_market_data)
        
        # Convert back to dictionary
        serialized = market_stats.to_dict()
        
        # Create new MarketStatistics from serialized data
        market_stats_2 = MarketStatistics.from_dict(serialized)
        
        # Compare key fields
        self.assertEqual(market_stats.id, market_stats_2.id)
        self.assertEqual(market_stats.zip_code, market_stats_2.zip_code)
        
        # Compare sale data
        if market_stats.sale_data and market_stats_2.sale_data:
            self.assertEqual(market_stats.sale_data.average_price, 
                           market_stats_2.sale_data.average_price)
            self.assertEqual(market_stats.sale_data.total_listings, 
                           market_stats_2.sale_data.total_listings)
        
        # Compare rental data
        if market_stats.rental_data and market_stats_2.rental_data:
            self.assertEqual(market_stats.rental_data.average_rent, 
                           market_stats_2.rental_data.average_rent)
            self.assertEqual(market_stats.rental_data.total_listings, 
                           market_stats_2.rental_data.total_listings)

    def test_empty_data_handling(self):
        """Test handling of empty or minimal data."""
        # Test with empty market data
        empty_market = MarketStatistics.from_dict({})
        self.assertIsNone(empty_market.id)
        self.assertIsNone(empty_market.zip_code)
        self.assertIsNone(empty_market.sale_data)
        self.assertIsNone(empty_market.rental_data)
        
        # Test with minimal sale data
        minimal_sale_data = {"averagePrice": 500000.0}
        sale_stats = SaleStatistics.from_dict(minimal_sale_data)
        self.assertEqual(sale_stats.average_price, 500000.0)
        self.assertIsNone(sale_stats.median_price)
        self.assertIsNone(sale_stats.total_listings)

    def test_string_representations(self):
        """Test string representation methods."""
        market_stats = MarketStatistics.from_dict(self.sample_market_data)
        
        # Test __str__
        str_repr = str(market_stats)
        self.assertIn("90210", str_repr)
        self.assertIn("market_12345", str_repr)
        
        # Test __repr__
        repr_str = repr(market_stats)
        self.assertIn("90210", repr_str)
        self.assertIn("sale_listings=150", repr_str)
        self.assertIn("rental_listings=95", repr_str)

    def test_filter_none_values_in_serialization(self):
        """Test that None values are properly filtered in serialization."""
        # Create market statistics with some None values
        minimal_data = {
            "id": "test_id",
            "zipCode": "12345",
            "saleData": {
                "averagePrice": 400000.0,
                # medianPrice intentionally omitted
            }
        }
        
        market_stats = MarketStatistics.from_dict(minimal_data)
        serialized = market_stats.to_dict()
        
        # Verify basic structure
        self.assertEqual(serialized['id'], "test_id")
        self.assertEqual(serialized['zipCode'], "12345")
        
        # Check sale data
        sale_data = serialized['saleData']
        self.assertEqual(sale_data['averagePrice'], 400000.0)
        # medianPrice should be None and included
        self.assertIn('medianPrice', sale_data)
        self.assertIsNone(sale_data['medianPrice'])


def run_all_tests():
    """Run all market schema tests."""
    print("Running Market Statistics Schema Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMarketStatistics)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print(f"✅ All {result.testsRun} tests passed successfully!")
        return True
    else:
        print(f"❌ {len(result.failures + result.errors)} tests failed out of {result.testsRun}")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
