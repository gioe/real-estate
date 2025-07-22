#!/usr/bin/env python3
"""
Test script for AVM schemas.

This script tests the new AVMValueResponse and AVMRentResponse schemas
with sample data based on the API documentation.
"""

from src.schemas.rentcast_schemas import AVMValueResponse, AVMRentResponse, Comparable, ListingType


def test_avm_value_response():
    """Test AVMValueResponse with sample data."""
    print("Testing AVMValueResponse...")
    
    sample_data = {
        "price": 221000,
        "priceRangeLow": 208000,
        "priceRangeHigh": 233000,
        "latitude": 29.475962,
        "longitude": -98.351442,
        "comparables": [
            {
                "id": "5014-Fern-Lk,-San-Antonio,-TX-78244",
                "formattedAddress": "5014 Fern Lk, San Antonio, TX 78244",
                "addressLine1": "5014 Fern Lk",
                "addressLine2": "Apt 12",
                "city": "San Antonio",
                "state": "TX",
                "zipCode": "78244",
                "county": "Bexar",
                "latitude": 29.471777,
                "longitude": -98.350172,
                "propertyType": "Single Family",
                "bedrooms": 4,
                "bathrooms": 2,
                "squareFootage": 1747,
                "lotSize": 6316,
                "yearBuilt": 1986,
                "price": 229900,
                "listingType": "Standard",
                "listedDate": "2024-04-03T00:00:00.000Z",
                "removedDate": "2024-05-26T00:00:00.000Z",
                "lastSeenDate": "2024-05-25T13:11:55.018Z",
                "daysOnMarket": 53,
                "distance": 0.2994,
                "daysOld": 127,
                "correlation": 0.9822
            }
        ]
    }
    
    # Test from_dict method
    avm_response = AVMValueResponse.from_dict(sample_data)
    
    # Verify basic fields
    assert avm_response.price == 221000
    assert avm_response.price_range_low == 208000
    assert avm_response.price_range_high == 233000
    assert avm_response.latitude == 29.475962
    assert avm_response.longitude == -98.351442
    assert len(avm_response.comparables) == 1
    
    # Verify comparable data
    comp = avm_response.comparables[0]
    assert comp.id == "5014-Fern-Lk,-San-Antonio,-TX-78244"
    assert comp.bedrooms == 4
    assert comp.bathrooms == 2
    assert comp.square_footage == 1747
    assert comp.price == 229900
    assert comp.correlation == 0.9822
    
    # Test to_dict method
    result_dict = avm_response.to_dict()
    assert result_dict['price'] == 221000
    assert result_dict['priceRangeLow'] == 208000
    assert len(result_dict['comparables']) == 1
    
    print("✅ AVMValueResponse test passed!")


def test_avm_rent_response():
    """Test AVMRentResponse with sample data."""
    print("Testing AVMRentResponse...")
    
    sample_data = {
        "rent": 1670,
        "rentRangeLow": 1630,
        "rentRangeHigh": 1710,
        "latitude": 29.475962,
        "longitude": -98.351442,
        "comparables": [
            {
                "id": "test-rental-property-1",
                "formattedAddress": "123 Test St, San Antonio, TX 78244",
                "city": "San Antonio",
                "state": "TX",
                "zipCode": "78244",
                "propertyType": "Single Family",
                "bedrooms": 3,
                "bathrooms": 2,
                "squareFootage": 1500,
                "price": 1650,
                "distance": 0.5,
                "correlation": 0.95
            }
        ]
    }
    
    # Test from_dict method
    rent_response = AVMRentResponse.from_dict(sample_data)
    
    # Verify basic fields
    assert rent_response.rent == 1670
    assert rent_response.rent_range_low == 1630
    assert rent_response.rent_range_high == 1710
    assert rent_response.latitude == 29.475962
    assert rent_response.longitude == -98.351442
    assert len(rent_response.comparables) == 1
    
    # Verify comparable data
    comp = rent_response.comparables[0]
    assert comp.id == "test-rental-property-1"
    assert comp.bedrooms == 3
    assert comp.bathrooms == 2
    assert comp.price == 1650  # This is rent price for rental comps
    
    # Test to_dict method
    result_dict = rent_response.to_dict()
    assert result_dict['rent'] == 1670
    assert result_dict['rentRangeLow'] == 1630
    assert len(result_dict['comparables']) == 1
    
    print("✅ AVMRentResponse test passed!")


def test_comparable_standalone():
    """Test Comparable as a standalone object."""
    print("Testing Comparable standalone...")
    
    comp_data = {
        "id": "test-comp-1",
        "formattedAddress": "456 Example Ave, Austin, TX 73301",
        "city": "Austin",
        "state": "TX",
        "zipCode": "73301",
        "propertyType": "Condo",
        "bedrooms": 2,
        "bathrooms": 1.5,
        "squareFootage": 1200,
        "price": 185000,
        "listingType": "Standard",
        "daysOnMarket": 30,
        "distance": 1.2,
        "correlation": 0.88
    }
    
    # Test from_dict method
    comp = Comparable.from_dict(comp_data)
    
    # Verify fields
    assert comp.id == "test-comp-1"
    assert comp.property_type == "Condo"
    assert comp.bedrooms == 2
    assert comp.bathrooms == 1.5
    assert comp.square_footage == 1200
    assert comp.price == 185000
    assert comp.listing_type == "Standard"
    assert comp.correlation == 0.88
    
    # Test to_dict method
    result = comp.to_dict()
    assert result['id'] == "test-comp-1"
    assert result['propertyType'] == "Condo"
    assert result['bedrooms'] == 2
    
    print("✅ Comparable standalone test passed!")


def main():
    """Run all tests."""
    print("Running AVM Schema Tests...")
    print("=" * 40)
    
    try:
        test_avm_value_response()
        test_avm_rent_response()
        test_comparable_standalone()
        
        print("=" * 40)
        print("🎉 All AVM schema tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    main()
