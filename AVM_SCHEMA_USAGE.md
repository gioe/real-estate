# AVM Schema Usage Guide

This document explains how to use the new AVM (Automated Valuation Model) schemas for the RentCast API endpoints.

## Available Schemas

### AVMValueResponse
Used for property value estimates from the `/avm/value` endpoint.

```python
from src.rentcast_schemas import AVMValueResponse

# Example usage with API response
api_response = {
    "price": 221000,
    "priceRangeLow": 208000,
    "priceRangeHigh": 233000,
    "latitude": 29.475962,
    "longitude": -98.351442,
    "comparables": [...]
}

value_estimate = AVMValueResponse.from_dict(api_response)
print(f"Estimated value: ${value_estimate.price:,}")
print(f"Range: ${value_estimate.price_range_low:,} - ${value_estimate.price_range_high:,}")
```

### AVMRentResponse
Used for property rent estimates from the `/avm/rent/long-term` endpoint.

```python
from src.rentcast_schemas import AVMRentResponse

# Example usage with API response
api_response = {
    "rent": 1670,
    "rentRangeLow": 1630,
    "rentRangeHigh": 1710,
    "latitude": 29.475962,
    "longitude": -98.351442,
    "comparables": [...]
}

rent_estimate = AVMRentResponse.from_dict(api_response)
print(f"Estimated monthly rent: ${rent_estimate.rent:,}")
print(f"Range: ${rent_estimate.rent_range_low:,} - ${rent_estimate.rent_range_high:,}")
```

### Comparable
Represents comparable properties used in AVM calculations.

```python
from src.rentcast_schemas import Comparable

# Access comparable properties
for comp in value_estimate.comparables:
    print(f"Comparable: {comp.formatted_address}")
    print(f"  Price: ${comp.price:,}")
    print(f"  Beds: {comp.bedrooms}, Baths: {comp.bathrooms}")
    print(f"  Square Footage: {comp.square_footage:,}")
    print(f"  Distance: {comp.distance} miles")
    print(f"  Correlation: {comp.correlation * 100:.1f}%")
```

## Field Descriptions

### AVMValueResponse Fields
- `price`: Estimated property value
- `price_range_low`: Lower boundary of estimate (85% confidence)
- `price_range_high`: Upper boundary of estimate (85% confidence)
- `latitude`/`longitude`: Subject property location
- `comparables`: List of comparable properties used

### AVMRentResponse Fields
- `rent`: Estimated monthly rent
- `rent_range_low`: Lower boundary of rent estimate (85% confidence)
- `rent_range_high`: Upper boundary of rent estimate (85% confidence)
- `latitude`/`longitude`: Subject property location
- `comparables`: List of comparable rental properties used

### Comparable Fields
- Basic property info: `id`, `formatted_address`, `city`, `state`, `zip_code`
- Property characteristics: `bedrooms`, `bathrooms`, `square_footage`, `lot_size`, `year_built`
- Listing information: `price`, `listing_type`, `days_on_market`
- Analysis metrics: `distance`, `correlation`, `days_old`

## Integration Examples

### Analyzing Value vs Rent Potential
```python
# Get both value and rent estimates
value_response = AVMValueResponse.from_dict(value_api_data)
rent_response = AVMRentResponse.from_dict(rent_api_data)

# Calculate potential returns
estimated_value = value_response.price
estimated_rent = rent_response.rent
annual_rent = estimated_rent * 12

if estimated_value and annual_rent:
    gross_yield = (annual_rent / estimated_value) * 100
    print(f"Gross rental yield: {gross_yield:.2f}%")
```

### Finding Best Comparables
```python
# Sort comparables by correlation (similarity)
best_comps = sorted(value_response.comparables, 
                   key=lambda x: x.correlation or 0, 
                   reverse=True)

print("Top 3 most similar properties:")
for comp in best_comps[:3]:
    print(f"  {comp.formatted_address} - {comp.correlation:.1%} similar")
```

## Error Handling

Always check for None values when working with optional fields:

```python
value_response = AVMValueResponse.from_dict(api_data)

if value_response.price is not None:
    print(f"Estimated value: ${value_response.price:,}")
else:
    print("No value estimate available")

# Check comparables exist
if value_response.comparables:
    avg_price = sum(comp.price for comp in value_response.comparables if comp.price) / len(value_response.comparables)
    print(f"Average comparable price: ${avg_price:,}")
```
