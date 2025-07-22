# Source Code Organization

## Directory Structure

The `src/` directory has been reorganized into logical subdirectories for better maintainability and code organization:

```
src/
├── __init__.py                    # Main package init with convenience imports
├── api/                          # API clients and HTTP communication
│   ├── __init__.py
│   ├── http_client.py           # Base HTTP client with rate limiting
│   └── rentcast_client.py       # RentCast API specific client
├── config/                       # Configuration management  
│   ├── __init__.py
│   └── config_manager.py        # YAML/JSON configuration handling
├── core/                         # Core business logic
│   ├── __init__.py
│   ├── data_analyzer.py         # Real estate data analysis
│   ├── data_fetcher.py          # Multi-source data fetching
│   └── database.py              # Database operations (SQLite/PostgreSQL)
├── notifications/                # Alert and notification system
│   ├── __init__.py
│   └── notification_system.py  # Email, SMS, webhook notifications
├── schemas/                      # Data models and schemas
│   ├── __init__.py
│   └── rentcast_schemas.py      # RentCast API response schemas
└── visualization/                # Chart and graph generation
    ├── __init__.py
    └── visualization.py         # Matplotlib/Seaborn visualizations
```

## Module Descriptions

### api/
- **http_client.py**: Base HTTP client with error handling, rate limiting, and retry logic
- **rentcast_client.py**: Specialized client for RentCast API endpoints with authentication

### core/  
- **data_analyzer.py**: Core analysis engine for market trends, price analysis, property matching
- **data_fetcher.py**: Multi-source data fetching from various real estate APIs
- **database.py**: Database operations and schema management

### config/
- **config_manager.py**: Configuration management supporting YAML, JSON, and environment variables

### notifications/
- **notification_system.py**: Multi-channel notification system (email, SMS, webhooks)

### schemas/
- **rentcast_schemas.py**: Comprehensive dataclasses for all RentCast API response structures

### visualization/
- **visualization.py**: Graph generation for market analysis and data visualization

## Import Changes

All import statements have been updated to reflect the new structure:

### Before:
```python
from src.config_manager import ConfigManager
from src.database import DatabaseManager
from src.rentcast_client import RentCastClient
```

### After:
```python
from src.config.config_manager import ConfigManager
from src.core.database import DatabaseManager
from src.api.rentcast_client import RentCastClient
```

### Convenience Imports (Recommended):
```python
# Main src package provides convenient access to key classes
from src import ConfigManager, DatabaseManager, RentCastClient
```

## Files Updated

The following files have been updated with new import statements:
- `main.py`
- `demo.py` 
- `example.py`
- `rentcast_test.py`
- `test_rentcast_endpoints.py`
- `test_listings_schemas.py`
- `test_avm_schemas.py`
- `test_property_schemas.py`

## Benefits

1. **Better Organization**: Related functionality is grouped together
2. **Clearer Dependencies**: API clients separate from business logic
3. **Easier Navigation**: Developers can quickly find relevant code
4. **Maintainability**: Changes to one area don't affect unrelated modules
5. **Scalability**: Easy to add new modules within appropriate categories
6. **Testing**: Test files can be organized to match source structure

## Migration Notes

- All existing functionality remains unchanged
- Import paths have been updated but API remains the same
- The main `src/__init__.py` provides convenient imports for common classes
- Each subdirectory is a proper Python package with its own `__init__.py`
