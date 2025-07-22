# Pagination Support Documentation

## Overview

The Real Estate Analyzer now includes comprehensive pagination support for both API requests and database queries. This allows efficient handling of large datasets without memory or performance issues.

## Key Features

- **API Pagination**: Automatically handles paginated responses from RentCast API endpoints
- **Database Pagination**: Efficient querying of large database tables with offset/limit support
- **Flexible Configuration**: Configurable page sizes, limits, and pagination parameters
- **Error Handling**: Robust error handling and retry logic for paginated requests
- **Progress Tracking**: Built-in logging and progress tracking for long-running operations

## API Pagination

### Supported Endpoints

The following RentCast API endpoints support pagination:

- `/properties` - Property search results
- `/listings/sale` - Sale listings
- `/listings/rental/long-term` - Rental listings

### Classes and Methods

#### PaginationManager

Manages pagination for API requests.

```python
from src.core.data_fetcher import PaginationManager

# Initialize with custom settings
paginator = PaginationManager(
    default_limit=50,    # Default page size
    max_limit=500        # Maximum allowed page size
)

# Paginate through results
for page_response in paginator.paginate_request(client, 'properties', search_params):
    # Process each page
    properties = page_response.data
    print(f"Got {len(properties)} properties")
    
    if not page_response.has_more:
        break
```

#### APIResponse

Container for paginated API response data.

```python
@dataclass
class APIResponse:
    data: List[Dict[str, Any]]      # Page data
    total_count: Optional[int]       # Total available records
    has_more: bool                  # Whether more pages exist
    next_offset: Optional[int]       # Offset for next page
    source: Optional[str]           # Data source identifier
```

#### RealEstateDataFetcher Pagination Methods

```python
from src.core.data_fetcher import RealEstateDataFetcher

fetcher = RealEstateDataFetcher(api_config)

# Fetch properties page by page
search_params = {'city': 'Austin', 'state': 'TX', 'limit': 100}
for response in fetcher.fetch_properties_paginated(search_params, max_pages=5):
    properties = response.data
    print(f"Page has {len(properties)} properties")

# Fetch all properties (automatic pagination)
all_properties = fetcher.fetch_all_properties_paginated(search_params, max_pages=10)
print(f"Total properties fetched: {len(all_properties)}")

# Fetch listings
listing_params = {'city': 'Dallas', 'state': 'TX', 'limit': 50}
all_listings = fetcher.fetch_all_listings_paginated(
    search_params=listing_params,
    listing_type='sale',
    max_pages=None  # No limit
)
```

### Configuration

Configure pagination settings in your `config.yaml`:

```yaml
api:
  rentcast_api_key: "your_api_key"
  rentcast_endpoint: "https://api.rentcast.io/v1"
  rentcast_rate_limit: 100
  default_page_size: 50      # Default items per page
  max_page_size: 500         # Maximum items per page
  rentcast_search_params:
    locations: 
      - "Austin, TX"
      - "Dallas, TX"
    property_types: 
      - "Single Family"
      - "Condo"
    limit: 100               # Items per API request
```

## Database Pagination

### Classes and Methods

#### PaginationParams

Parameters for database pagination.

```python
from src.core.database import PaginationParams

# Create pagination parameters
pagination = PaginationParams(
    limit=25,    # Records per page (1-500)
    offset=0     # Starting record (0-based)
)

# Validation is automatic
try:
    bad_params = PaginationParams(limit=1000)  # Will raise ValueError
except ValueError as e:
    print(f"Invalid pagination: {e}")
```

#### PaginatedResult

Container for paginated database query results.

```python
@dataclass
class PaginatedResult:
    data: List[Dict[str, Any]]      # Query results
    total_count: int                # Total matching records
    limit: int                      # Page size used
    offset: int                     # Starting offset used
    has_more: bool                  # Whether more results exist
    next_offset: Optional[int]       # Offset for next page (if has_more)
```

#### DatabaseManager Pagination Methods

```python
from src.core.database import DatabaseManager, PaginationParams

db = DatabaseManager(db_config)

# Paginated property search
pagination = PaginationParams(limit=50, offset=0)
criteria = {
    'price': {'min': 200000, 'max': 800000},
    'bedrooms': {'min': 2},
    'cities': {'in': ['Austin', 'Houston']}
}

result = db.get_properties_paginated(pagination, criteria)
print(f"Got {len(result.data)} properties out of {result.total_count} total")

if result.has_more:
    # Fetch next page
    next_pagination = PaginationParams(limit=50, offset=result.next_offset)
    next_result = db.get_properties_paginated(next_pagination, criteria)

# Paginated recent properties
recent_pagination = PaginationParams(limit=20, offset=0)
recent_result = db.get_recent_properties_paginated(
    days=7,
    pagination=recent_pagination
)
```

### Usage Examples

#### Page Through All Results

```python
def fetch_all_properties_paged(db_manager, criteria):
    """Fetch all matching properties using pagination."""
    all_properties = []
    pagination = PaginationParams(limit=100, offset=0)
    
    while True:
        result = db_manager.get_properties_paginated(pagination, criteria)
        all_properties.extend(result.data)
        
        print(f"Fetched {len(result.data)} properties, total so far: {len(all_properties)}")
        
        if not result.has_more:
            break
        
        # Move to next page
        pagination.offset = result.next_offset
    
    return all_properties
```

#### Process Results in Batches

```python
def process_properties_in_batches(db_manager, criteria, batch_size=50):
    """Process properties in manageable batches."""
    pagination = PaginationParams(limit=batch_size, offset=0)
    
    while True:
        result = db_manager.get_properties_paginated(pagination, criteria)
        
        if not result.data:
            break
        
        # Process this batch
        process_property_batch(result.data)
        
        if not result.has_more:
            break
        
        pagination.offset = result.next_offset

def process_property_batch(properties):
    """Process a batch of properties."""
    for prop in properties:
        # Do something with each property
        analyze_property(prop)
```

## Best Practices

### API Pagination

1. **Respect Rate Limits**: Use appropriate delays between requests
   ```python
   # Built-in rate limiting in RentCastClient
   client = RentCastClient(api_key="key", rate_limit=100)
   ```

2. **Handle Errors Gracefully**: Paginated requests can fail partway through
   ```python
   try:
       for response in fetcher.fetch_properties_paginated(params):
           # Process response
           pass
   except RentCastClientError as e:
       logger.error(f"API error during pagination: {e}")
   ```

3. **Use Reasonable Page Sizes**: Balance between efficiency and memory usage
   ```python
   # Good: Reasonable page size
   params = {'city': 'Austin', 'state': 'TX', 'limit': 100}
   
   # Avoid: Too small (inefficient) or too large (memory issues)
   params = {'limit': 1}    # Too small
   params = {'limit': 1000} # Too large (exceeds API limit)
   ```

4. **Set Maximum Pages**: Prevent runaway requests
   ```python
   # Limit to prevent excessive API calls
   all_data = fetcher.fetch_all_properties_paginated(params, max_pages=50)
   ```

### Database Pagination

1. **Use Appropriate Page Sizes**: Consider your application's memory constraints
   ```python
   # For web applications
   pagination = PaginationParams(limit=20, offset=0)
   
   # For batch processing
   pagination = PaginationParams(limit=1000, offset=0)
   ```

2. **Add Indexes**: Ensure your database queries are optimized
   ```sql
   -- Indexes are automatically created for common fields
   CREATE INDEX idx_properties_city ON properties(city);
   CREATE INDEX idx_properties_price ON properties(price);
   ```

3. **Use Consistent Ordering**: Ensure predictable pagination results
   ```python
   # Database queries automatically ORDER BY created_at DESC
   # This ensures consistent pagination
   ```

4. **Handle Empty Results**: Check for empty pages
   ```python
   result = db.get_properties_paginated(pagination, criteria)
   if not result.data:
       print("No results found")
   ```

## Error Handling

### API Errors

```python
from src.api.http_client import HTTPClientError
from src.api.rentcast_client import RentCastClientError

try:
    for response in fetcher.fetch_properties_paginated(params):
        # Process response
        pass
except RentCastClientError as e:
    logger.error(f"RentCast API error: {e}")
except HTTPClientError as e:
    logger.error(f"HTTP client error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

### Database Errors

```python
try:
    result = db.get_properties_paginated(pagination, criteria)
except ValueError as e:
    logger.error(f"Invalid pagination parameters: {e}")
except Exception as e:
    logger.error(f"Database error: {e}")
```

## Performance Considerations

### Memory Usage

- **API Pagination**: Each page loads into memory temporarily
- **Database Pagination**: Only requested page is loaded into memory
- **Combined Results**: Use generators when possible to avoid loading everything at once

### Query Performance

- **Database Indexes**: Automatically created for common search fields
- **LIMIT/OFFSET**: Efficient for small-medium offsets; consider cursor-based pagination for very large datasets
- **Search Criteria**: More specific criteria = faster queries

### Rate Limiting

- **API Calls**: Built-in rate limiting respects API constraints
- **Database Queries**: No rate limiting needed for local databases

## Example Configuration

```yaml
# config/config.yaml
database:
  type: sqlite
  sqlite_path: data/real_estate.db

api:
  rentcast_enabled: true
  rentcast_api_key: "${RENTCAST_API_KEY}"
  rentcast_endpoint: "https://api.rentcast.io/v1"
  rentcast_rate_limit: 100
  default_page_size: 50
  max_page_size: 500
  
  rentcast_search_params:
    locations:
      - "Austin, TX"
      - "Dallas, TX" 
      - "Houston, TX"
    property_types:
      - "Single Family"
      - "Condo"
      - "Townhouse"
    limit: 100
```

## Testing

Run the pagination demo to test functionality:

```bash
python pagination_demo.py
```

This will demonstrate:
- API pagination with RentCast
- Database pagination queries  
- Combined API + Database workflow
