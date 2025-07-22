# Search Query System Documentation

The Real Estate Analyzer now includes a comprehensive search query system that supports all the search patterns available in the RentCast API. This system provides structured, type-safe ways to query for properties and listings.

## Overview

The search system supports three main types of searches:

1. **Specific Address Search** - Find data for a particular property address
2. **Location Search** - Find properties in a city, state, and/or zip code  
3. **Geographical Area Search** - Find properties within a radius of coordinates or an address

## Quick Start

```python
from src import RealEstateDataFetcher, SearchQueryBuilder
from src.config import ConfigManager

# Initialize
config_manager = ConfigManager()
fetcher = RealEstateDataFetcher(config_manager.get_api_config())

# Simple address search
properties = fetcher.search_by_address("5500 Grand Lake Dr, San Antonio, TX, 78244")

# Location search with filters
properties = fetcher.search_by_location(
    city="Austin",
    state="TX",
    bedrooms=3,
    bathrooms=2,
    min_price=300000,
    max_price=600000
)

# Geographical area search
properties = fetcher.search_by_coordinates(
    latitude=33.45141,
    longitude=-112.073827,
    radius=5,
    property_type="Single Family"
)
```

## Search Types

### 1. Specific Address Search

Used to retrieve data for a specific property address.

#### Usage
```python
from src.core.search_queries import SpecificAddressSearch, search_by_address

# Method 1: Convenience function
properties = fetcher.search_by_address("5500 Grand Lake Dr, San Antonio, TX, 78244")

# Method 2: Using search criteria class
search_criteria = SpecificAddressSearch(address="5500 Grand Lake Dr, San Antonio, TX, 78244")
properties = fetcher.search_properties_structured(search_criteria)
```

#### Important Notes
- Address should be in format: "Street, City, State, Zip"
- Returns data for that specific property only
- Most filters are ignored for specific address searches

### 2. Location Search

Search for properties in a specific city, state, and/or zip code.

#### Usage
```python
from src.core.search_queries import LocationSearch, search_by_location

# Method 1: Convenience function
properties = fetcher.search_by_location(
    city="Austin",
    state="TX",
    bedrooms=3,
    bathrooms=2,
    limit=10
)

# Method 2: Using search criteria class
search_criteria = LocationSearch(
    city="Austin",
    state="TX",
    property_type="Single Family",
    min_bedrooms=2,
    max_bedrooms=4,
    min_price=200000,
    max_price=500000
)
properties = fetcher.search_properties_structured(search_criteria)
```

#### Parameters
- `city`: City name (string)
- `state`: 2-character state abbreviation (e.g., 'TX', 'CA')
- `zip_code`: 5-digit zip code (string)
- At least one of city, state, or zip_code is required

### 3. Geographical Area Search

Search for properties within a radius of coordinates or an address.

#### Usage
```python
from src.core.search_queries import GeographicalAreaSearch, search_by_coordinates, search_around_address

# Method 1: Search by coordinates
properties = fetcher.search_by_coordinates(
    latitude=33.45141,
    longitude=-112.073827,
    radius=5,
    bedrooms=3,
    bathrooms=2
)

# Method 2: Search around an address
properties = fetcher.search_around_address(
    address="Times Square, New York, NY",
    radius=2,
    property_type="Condo",
    min_price=500000
)

# Method 3: Using search criteria class
search_criteria = GeographicalAreaSearch(
    center_address="Space Needle, Seattle, WA",
    radius=3,
    min_square_feet=1000,
    max_square_feet=3000
)
properties = fetcher.search_properties_structured(search_criteria)
```

#### Parameters
- Must provide either:
  - `latitude` and `longitude` (float values)
  - `center_address` (string)
- `radius`: Search radius in miles (float, default 5.0)

## Search Query Builder

For complex searches, use the SearchQueryBuilder for a fluent interface:

```python
# Create builder
builder = fetcher.create_search_builder()

# Build complex search
search_criteria = (builder
    .in_city_state("Denver", "CO")
    .with_property_type("Single Family")
    .with_bedrooms_range(min_bedrooms=3, max_bedrooms=5)
    .with_bathrooms_range(min_bathrooms=2)
    .with_price_range(min_price=400000, max_price=800000)
    .with_square_feet_range(min_square_feet=1500, max_square_feet=4000)
    .with_year_built_range(min_year=1990)
    .with_limit(20)
    .build())

# Execute search
properties = fetcher.search_properties_structured(search_criteria)
```

### Builder Methods

#### Location Methods
- `.for_address(address)` - Specific address search
- `.in_city(city)` - Search in city
- `.in_state(state)` - Search in state  
- `.in_zip_code(zip_code)` - Search in zip code
- `.in_city_state(city, state)` - Search in city and state
- `.within_radius(lat, lng, radius)` - Geographical search by coordinates
- `.around_address(address, radius)` - Geographical search around address

#### Property Filter Methods
- `.with_property_type(property_type)` - Filter by property type
- `.with_bedrooms(bedrooms)` - Exact bedroom count
- `.with_bedrooms_range(min_bedrooms, max_bedrooms)` - Bedroom range
- `.with_bathrooms(bathrooms)` - Exact bathroom count
- `.with_bathrooms_range(min_bathrooms, max_bathrooms)` - Bathroom range
- `.with_price_range(min_price, max_price)` - Price range
- `.with_square_feet_range(min_square_feet, max_square_feet)` - Square footage range
- `.with_year_built_range(min_year, max_year)` - Year built range

#### Pagination Methods  
- `.with_limit(limit)` - Result limit (1-500)
- `.with_offset(offset)` - Result offset

## Common Filters

All search types support these common filters:

### Property Characteristics
- `property_type`: Property type (use PropertyType enum or string)
- `bedrooms`: Exact bedroom count
- `bathrooms`: Exact bathroom count  
- `min_bedrooms` / `max_bedrooms`: Bedroom range
- `min_bathrooms` / `max_bathrooms`: Bathroom range
- `min_square_feet` / `max_square_feet`: Square footage range
- `min_lot_size` / `max_lot_size`: Lot size range
- `min_year_built` / `max_year_built`: Year built range

### Price Filters
- `min_price` / `max_price`: Price range

### Listing Filters (for listing searches)
- `min_days_on_market` / `max_days_on_market`: Days on market range
- `listing_type`: Type of listing

### Pagination
- `limit`: Maximum results per page (1-500, default 50)
- `offset`: Number of results to skip (default 0)

## Property Types

Use the PropertyType enum for consistent property type filtering:

```python
from src.core.search_queries import PropertyType

# Available property types:
PropertyType.SINGLE_FAMILY     # "Single Family"
PropertyType.CONDO             # "Condo"
PropertyType.TOWNHOUSE         # "Townhouse"
PropertyType.MULTI_FAMILY      # "Multi Family"
PropertyType.APARTMENT         # "Apartment"
PropertyType.MOBILE_HOME       # "Mobile Home"
PropertyType.MANUFACTURED      # "Manufactured"
PropertyType.LAND              # "Land"
PropertyType.COMMERCIAL        # "Commercial"
PropertyType.OTHER             # "Other"
```

## Listing Searches

The system also supports searching for listings (properties currently for sale or rent):

```python
# Sale listings
search_criteria = LocationSearch(city="Miami", state="FL", min_price=300000)
sale_listings = fetcher.search_listings_structured(search_criteria, listing_type='sale')

# Rental listings  
search_criteria = GeographicalAreaSearch(center_address="Austin, TX", radius=10)
rental_listings = fetcher.search_listings_structured(search_criteria, listing_type='rental')
```

## Error Handling

The search system includes comprehensive validation:

```python
# Invalid state abbreviation
try:
    search = LocationSearch(city="Boston", state="Massachusetts")  # Should be "MA"
except ValueError as e:
    print(f"Error: {e}")

# Invalid coordinates
try:
    search = GeographicalAreaSearch(latitude=100, longitude=200, radius=5)
except ValueError as e:
    print(f"Error: {e}")
```

## Pagination

All searches support pagination for large result sets:

```python
# Get first page
search_criteria = LocationSearch(city="Los Angeles", state="CA", limit=50, offset=0)
page1 = fetcher.search_properties_structured(search_criteria)

# Get second page
search_criteria.offset = 50
page2 = fetcher.search_properties_structured(search_criteria)
```

## Examples

### Find Luxury Homes in Specific Area
```python
builder = fetcher.create_search_builder()
luxury_search = (builder
    .around_address("Beverly Hills, CA", 5)
    .with_property_type(PropertyType.SINGLE_FAMILY)
    .with_bedrooms_range(min_bedrooms=4)
    .with_bathrooms_range(min_bathrooms=3)
    .with_price_range(min_price=2000000)
    .with_square_feet_range(min_square_feet=3000)
    .with_limit(25)
    .build())

luxury_homes = fetcher.search_properties_structured(luxury_search)
```

### Find Investment Properties
```python
investment_search = LocationSearch(
    city="Phoenix",
    state="AZ",
    property_type="Multi Family",
    min_price=300000,
    max_price=800000,
    min_year_built=1980,
    limit=30
)

investment_properties = fetcher.search_properties_structured(investment_search)
```

### Find Starter Homes Near Work
```python
starter_homes = fetcher.search_around_address(
    address="1600 Amphitheatre Parkway, Mountain View, CA",  # Google HQ
    radius=10,
    property_type="Single Family",
    bedrooms=3,
    max_price=1200000,
    min_year_built=1990
)
```

## Best Practices

1. **Use specific addresses in recommended format**: "Street, City, State, Zip"

2. **Use appropriate search types**:
   - Specific address for individual properties
   - Location search for city/state/zip queries
   - Geographical search for radius-based queries

3. **Apply reasonable filters**:
   - Use price ranges appropriate for the market
   - Don't over-constrain with too many filters

4. **Handle pagination for large results**:
   - Use limit and offset for large searches
   - Consider using the pagination system for bulk data fetching

5. **Use PropertyType enum** for consistent property type filtering

6. **Handle errors gracefully** with try/catch blocks for validation errors

7. **Test connection first** when using the API in production

## Integration with Existing System

The search functionality integrates seamlessly with the existing Real Estate Analyzer:

```python
# Use search results with analyzer
properties = fetcher.search_by_location(city="Austin", state="TX")
analyzer = RealEstateAnalyzer()
analysis = analyzer.analyze_properties(properties)

# Use search results with database
db = DatabaseManager()
db.save_properties(properties, source="RentCast_Search")

# Use search results with notifications
notification_manager = NotificationManager()
for prop in properties:
    if prop.get('price', 0) < 500000:  # Found a deal
        notification_manager.send_property_alert(prop)
```
