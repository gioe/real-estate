# RentCast Markets Endpoint Schema Documentation

This document provides comprehensive documentation for the RentCast Markets endpoint schemas, showing how to use the Python dataclasses to handle market statistics data.

## Overview

The Markets endpoint schemas provide complete market statistics for both sales and rental data in a specific zip code, including:

- Current market statistics (averages, medians, min/max values)
- Breakdowns by property type and bedroom count
- Historical data with monthly breakdowns
- Price and rent per square foot metrics
- Days on market statistics
- Listing counts (new and total)

## Schema Hierarchy

```
MarketStatistics
├── id (str)
├── zip_code (str)  
├── sale_data (MarketSaleData)
│   ├── Current statistics (SaleStatistics fields)
│   ├── data_by_property_type (List[SaleDataByPropertyType])
│   ├── data_by_bedrooms (List[SaleDataByBedrooms])
│   └── history (Dict[str, SaleHistoryEntry])
└── rental_data (MarketRentalData)
    ├── Current statistics (RentalStatistics fields)
    ├── data_by_property_type (List[RentalDataByPropertyType])
    ├── data_by_bedrooms (List[RentalDataByBedrooms])
    └── history (Dict[str, RentalHistoryEntry])
```

## Core Schemas

### MarketStatistics

The main response container for market data:

```python
from src.rentcast_schemas import MarketStatistics

# Parse API response
market_data = {
    "id": "market_12345",
    "zipCode": "90210",
    "saleData": {
        "lastUpdatedDate": "2024-07-15T10:30:00.000Z",
        "averagePrice": 450000.0,
        "medianPrice": 425000.0,
        "totalListings": 150,
        # ... other sale statistics
    },
    "rentalData": {
        "lastUpdatedDate": "2024-07-15T10:30:00.000Z", 
        "averageRent": 2500.0,
        "medianRent": 2400.0,
        "totalListings": 95,
        # ... other rental statistics
    }
}

market_stats = MarketStatistics.from_dict(market_data)
print(f"Market statistics for {market_stats.zip_code}")
print(f"Average sale price: ${market_stats.sale_data.average_price:,}")
print(f"Average rent: ${market_stats.rental_data.average_rent:,}")
```

### Sale and Rental Statistics

Base statistics classes that contain all the core metrics:

```python
# Sale statistics include:
sale_stats = market_stats.sale_data
print(f"Average price: ${sale_stats.average_price:,}")
print(f"Price per sq ft: ${sale_stats.average_price_per_square_foot}/sq ft")
print(f"Days on market: {sale_stats.average_days_on_market} days")
print(f"New listings: {sale_stats.new_listings}")

# Rental statistics include:
rental_stats = market_stats.rental_data  
print(f"Average rent: ${rental_stats.average_rent:,}")
print(f"Rent per sq ft: ${rental_stats.average_rent_per_square_foot}/sq ft")
print(f"Days on market: {rental_stats.average_days_on_market} days")
```

## Breakdown Analysis

### Property Type Breakdowns

Analyze market data by property type:

```python
# Sale data by property type
for property_breakdown in market_stats.sale_data.data_by_property_type:
    print(f"\n{property_breakdown.property_type} Sales:")
    print(f"  Average price: ${property_breakdown.average_price:,}")
    print(f"  Median price: ${property_breakdown.median_price:,}")
    print(f"  Total listings: {property_breakdown.total_listings}")

# Rental data by property type  
for property_breakdown in market_stats.rental_data.data_by_property_type:
    print(f"\n{property_breakdown.property_type} Rentals:")
    print(f"  Average rent: ${property_breakdown.average_rent:,}")
    print(f"  Median rent: ${property_breakdown.median_rent:,}")
    print(f"  Total listings: {property_breakdown.total_listings}")
```

### Bedroom Count Breakdowns

Analyze market data by bedroom count:

```python
# Sale data by bedrooms
for bedroom_breakdown in market_stats.sale_data.data_by_bedrooms:
    print(f"\n{bedroom_breakdown.bedrooms} Bedroom Sales:")
    print(f"  Average price: ${bedroom_breakdown.average_price:,}")
    print(f"  Price range: ${bedroom_breakdown.min_price:,} - ${bedroom_breakdown.max_price:,}")
    print(f"  Total listings: {bedroom_breakdown.total_listings}")

# Rental data by bedrooms
for bedroom_breakdown in market_stats.rental_data.data_by_bedrooms:
    print(f"\n{bedroom_breakdown.bedrooms} Bedroom Rentals:")
    print(f"  Average rent: ${bedroom_breakdown.average_rent:,}")
    print(f"  Rent range: ${bedroom_breakdown.min_rent:,} - ${bedroom_breakdown.max_rent:,}")
    print(f"  Total listings: {bedroom_breakdown.total_listings}")
```

## Historical Analysis

Access and analyze historical market trends:

```python
# Analyze sale history
print("Sale Price History:")
for date_key, history_entry in market_stats.sale_data.history.items():
    print(f"\n{date_key}:")
    print(f"  Average price: ${history_entry.average_price:,}")
    print(f"  New listings: {history_entry.new_listings}")
    print(f"  Total listings: {history_entry.total_listings}")
    
    # Historical breakdowns by property type
    for breakdown in history_entry.data_by_property_type:
        print(f"    {breakdown.property_type}: ${breakdown.average_price:,}")

# Analyze rental history
print("\nRental Price History:")
for date_key, history_entry in market_stats.rental_data.history.items():
    print(f"\n{date_key}:")
    print(f"  Average rent: ${history_entry.average_rent:,}")
    print(f"  New listings: {history_entry.new_listings}")
    print(f"  Total listings: {history_entry.total_listings}")
```

## Advanced Usage Examples

### Market Comparison Analysis

```python
def analyze_market_trends(market_stats: MarketStatistics):
    """Analyze market trends and insights."""
    
    # Price metrics
    sale_data = market_stats.sale_data
    rental_data = market_stats.rental_data
    
    if sale_data and rental_data:
        # Calculate price-to-rent ratio
        if rental_data.average_rent and rental_data.average_rent > 0:
            monthly_rent = rental_data.average_rent
            annual_rent = monthly_rent * 12
            price_to_rent_ratio = sale_data.average_price / annual_rent
            print(f"Price-to-rent ratio: {price_to_rent_ratio:.1f}")
        
        # Market velocity comparison
        print(f"Sale market velocity: {sale_data.average_days_on_market:.1f} days")
        print(f"Rental market velocity: {rental_data.average_days_on_market:.1f} days")
        
        # Inventory analysis
        print(f"Sale inventory: {sale_data.total_listings} listings")
        print(f"Rental inventory: {rental_data.total_listings} listings")

# Use the analysis function
analyze_market_trends(market_stats)
```

### Historical Trend Detection

```python
def detect_price_trends(market_data: MarketSaleData):
    """Detect price trends from historical data."""
    
    if not market_data.history or len(market_data.history) < 2:
        return "Insufficient historical data"
    
    # Sort history by date
    sorted_history = sorted(
        market_data.history.items(), 
        key=lambda x: x[0]  # Sort by date key
    )
    
    # Calculate month-over-month change
    latest_price = sorted_history[-1][1].average_price
    previous_price = sorted_history[-2][1].average_price
    
    if latest_price and previous_price:
        change_pct = ((latest_price - previous_price) / previous_price) * 100
        trend = "increasing" if change_pct > 0 else "decreasing"
        print(f"Month-over-month price trend: {trend} ({change_pct:+.1f}%)")
        return trend, change_pct
    
    return "Unable to calculate trend"

# Analyze trends
if market_stats.sale_data:
    detect_price_trends(market_stats.sale_data)
```

### Property Type Performance

```python
def analyze_property_performance(market_data):
    """Analyze which property types are performing best."""
    
    if not market_data.sale_data or not market_data.sale_data.data_by_property_type:
        return
    
    # Sort property types by average price
    property_types = sorted(
        market_data.sale_data.data_by_property_type,
        key=lambda x: x.average_price or 0,
        reverse=True
    )
    
    print("Property Type Performance (by average price):")
    for i, prop_type in enumerate(property_types, 1):
        if prop_type.average_price:
            print(f"{i}. {prop_type.property_type}: ${prop_type.average_price:,}")
            print(f"   Listings: {prop_type.total_listings}")
            
            # Calculate price per listing as a market depth indicator
            if prop_type.total_listings and prop_type.total_listings > 0:
                depth_indicator = prop_type.average_price / prop_type.total_listings
                print(f"   Market depth: ${depth_indicator:,.0f} per listing")

analyze_property_performance(market_stats)
```

## Serialization and Storage

### Converting to/from dictionaries

```python
# Convert to dictionary for JSON serialization
market_dict = market_stats.to_dict()

# Save to JSON file
import json
with open('market_data.json', 'w') as f:
    json.dump(market_dict, f, indent=2)

# Load from JSON file
with open('market_data.json', 'r') as f:
    loaded_dict = json.load(f)

# Recreate MarketStatistics object
reloaded_market = MarketStatistics.from_dict(loaded_dict)
```

### Database Storage

```python
import sqlite3
import json

def store_market_data(market_stats: MarketStatistics, db_path: str):
    """Store market statistics in SQLite database."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_statistics (
            id TEXT PRIMARY KEY,
            zip_code TEXT,
            data_json TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert data
    cursor.execute('''
        INSERT OR REPLACE INTO market_statistics 
        (id, zip_code, data_json) VALUES (?, ?, ?)
    ''', (
        market_stats.id,
        market_stats.zip_code,
        json.dumps(market_stats.to_dict())
    ))
    
    conn.commit()
    conn.close()

# Store market data
store_market_data(market_stats, 'market_data.db')
```

## Error Handling

### Robust Data Processing

```python
def safe_market_analysis(market_dict: dict):
    """Safely process market data with error handling."""
    
    try:
        market_stats = MarketStatistics.from_dict(market_dict)
        
        # Check data availability
        if not market_stats.sale_data and not market_stats.rental_data:
            print("No market data available")
            return None
        
        if market_stats.sale_data:
            # Safely access sale data
            avg_price = market_stats.sale_data.average_price
            if avg_price:
                print(f"Average sale price: ${avg_price:,}")
            else:
                print("Sale price data not available")
        
        if market_stats.rental_data:
            # Safely access rental data
            avg_rent = market_stats.rental_data.average_rent
            if avg_rent:
                print(f"Average rent: ${avg_rent:,}")
            else:
                print("Rental price data not available")
        
        return market_stats
        
    except Exception as e:
        print(f"Error processing market data: {e}")
        return None

# Use safe processing
market_stats = safe_market_analysis(market_data_dict)
```

## Integration with RentCast Client

```python
from src.rentcast_client import RentCastClient
from src.rentcast_schemas import MarketStatistics

# Initialize client
client = RentCastClient(api_key="your_api_key")

# Fetch and parse market data
def get_market_statistics(zip_code: str) -> MarketStatistics:
    """Get market statistics for a zip code."""
    
    try:
        # Fetch raw data from API
        response = client.get_market_statistics(zip_code=zip_code)
        
        # Parse with schema
        market_stats = MarketStatistics.from_dict(response)
        
        print(f"Successfully retrieved market data for {zip_code}")
        print(f"Sale listings: {market_stats.sale_data.total_listings if market_stats.sale_data else 'N/A'}")
        print(f"Rental listings: {market_stats.rental_data.total_listings if market_stats.rental_data else 'N/A'}")
        
        return market_stats
        
    except Exception as e:
        print(f"Error fetching market data: {e}")
        raise

# Get market statistics
market_data = get_market_statistics("90210")
```

## All Available Fields

### Sale Statistics Fields
- `average_price`, `median_price`, `min_price`, `max_price`
- `average_price_per_square_foot`, `median_price_per_square_foot`, `min_price_per_square_foot`, `max_price_per_square_foot`
- `average_square_footage`, `median_square_footage`, `min_square_footage`, `max_square_footage`  
- `average_days_on_market`, `median_days_on_market`, `min_days_on_market`, `max_days_on_market`
- `new_listings`, `total_listings`
- `last_updated_date`

### Rental Statistics Fields
- `average_rent`, `median_rent`, `min_rent`, `max_rent`
- `average_rent_per_square_foot`, `median_rent_per_square_foot`, `min_rent_per_square_foot`, `max_rent_per_square_foot`
- `average_square_footage`, `median_square_footage`, `min_square_footage`, `max_square_footage`
- `average_days_on_market`, `median_days_on_market`, `min_days_on_market`, `max_days_on_market`
- `new_listings`, `total_listings`
- `last_updated_date`

### Breakdown Fields
- Property type breakdowns: All above statistics grouped by `property_type`
- Bedroom breakdowns: All above statistics grouped by `bedrooms` (string value)

### Historical Fields
- Monthly historical data with same structure as current statistics
- Includes breakdowns by property type and bedrooms for each month
- Date keys in format "YYYY-MM" (e.g., "2024-07")

This comprehensive schema system provides type-safe, validated access to all RentCast Markets endpoint data with full support for current statistics, breakdowns, and historical trends.
