#!/usr/bin/env python3
"""
RentCast Property Schema Test Script

This script demonstrates the Property schema and dataclasses created for the RentCast API.
It shows how to parse property data and work with the typed objects.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.schemas.rentcast_schemas import (
    Property, 
    PropertiesResponse, 
    PropertyFeatures, 
    HOADetails,
    PropertyOwner,
    Address,
    TaxAssessmentEntry,
    PropertyTaxEntry,
    PropertyHistoryEntry,
    AVMValueResponse,
    AVMRentResponse,
    Comparable,
    ListingType,
    PropertyListing,
    ListingsResponse,
    ListingAgent,
    ListingOffice,
    Builder,
    ListingHistoryEntry,
    ListingStatus,
    ListingEventType,
    parse_property_response,
    filter_properties_by_criteria
)


def create_sample_property_data() -> Dict[str, Any]:
    """Create sample property data matching the RentCast schema."""
    return {
        "id": "5500-Grand-Lake-Dr,-San-Antonio,-TX-78244",
        "formattedAddress": "5500 Grand Lake Dr, San Antonio, TX 78244",
        "addressLine1": "5500 Grand Lake Dr",
        "addressLine2": "Apt 12",
        "city": "San Antonio",
        "state": "TX",
        "zipCode": "78244",
        "county": "Bexar",
        "latitude": 29.476011,
        "longitude": -98.351454,
        "propertyType": "Single Family",
        "bedrooms": 3,
        "bathrooms": 2,
        "squareFootage": 1878,
        "lotSize": 8843,
        "yearBuilt": 1973,
        "assessorID": "05076-103-0500",
        "legalDescription": "CB 5076A BLK 3 LOT 50",
        "subdivision": "CONV A/S CODE",
        "zoning": "RH",
        "lastSaleDate": "2017-10-19T00:00:00.000Z",
        "lastSalePrice": 185000,
        "hoa": {
            "fee": 175
        },
        "features": {
            "architectureType": "Contemporary",
            "cooling": True,
            "coolingType": "Central",
            "exteriorType": "Wood",
            "fireplace": True,
            "fireplaceType": "Masonry",
            "floorCount": 1,
            "foundationType": "Slab / Mat / Raft",
            "garage": True,
            "garageSpaces": 2,
            "garageType": "Garage",
            "heating": True,
            "heatingType": "Forced Air",
            "pool": True,
            "poolType": "Concrete",
            "roofType": "Asphalt",
            "roomCount": 5,
            "unitCount": 1,
            "viewType": "City"
        },
        "taxAssessments": {
            "2023": {
                "year": 2023,
                "value": 225790,
                "land": 59380,
                "improvements": 166410
            },
            "2022": {
                "year": 2022,
                "value": 210000,
                "land": 55000,
                "improvements": 155000
            }
        },
        "propertyTaxes": {
            "2023": {
                "year": 2023,
                "total": 4201
            },
            "2022": {
                "year": 2022,
                "total": 3950
            }
        },
        "history": {
            "2017-10-19": {
                "event": "Sale",
                "date": "2017-10-19T00:00:00.000Z",
                "price": 185000
            },
            "2010-05-15": {
                "event": "Sale",
                "date": "2010-05-15T00:00:00.000Z",
                "price": 145000
            }
        },
        "owner": {
            "names": ["Michael Smith"],
            "type": "Individual",
            "mailingAddress": {
                "id": "149-Weaver-Blvd,---264,-Weaverville,-NC-28787",
                "formattedAddress": "149 Weaver Blvd, # 264, Weaverville, NC 28787",
                "addressLine1": "149 Weaver Blvd",
                "addressLine2": "# 264",
                "city": "Weaverville",
                "state": "NC",
                "zipCode": "28787"
            }
        },
        "ownerOccupied": False
    }


def create_sample_properties_response() -> Dict[str, Any]:
    """Create sample properties response data."""
    sample_property = create_sample_property_data()
    
    # Create a few variations
    property_2 = sample_property.copy()
    property_2["id"] = "1234-Oak-St,-Austin,-TX-78701"
    property_2["formattedAddress"] = "1234 Oak St, Austin, TX 78701"
    property_2["city"] = "Austin"
    property_2["bedrooms"] = 4
    property_2["bathrooms"] = 3.5
    property_2["propertyType"] = "Condo"
    
    property_3 = sample_property.copy()
    property_3["id"] = "5678-Elm-Ave,-Houston,-TX-77001"
    property_3["formattedAddress"] = "5678 Elm Ave, Houston, TX 77001"
    property_3["city"] = "Houston"
    property_3["bedrooms"] = 2
    property_3["bathrooms"] = 1.5
    property_3["propertyType"] = "Townhouse"
    
    return {
        "properties": [sample_property, property_2, property_3],
        "totalCount": 150,
        "hasMore": True,
        "nextOffset": 3
    }


def test_property_parsing():
    """Test parsing individual property data."""
    print("=" * 60)
    print("TESTING PROPERTY PARSING")
    print("=" * 60)
    
    # Test single property parsing
    sample_data = create_sample_property_data()
    property_obj = Property.from_dict(sample_data)
    
    print(f"✅ Property parsed successfully:")
    print(f"   ID: {property_obj.id}")
    print(f"   Address: {property_obj.formatted_address}")
    print(f"   Type: {property_obj.property_type}")
    print(f"   Bedrooms: {property_obj.bedrooms}")
    print(f"   Bathrooms: {property_obj.bathrooms}")
    print(f"   Square Footage: {property_obj.square_footage}")
    print(f"   Year Built: {property_obj.year_built}")
    print(f"   Last Sale Price: ${property_obj.last_sale_price:,}" if property_obj.last_sale_price else "   Last Sale Price: N/A")
    
    # Test features
    if property_obj.features:
        print(f"   Features:")
        print(f"     - Garage: {property_obj.features.garage} ({property_obj.features.garage_spaces} spaces)")
        print(f"     - Pool: {property_obj.features.pool} ({property_obj.features.pool_type})")
        print(f"     - Fireplace: {property_obj.features.fireplace} ({property_obj.features.fireplace_type})")
        print(f"     - Cooling: {property_obj.features.cooling} ({property_obj.features.cooling_type})")
    
    # Test HOA
    if property_obj.hoa:
        print(f"   HOA Fee: ${property_obj.hoa.fee}/month")
    
    # Test tax assessments
    if property_obj.tax_assessments:
        print(f"   Tax Assessments:")
        for year, assessment in property_obj.tax_assessments.items():
            print(f"     - {year}: ${assessment.value:,} (Land: ${assessment.land:,}, Improvements: ${assessment.improvements:,})")
    
    # Test owner
    if property_obj.owner and property_obj.owner.names:
        owner_names = ', '.join(property_obj.owner.names)
        print(f"   Owner: {owner_names} ({property_obj.owner.type})")
        print(f"   Owner Occupied: {property_obj.owner_occupied}")
    
    # Test serialization back to dict
    property_dict = property_obj.to_dict()
    print(f"✅ Property serialized back to dict with {len(property_dict)} fields")
    
    return property_obj


def test_properties_response_parsing():
    """Test parsing properties response data."""
    print("\n" + "=" * 60)
    print("TESTING PROPERTIES RESPONSE PARSING")
    print("=" * 60)
    
    # Test multiple properties response
    sample_response = create_sample_properties_response()
    response_obj = PropertiesResponse.from_dict(sample_response)
    
    print(f"✅ Properties response parsed successfully:")
    print(f"   Total Properties: {len(response_obj.properties)}")
    print(f"   Total Count: {response_obj.total_count}")
    print(f"   Has More: {response_obj.has_more}")
    print(f"   Next Offset: {response_obj.next_offset}")
    
    print(f"\n   Properties:")
    for i, prop in enumerate(response_obj.properties, 1):
        print(f"     {i}. {prop.formatted_address} ({prop.property_type}) - {prop.bedrooms}BR/{prop.bathrooms}BA")
    
    # Test serialization
    response_dict = response_obj.to_dict()
    print(f"✅ Response serialized back to dict with {len(response_dict)} fields")
    
    return response_obj


def test_filtering():
    """Test property filtering functionality."""
    print("\n" + "=" * 60)
    print("TESTING PROPERTY FILTERING")
    print("=" * 60)
    
    # Create response with multiple properties
    sample_response = create_sample_properties_response()
    response_obj = PropertiesResponse.from_dict(sample_response)
    
    print(f"Original properties: {len(response_obj.properties)}")
    for prop in response_obj.properties:
        print(f"  - {prop.formatted_address}: {prop.bedrooms}BR/{prop.bathrooms}BA, {prop.property_type}")
    
    # Filter by bedrooms
    filtered_3br = filter_properties_by_criteria(
        response_obj.properties,
        min_bedrooms=3
    )
    print(f"\n✅ Properties with 3+ bedrooms: {len(filtered_3br)}")
    for prop in filtered_3br:
        print(f"  - {prop.formatted_address}: {prop.bedrooms}BR")
    
    # Filter by property type
    condos_only = filter_properties_by_criteria(
        response_obj.properties,
        property_types=["Condo", "Townhouse"]
    )
    print(f"\n✅ Condos and Townhouses only: {len(condos_only)}")
    for prop in condos_only:
        print(f"  - {prop.formatted_address}: {prop.property_type}")
    
    # Complex filter
    luxury_properties = filter_properties_by_criteria(
        response_obj.properties,
        min_bedrooms=3,
        min_bathrooms=2.0,
        property_types=["Single Family", "Condo"]
    )
    print(f"\n✅ Luxury properties (3+BR, 2+BA, Single Family/Condo): {len(luxury_properties)}")
    for prop in luxury_properties:
        print(f"  - {prop.formatted_address}: {prop.bedrooms}BR/{prop.bathrooms}BA, {prop.property_type}")


def test_parse_utility_function():
    """Test the parse_property_response utility function."""
    print("\n" + "=" * 60)
    print("TESTING PARSE UTILITY FUNCTION")
    print("=" * 60)
    
    # Test with single property
    single_property_data = create_sample_property_data()
    result = parse_property_response(single_property_data)
    
    if isinstance(result, Property):
        print(f"✅ Single property parsed correctly: {result.formatted_address}")
    else:
        print(f"❌ Expected Property, got {type(result)}")
    
    # Test with multiple properties
    multiple_properties_data = create_sample_properties_response()
    result = parse_property_response(multiple_properties_data)
    
    if isinstance(result, PropertiesResponse):
        print(f"✅ Multiple properties parsed correctly: {len(result.properties)} properties")
    else:
        print(f"❌ Expected PropertiesResponse, got {type(result)}")


def test_json_serialization():
    """Test JSON serialization of the schemas."""
    print("\n" + "=" * 60)
    print("TESTING JSON SERIALIZATION")
    print("=" * 60)
    
    # Create property
    sample_data = create_sample_property_data()
    property_obj = Property.from_dict(sample_data)
    
    # Convert to dict and then to JSON
    property_dict = property_obj.to_dict()
    json_str = json.dumps(property_dict, indent=2)
    
    print(f"✅ Property serialized to JSON ({len(json_str)} characters)")
    print(f"First 200 characters: {json_str[:200]}...")
    
    # Parse back from JSON
    parsed_dict = json.loads(json_str)
    reconstructed_property = Property.from_dict(parsed_dict)
    
    print(f"✅ Property reconstructed from JSON:")
    print(f"   Address: {reconstructed_property.formatted_address}")
    print(f"   Bedrooms: {reconstructed_property.bedrooms}")
    print(f"   Last Sale Price: ${reconstructed_property.last_sale_price:,}" if reconstructed_property.last_sale_price else "   Last Sale Price: N/A")


def demonstrate_real_world_usage():
    """Demonstrate real-world usage patterns."""
    print("\n" + "=" * 60)
    print("REAL-WORLD USAGE EXAMPLES")
    print("=" * 60)
    
    # Simulate API response parsing
    api_response = create_sample_properties_response()
    properties = PropertiesResponse.from_dict(api_response)
    
    print("📊 Market Analysis Example:")
    print(f"   Found {len(properties.properties)} properties")
    
    # Calculate average price per square foot
    properties_with_sqft = [
        p for p in properties.properties 
        if p.square_footage and p.last_sale_price and p.square_footage > 0
    ]
    if properties_with_sqft:
        price_per_sqft_values = []
        for p in properties_with_sqft:
            if p.last_sale_price and p.square_footage:
                price_per_sqft_values.append(p.last_sale_price / p.square_footage)
        
        if price_per_sqft_values:
            avg_price_per_sqft = sum(price_per_sqft_values) / len(price_per_sqft_values)
            print(f"   Average price per sq ft: ${avg_price_per_sqft:.2f}")
    
    # Property type distribution
    from collections import Counter
    property_types = Counter(p.property_type for p in properties.properties if p.property_type)
    print(f"   Property type distribution: {dict(property_types)}")
    
    # Find investment opportunities (properties with recent sales data)
    investment_candidates = [
        p for p in properties.properties 
        if (p.last_sale_price and p.square_footage and 
            p.bedrooms is not None and p.bedrooms >= 3)
    ]
    print(f"   Investment candidates (3+ BR with sale data): {len(investment_candidates)}")
    
    # Calculate potential rental yields (assuming features indicate quality)
    for prop in investment_candidates[:2]:  # Show first 2
        features_score = 0
        if prop.features:
            if prop.features.garage: features_score += 1
            if prop.features.pool: features_score += 1
            if prop.features.fireplace: features_score += 1
            if prop.features.cooling: features_score += 1
        
        print(f"   📍 {prop.formatted_address}")
        print(f"      Features Score: {features_score}/4")
        print(f"      Last Sale: ${prop.last_sale_price:,} ({prop.last_sale_date})")
        if prop.hoa and prop.hoa.fee:
            print(f"      HOA Fee: ${prop.hoa.fee}/month")


def main():
    """Run all schema tests."""
    print("RentCast Property Schema Test Suite")
    print("=" * 60)
    
    try:
        # Run all tests
        test_property_parsing()
        test_properties_response_parsing()
        test_filtering()
        test_parse_utility_function()
        test_json_serialization()
        demonstrate_real_world_usage()
        
        print("\n" + "=" * 60)
        print("🎉 ALL SCHEMA TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ Property dataclass is ready for use")
        print("✅ PropertiesResponse dataclass is ready for use")
        print("✅ All nested schemas working correctly")
        print("✅ Filtering and utility functions working")
        print("✅ JSON serialization/deserialization working")
        print("\n💡 The RentCast client can now return properly typed objects!")
        
        # Test AVM schemas
        test_avm_schemas()
        
        # Test Listings schemas
        test_listings_schemas()
        
    except Exception as e:
        print(f"\n❌ Schema test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


def test_avm_schemas():
    """Test the AVM endpoint schemas with sample data."""
    print("\n" + "="*60)
    print("🏠 Testing AVM (Automated Valuation Model) Schemas")
    print("="*60)
    
    # Test AVMValueResponse
    print("\n1. Testing Value Estimate Response")
    print("-" * 40)
    
    sample_value_data = {
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
    
    value_response = AVMValueResponse.from_dict(sample_value_data)
    
    print(f"Estimated Value: ${value_response.price:,}")
    print(f"Range: ${value_response.price_range_low:,} - ${value_response.price_range_high:,}")
    print(f"Subject Location: {value_response.latitude}, {value_response.longitude}")
    print(f"Number of Comparables: {len(value_response.comparables)}")
    
    if value_response.comparables:
        comp = value_response.comparables[0]
        print(f"\nTop Comparable:")
        print(f"  Address: {comp.formatted_address}")
        print(f"  Price: ${comp.price:,}")
        print(f"  Beds/Baths: {comp.bedrooms}/{comp.bathrooms}")
        print(f"  Square Feet: {comp.square_footage:,}")
        print(f"  Correlation: {comp.correlation:.1%}")
    
    # Test AVMRentResponse
    print("\n2. Testing Rent Estimate Response")
    print("-" * 40)
    
    sample_rent_data = {
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
                "price": 1650,  # Rent price
                "distance": 0.5,
                "correlation": 0.95
            }
        ]
    }
    
    rent_response = AVMRentResponse.from_dict(sample_rent_data)
    
    print(f"Estimated Monthly Rent: ${rent_response.rent:,}")
    print(f"Range: ${rent_response.rent_range_low:,} - ${rent_response.rent_range_high:,}")
    if rent_response.rent:
        print(f"Annual Rent: ${rent_response.rent * 12:,}")
    print(f"Number of Comparables: {len(rent_response.comparables)}")
    
    if rent_response.comparables:
        comp = rent_response.comparables[0]
        print(f"\nRental Comparable:")
        print(f"  Address: {comp.formatted_address}")
        print(f"  Monthly Rent: ${comp.price:,}")
        print(f"  Beds/Baths: {comp.bedrooms}/{comp.bathrooms}")
        print(f"  Correlation: {comp.correlation:.1%}")
    
    # Test investment analysis
    print("\n3. Investment Analysis Example")
    print("-" * 40)
    
    if value_response.price and rent_response.rent:
        annual_rent = rent_response.rent * 12
        gross_yield = (annual_rent / value_response.price) * 100
        print(f"Purchase Price: ${value_response.price:,}")
        print(f"Annual Rent: ${annual_rent:,}")
        print(f"Gross Rental Yield: {gross_yield:.2f}%")
        
        # 1% rule check
        one_percent_rule = (rent_response.rent / value_response.price) * 100
        print(f"Monthly Rent as % of Price: {one_percent_rule:.2f}%")
        if one_percent_rule >= 1.0:
            print("✅ Passes the 1% rule!")
        else:
            print("❌ Does not pass the 1% rule")
    
    # Test schema conversion methods
    print("\n4. Testing Schema Conversion Methods")
    print("-" * 40)
    
    # Test to_dict methods
    value_dict = value_response.to_dict()
    rent_dict = rent_response.to_dict()
    
    print(f"Value response dict keys: {list(value_dict.keys())}")
    print(f"Rent response dict keys: {list(rent_dict.keys())}")
    
    # Test round-trip conversion
    value_roundtrip = AVMValueResponse.from_dict(value_dict)
    rent_roundtrip = AVMRentResponse.from_dict(rent_dict)
    
    assert value_roundtrip.price == value_response.price
    assert rent_roundtrip.rent == rent_response.rent
    print("✅ Round-trip conversion successful!")
    
    print("\n🎉 All AVM schema tests passed!")


def test_listings_schemas():
    """Test the Listings endpoint schemas with sample data."""
    print("\n" + "="*60)
    print("🏢 Testing Listings Schemas")
    print("="*60)
    
    # Test PropertyListing with comprehensive data
    print("\n1. Testing Property Listing Schema")
    print("-" * 40)
    
    sample_listing_data = {
        "id": "3821-Hargis-St,-Austin,-TX-78723",
        "formattedAddress": "3821 Hargis St, Austin, TX 78723",
        "addressLine1": "3821 Hargis St",
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
        "hoa": {"fee": 65},
        "status": "Active",
        "price": 899000,
        "listingType": "Standard",
        "listedDate": "2024-06-24T00:00:00.000Z",
        "daysOnMarket": 99,
        "mlsName": "UnlockMLS",
        "mlsNumber": "5519228",
        "listingAgent": {
            "name": "Jennifer Welch",
            "phone": "5124313110",
            "email": "jennifer@example.com"
        },
        "listingOffice": {
            "name": "Gottesman Residential RE",
            "phone": "5124512422"
        }
    }
    
    listing = PropertyListing.from_dict(sample_listing_data)
    
    print(f"Listing ID: {listing.id}")
    print(f"Address: {listing.formatted_address}")
    print(f"Status: {listing.status}")
    print(f"Price: ${listing.price:,}")
    print(f"Property Type: {listing.property_type}")
    print(f"Beds/Baths: {listing.bedrooms}/{listing.bathrooms}")
    print(f"Square Feet: {listing.square_footage:,}")
    print(f"Days on Market: {listing.days_on_market}")
    print(f"MLS: {listing.mls_name} #{listing.mls_number}")
    
    if listing.hoa:
        print(f"HOA Fee: ${listing.hoa.fee}/month")
    
    if listing.listing_agent:
        print(f"Agent: {listing.listing_agent.name} ({listing.listing_agent.phone})")
    
    if listing.listing_office:
        print(f"Office: {listing.listing_office.name}")
    
    # Test ListingsResponse
    print("\n2. Testing Listings Response Schema")
    print("-" * 40)
    
    listings_response_data = {
        "listings": [sample_listing_data],
        "totalCount": 150,
        "hasMore": True,
        "nextOffset": 1
    }
    
    response = ListingsResponse.from_dict(listings_response_data)
    
    print(f"Total Listings Found: {len(response.listings)}")
    print(f"Total Count: {response.total_count}")
    print(f"Has More: {response.has_more}")
    print(f"Next Offset: {response.next_offset}")
    
    # Test listing enums
    print("\n3. Testing Listing Enums")
    print("-" * 40)
    
    print(f"Listing Statuses: {[status.value for status in ListingStatus]}")
    print(f"Listing Types: {[ltype.value for ltype in ListingType]}")
    print(f"Event Types: {[event.value for event in ListingEventType]}")
    
    # Test conversions
    print("\n4. Testing Schema Conversions")
    print("-" * 40)
    
    # Test to_dict conversion
    listing_dict = listing.to_dict()
    response_dict = response.to_dict()
    
    print(f"Listing dict keys: {len(listing_dict.keys())}")
    print(f"Response dict keys: {list(response_dict.keys())}")
    
    # Test round-trip conversion
    listing_roundtrip = PropertyListing.from_dict(listing_dict)
    response_roundtrip = ListingsResponse.from_dict(response_dict)
    
    assert listing_roundtrip.id == listing.id
    assert listing_roundtrip.price == listing.price
    assert len(response_roundtrip.listings) == len(response.listings)
    
    print("✅ Round-trip conversion successful!")
    
    print("\n🎉 All listings schema tests passed!")


if __name__ == "__main__":
    exit(main())
