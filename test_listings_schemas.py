#!/usr/bin/env python3
"""
Test script for Listings schemas.

This script tests the PropertyListing, ListingsResponse, and related schemas
with comprehensive sample data based on the API documentation.
"""

from src.schemas.rentcast_schemas import (
    PropertyListing, ListingsResponse, ListingAgent, ListingOffice, 
    Builder, ListingHistoryEntry, ListingStatus, ListingEventType, 
    ListingType, HOADetails
)


def test_listing_agent():
    """Test ListingAgent schema."""
    print("Testing ListingAgent...")
    
    agent_data = {
        "name": "Jennifer Welch",
        "phone": "5124313110",
        "email": "jennifer@example.com",
        "website": "https://example.com"
    }
    
    agent = ListingAgent.from_dict(agent_data)
    assert agent.name == "Jennifer Welch"
    assert agent.phone == "5124313110"
    
    # Test to_dict conversion
    result_dict = agent.to_dict()
    assert result_dict['name'] == "Jennifer Welch"
    assert result_dict['phone'] == "5124313110"
    
    print("✅ ListingAgent test passed!")


def test_listing_office():
    """Test ListingOffice schema."""
    print("Testing ListingOffice...")
    
    office_data = {
        "name": "Gottesman Residential RE",
        "phone": "5124512422",
        "email": "office@example.com",
        "website": "https://gottesman.example.com"
    }
    
    office = ListingOffice.from_dict(office_data)
    assert office.name == "Gottesman Residential RE"
    assert office.phone == "5124512422"
    
    # Test to_dict conversion
    result_dict = office.to_dict()
    assert result_dict['name'] == "Gottesman Residential RE"
    
    print("✅ ListingOffice test passed!")


def test_builder():
    """Test Builder schema."""
    print("Testing Builder...")
    
    builder_data = {
        "name": "Pulte Homes",
        "development": "Hampton Lakes at River Hall",
        "phone": "2392300326",
        "website": "https://pultehomes.com"
    }
    
    builder = Builder.from_dict(builder_data)
    assert builder.name == "Pulte Homes"
    assert builder.development == "Hampton Lakes at River Hall"
    
    # Test to_dict conversion
    result_dict = builder.to_dict()
    assert result_dict['name'] == "Pulte Homes"
    assert result_dict['development'] == "Hampton Lakes at River Hall"
    
    print("✅ Builder test passed!")


def test_listing_history_entry():
    """Test ListingHistoryEntry schema."""
    print("Testing ListingHistoryEntry...")
    
    history_data = {
        "event": "Sale Listing",
        "price": 899000,
        "listingType": "Standard",
        "listedDate": "2024-06-24T00:00:00.000Z",
        "removedDate": "2024-10-01T00:00:00.000Z",
        "daysOnMarket": 99
    }
    
    history_entry = ListingHistoryEntry.from_dict("2024-06-24", history_data)
    assert history_entry.date == "2024-06-24"
    assert history_entry.event == "Sale Listing"
    assert history_entry.price == 899000
    assert history_entry.days_on_market == 99
    
    # Test to_dict conversion
    result_dict = history_entry.to_dict()
    assert result_dict['event'] == "Sale Listing"
    assert result_dict['price'] == 899000
    
    print("✅ ListingHistoryEntry test passed!")


def test_property_listing():
    """Test PropertyListing with comprehensive data."""
    print("Testing PropertyListing...")
    
    # Comprehensive sample data based on API documentation
    listing_data = {
        "id": "3821-Hargis-St,-Austin,-TX-78723",
        "formattedAddress": "3821 Hargis St, Austin, TX 78723",
        "addressLine1": "3821 Hargis St",
        "addressLine2": "Apt 12",
        "city": "Austin",
        "state": "TX",
        "zipCode": "78723",
        "county": "Travis",
        "latitude": 30.290643,
        "longitude": -97.701547,
        "propertyType": "Single Family",
        "bedrooms": 4,
        "bathrooms": 2.5,
        "squareFootage": 2345,
        "lotSize": 3284,
        "yearBuilt": 2008,
        "hoa": {
            "fee": 65
        },
        "status": "Active",
        "price": 899000,
        "listingType": "Standard",
        "listedDate": "2024-06-24T00:00:00.000Z",
        "removedDate": "2024-10-01T00:00:00.000Z",
        "createdDate": "2021-06-25T00:00:00.000Z",
        "lastSeenDate": "2024-09-30T13:11:47.157Z",
        "daysOnMarket": 99,
        "mlsName": "UnlockMLS",
        "mlsNumber": "5519228",
        "listingAgent": {
            "name": "Jennifer Welch",
            "phone": "5124313110",
            "email": "jennifer@example.com",
            "website": "https://example.com"
        },
        "listingOffice": {
            "name": "Gottesman Residential RE",
            "phone": "5124512422",
            "email": "office@example.com",
            "website": "https://gottesman.com"
        },
        "builder": {
            "name": "Pulte Homes",
            "development": "Hampton Lakes at River Hall",
            "phone": "2392300326",
            "website": "https://pultehomes.com"
        },
        "history": {
            "2024-06-24": {
                "event": "Sale Listing",
                "price": 899000,
                "listingType": "Standard",
                "listedDate": "2024-06-24T00:00:00.000Z",
                "removedDate": "2024-10-01T00:00:00.000Z",
                "daysOnMarket": 99
            },
            "2024-05-15": {
                "event": "Sale Listing",
                "price": 879000,
                "listingType": "Standard",
                "listedDate": "2024-05-15T00:00:00.000Z",
                "removedDate": "2024-06-10T00:00:00.000Z",
                "daysOnMarket": 26
            }
        }
    }
    
    # Test from_dict method
    listing = PropertyListing.from_dict(listing_data)
    
    # Verify basic property fields
    assert listing.id == "3821-Hargis-St,-Austin,-TX-78723"
    assert listing.formatted_address == "3821 Hargis St, Austin, TX 78723"
    assert listing.bedrooms == 4
    assert listing.bathrooms == 2.5
    assert listing.square_footage == 2345
    assert listing.year_built == 2008
    
    # Verify listing-specific fields
    assert listing.status == "Active"
    assert listing.price == 899000
    assert listing.listing_type == "Standard"
    assert listing.days_on_market == 99
    assert listing.mls_name == "UnlockMLS"
    assert listing.mls_number == "5519228"
    
    # Verify HOA details
    assert listing.hoa is not None
    assert listing.hoa.fee == 65
    
    # Verify agent information
    assert listing.listing_agent is not None
    assert listing.listing_agent.name == "Jennifer Welch"
    assert listing.listing_agent.phone == "5124313110"
    
    # Verify office information
    assert listing.listing_office is not None
    assert listing.listing_office.name == "Gottesman Residential RE"
    
    # Verify builder information
    assert listing.builder is not None
    assert listing.builder.name == "Pulte Homes"
    assert listing.builder.development == "Hampton Lakes at River Hall"
    
    # Verify history
    assert len(listing.history) == 2
    assert "2024-06-24" in listing.history
    assert "2024-05-15" in listing.history
    
    june_history = listing.history["2024-06-24"]
    assert june_history.event == "Sale Listing"
    assert june_history.price == 899000
    
    may_history = listing.history["2024-05-15"]
    assert may_history.price == 879000
    assert may_history.days_on_market == 26
    
    # Test to_dict method
    result_dict = listing.to_dict()
    assert result_dict['id'] == "3821-Hargis-St,-Austin,-TX-78723"
    assert result_dict['price'] == 899000
    assert result_dict['status'] == "Active"
    assert 'listingAgent' in result_dict
    assert 'listingOffice' in result_dict
    assert 'builder' in result_dict
    assert 'history' in result_dict
    assert len(result_dict['history']) == 2
    
    # Test string representations
    str_repr = str(listing)
    assert "3821-Hargis-St,-Austin,-TX-78723" in str_repr
    assert "Active" in str_repr
    assert "$899,000" in str_repr
    
    print("✅ PropertyListing test passed!")


def test_listings_response():
    """Test ListingsResponse with multiple listings."""
    print("Testing ListingsResponse...")
    
    # Sample response with multiple listings
    response_data = {
        "listings": [
            {
                "id": "listing-1",
                "formattedAddress": "123 Main St, Austin, TX 78701",
                "city": "Austin",
                "state": "TX",
                "zipCode": "78701",
                "propertyType": "Condo",
                "bedrooms": 2,
                "bathrooms": 2,
                "price": 450000,
                "status": "Active",
                "listingType": "Standard"
            },
            {
                "id": "listing-2",
                "formattedAddress": "456 Oak Ave, Austin, TX 78702",
                "city": "Austin",
                "state": "TX",
                "zipCode": "78702",
                "propertyType": "Single Family",
                "bedrooms": 3,
                "bathrooms": 2.5,
                "price": 650000,
                "status": "Active",
                "listingType": "New Construction"
            }
        ],
        "totalCount": 250,
        "hasMore": True,
        "nextOffset": 2
    }
    
    # Test from_dict method
    response = ListingsResponse.from_dict(response_data)
    
    assert len(response.listings) == 2
    assert response.total_count == 250
    assert response.has_more == True
    assert response.next_offset == 2
    
    # Verify individual listings
    first_listing = response.listings[0]
    assert first_listing.id == "listing-1"
    assert first_listing.property_type == "Condo"
    assert first_listing.price == 450000
    
    second_listing = response.listings[1]
    assert second_listing.id == "listing-2"
    assert second_listing.listing_type == "New Construction"
    assert second_listing.bedrooms == 3
    
    # Test to_dict method
    result_dict = response.to_dict()
    assert len(result_dict['listings']) == 2
    assert result_dict['totalCount'] == 250
    assert result_dict['hasMore'] == True
    
    print("✅ ListingsResponse test passed!")


def test_enums():
    """Test the listing-related enums."""
    print("Testing Listing Enums...")
    
    # Test ListingStatus
    assert ListingStatus.ACTIVE.value == "Active"
    assert ListingStatus.INACTIVE.value == "Inactive"
    
    # Test ListingType
    assert ListingType.STANDARD.value == "Standard"
    assert ListingType.NEW_CONSTRUCTION.value == "New Construction"
    assert ListingType.FORECLOSURE.value == "Foreclosure"
    assert ListingType.SHORT_SALE.value == "Short Sale"
    
    # Test ListingEventType
    assert ListingEventType.SALE_LISTING.value == "Sale Listing"
    assert ListingEventType.RENTAL_LISTING.value == "Rental Listing"
    
    print("✅ Listing Enums test passed!")


def test_edge_cases():
    """Test edge cases and minimal data."""
    print("Testing Edge Cases...")
    
    # Test minimal listing data
    minimal_data = {
        "id": "minimal-listing",
        "formattedAddress": "123 Test St, Austin, TX 78701"
    }
    
    listing = PropertyListing.from_dict(minimal_data)
    assert listing.id == "minimal-listing"
    assert listing.formatted_address == "123 Test St, Austin, TX 78701"
    assert listing.price is None
    assert listing.bedrooms is None
    
    # Test empty history
    assert len(listing.history) == 0
    
    # Test to_dict with minimal data
    result_dict = listing.to_dict()
    assert 'id' in result_dict
    assert 'formattedAddress' in result_dict
    # None values should be filtered out
    assert 'price' not in result_dict or result_dict['price'] is None
    
    # Test empty listings response
    empty_response_data = {"listings": []}
    response = ListingsResponse.from_dict(empty_response_data)
    assert len(response.listings) == 0
    assert response.total_count is None
    
    print("✅ Edge Cases test passed!")


def main():
    """Run all listings schema tests."""
    print("Running Listings Schema Tests...")
    print("=" * 50)
    
    try:
        test_listing_agent()
        test_listing_office()
        test_builder()
        test_listing_history_entry()
        test_property_listing()
        test_listings_response()
        test_enums()
        test_edge_cases()
        
        print("=" * 50)
        print("🎉 All listings schema tests passed successfully!")
        
        # Summary
        print("\n📋 Implemented Schemas:")
        print("  ✅ PropertyListing - Complete listing with all fields")
        print("  ✅ ListingsResponse - Paginated listings response")
        print("  ✅ ListingAgent - Agent contact information")
        print("  ✅ ListingOffice - Office/broker information")
        print("  ✅ Builder - New construction builder details")
        print("  ✅ ListingHistoryEntry - Historical listing data")
        print("  ✅ ListingStatus, ListingType, ListingEventType - Enumerations")
        
        print("\n🚀 Ready for integration with RentCast listings API!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
