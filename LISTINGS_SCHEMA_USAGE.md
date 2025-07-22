# Listings Schema Usage Guide

This document explains how to use the new Listings schemas for the RentCast API `/listings` endpoint.

## Available Schemas

### PropertyListing
Complete schema for property listings (both sales and rentals) from the `/listings` endpoint.

```python
from src.rentcast_schemas import PropertyListing

# Example usage with API response
api_response = {
    "id": "3821-Hargis-St,-Austin,-TX-78723",
    "formattedAddress": "3821 Hargis St, Austin, TX 78723",
    "status": "Active",
    "price": 899000,
    "propertyType": "Single Family",
    "bedrooms": 4,
    "bathrooms": 2.5,
    "listingAgent": {
        "name": "Jennifer Welch",
        "phone": "5124313110"
    },
    # ... other fields
}

listing = PropertyListing.from_dict(api_response)
print(f"Listing: {listing.formatted_address}")
print(f"Price: ${listing.price:,}")
print(f"Status: {listing.status}")
print(f"Agent: {listing.listing_agent.name}")
```

### ListingsResponse  
Paginated response wrapper for multiple listings.

```python
from src.rentcast_schemas import ListingsResponse

# Example usage with API response
api_response = {
    "listings": [...],  # Array of listing objects
    "totalCount": 250,
    "hasMore": True,
    "nextOffset": 10
}

response = ListingsResponse.from_dict(api_response)
print(f"Found {len(response.listings)} listings")
print(f"Total available: {response.total_count}")

for listing in response.listings:
    print(f"  {listing.formatted_address} - ${listing.price:,}")
```

### Supporting Schemas

#### ListingAgent
```python
from src.rentcast_schemas import ListingAgent

agent = listing.listing_agent
if agent:
    print(f"Agent: {agent.name}")
    print(f"Phone: {agent.phone}")
    print(f"Email: {agent.email}")
```

#### ListingOffice
```python
from src.rentcast_schemas import ListingOffice

office = listing.listing_office
if office:
    print(f"Office: {office.name}")
    print(f"Phone: {office.phone}")
```

#### Builder (New Construction)
```python
from src.rentcast_schemas import Builder

if listing.builder:
    print(f"Builder: {listing.builder.name}")
    print(f"Development: {listing.builder.development}")
```

#### ListingHistoryEntry
```python
# Access listing history
for date, history in listing.history.items():
    print(f"{date}: {history.event}")
    print(f"  Price: ${history.price:,}")
    print(f"  Days on Market: {history.days_on_market}")
```

## Field Reference

### Core Listing Fields
- **Basic Info**: `id`, `formatted_address`, `city`, `state`, `zip_code`, `county`
- **Location**: `latitude`, `longitude`
- **Property Details**: `property_type`, `bedrooms`, `bathrooms`, `square_footage`, `lot_size`, `year_built`
- **Listing Info**: `status`, `price`, `listing_type`, `days_on_market`
- **Dates**: `listed_date`, `removed_date`, `created_date`, `last_seen_date`
- **MLS**: `mls_name`, `mls_number`

### Nested Objects
- **`hoa`**: HOA fee information
- **`listing_agent`**: Agent contact details
- **`listing_office`**: Office/broker information  
- **`builder`**: New construction builder details
- **`history`**: Dictionary of historical listing entries

## Enumerations

### ListingStatus
- `ACTIVE`: Currently listed on market
- `INACTIVE`: Not currently listed

### ListingType
- `STANDARD`: Regular listing
- `NEW_CONSTRUCTION`: Recently built property
- `FORECLOSURE`: Foreclosure sale
- `SHORT_SALE`: Short sale process

### ListingEventType  
- `SALE_LISTING`: Sale listing event
- `RENTAL_LISTING`: Rental listing event

## Usage Examples

### Finding Active Listings
```python
active_listings = [
    listing for listing in response.listings 
    if listing.status == "Active"
]
```

### Filtering by Price Range
```python
def filter_by_price(listings, min_price=None, max_price=None):
    filtered = listings
    if min_price:
        filtered = [l for l in filtered if l.price and l.price >= min_price]
    if max_price:
        filtered = [l for l in filtered if l.price and l.price <= max_price]
    return filtered

affordable_homes = filter_by_price(response.listings, max_price=500000)
```

### Analyzing Market Activity
```python
# Calculate average days on market
active_listings = [l for l in response.listings if l.status == "Active"]
avg_dom = sum(l.days_on_market for l in active_listings if l.days_on_market) / len(active_listings)
print(f"Average days on market: {avg_dom:.0f}")

# Group by property type
from collections import Counter
type_counts = Counter(l.property_type for l in response.listings if l.property_type)
print("Property type distribution:", dict(type_counts))
```

### Agent Performance Analysis
```python
# Find top agents by listing count
from collections import Counter
agent_counts = Counter(
    l.listing_agent.name for l in response.listings 
    if l.listing_agent and l.listing_agent.name
)
top_agents = agent_counts.most_common(5)
print("Top agents by listing count:")
for agent, count in top_agents:
    print(f"  {agent}: {count} listings")
```

### New Construction Analysis
```python
new_construction = [
    l for l in response.listings 
    if l.listing_type == "New Construction"
]

if new_construction:
    print(f"Found {len(new_construction)} new construction listings")
    
    # Group by builder
    builder_counts = Counter(
        l.builder.name for l in new_construction 
        if l.builder and l.builder.name
    )
    
    print("Builders:")
    for builder, count in builder_counts.items():
        print(f"  {builder}: {count} listings")
```

### Price History Analysis
```python
def analyze_price_history(listing):
    """Analyze price changes over time."""
    if not listing.history:
        return "No price history available"
    
    prices = []
    for date, history in sorted(listing.history.items()):
        if history.price:
            prices.append((date, history.price))
    
    if len(prices) < 2:
        return "Insufficient price history"
    
    initial_price = prices[0][1]
    current_price = prices[-1][1]
    change = current_price - initial_price
    percent_change = (change / initial_price) * 100
    
    return f"Price change: ${change:,} ({percent_change:+.1f}%)"
```

## Error Handling

Always check for None values when accessing optional fields:

```python
listing = PropertyListing.from_dict(api_data)

# Safe access to optional fields
if listing.price is not None:
    print(f"Price: ${listing.price:,}")
else:
    print("Price not available")

# Safe access to nested objects
if listing.listing_agent:
    agent_name = listing.listing_agent.name or "Unknown"
    print(f"Agent: {agent_name}")

# Safe iteration over history
if listing.history:
    for date, entry in listing.history.items():
        if entry.price:
            print(f"{date}: ${entry.price:,}")
```

## Integration Notes

The listings schemas work seamlessly with:

1. **Database Storage**: Use `to_dict()` method for database insertion
2. **API Responses**: Use `from_dict()` method to parse API responses  
3. **Data Analysis**: All fields are properly typed for analysis functions
4. **Filtering**: Compatible with existing property filtering utilities
5. **Serialization**: Full JSON serialization support for caching

The schemas handle all edge cases including missing fields, empty responses, and various response formats from the RentCast listings API.
