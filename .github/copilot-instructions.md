# Copilot Instructions for Real Estate Data Analyzer

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

**IMPORTANT: When adding new context, documentation, or project information, always update this copilot-instructions.md file directly rather than creating separate .md files at the project root. This keeps all context consolidated and easily accessible.**

This is a comprehensive Python scripting project for real estate data analysis with advanced API integration, data processing, and market analysis capabilities.

## Project Purpose

- Fetch real estate listings from RentCast API and other sources (MLS, Zillow, Redfin)
- Generate comprehensive market analysis and visualizations
- Send intelligent notifications when listings matching specific criteria are found
- Perform advanced data analysis, trend identification, and investment analysis
- Provide automated valuation models (AVM) for property values and rental estimates
- Support bulk data processing with pagination and rate limiting

## Key Technologies & Dependencies

- Python 3.9+
- **API Integration**: Custom HTTP client with rate limiting, retry logic, and error handling
- **Data Processing**: pandas for data manipulation, comprehensive schema validation
- **Visualization**: matplotlib/seaborn for market analysis charts and graphs
- **Notifications**: smtplib/twilio for email and SMS alerts, webhook support
- **Database**: SQLite (default) with PostgreSQL support for data persistence
- **Configuration**: YAML configuration with environment variable support
- **Scheduling**: schedule for automated tasks and data fetching
- **Type Safety**: Full type hints with dataclasses for API responses

## Code Style Guidelines

- Follow PEP 8 conventions strictly
- Use type hints for ALL function parameters and return values
- Include comprehensive docstrings for all functions and classes using Google/NumPy style
- Implement robust error handling and structured logging
- Use configuration files for API keys, settings, and search criteria
- Structure code with clear separation of concerns (data fetching, analysis, visualization, notifications)
- Prefer dataclasses over dictionaries for structured data
- Use context managers (`with` statements) for resource management

## Project Architecture & Organization

### Directory Structure

```
src/
├── api/                          # API clients and HTTP communication
│   ├── http_client.py           # Base HTTP client with rate limiting/retry
│   └── rentcast_client.py       # RentCast API specialized client
├── config/                       # Configuration management
│   └── config_manager.py        # YAML/JSON configuration handling
├── core/                         # Core business logic
│   ├── data_analyzer.py         # Real estate analysis engine
│   ├── data_fetcher.py          # Multi-source listings fetching with pagination
│   ├── database.py              # Database operations and schema management
│   └── search_queries.py        # Structured search query system
├── notifications/                # Alert and notification system
│   └── notification_system.py  # Multi-channel notifications
├── schemas/                      # Data models and API response schemas
│   └── rentcast_schemas.py      # Complete RentCast API schemas
└── visualization/                # Chart and graph generation
    └── visualization.py         # Market analysis visualizations
```

### Project Root Structure

Keep the project root clean with only essential files:

```
real-estate/
├── Makefile                     # Project management commands
├── main.py                      # Main application entry point
├── setup.py                     # Package setup and dependencies
├── requirements.txt             # Python dependencies
├── README.md                    # Project overview and quick start
├── .gitignore                   # Git ignore patterns
├── src/                         # Source code (organized above)
├── config/                      # Configuration files
├── data/                        # Data storage and databases
├── logs/                        # Application logs
└── output/                      # Generated reports and visualizations
```

**CRITICAL: PROJECT ROOT HYGIENE**

The project root MUST remain clean and contain ONLY these essential files:

- `main.py` (main application entry point)
- `Makefile` (project management commands)
- `setup.py` (package setup and dependencies)
- `requirements.txt` (Python dependencies)
- `README.md` (project overview and quick start)
- `.gitignore` (Git ignore patterns)
- Core directories: `src/`, `config/`, `data/`, `logs/`, `output/`

**STRICTLY FORBIDDEN in project root:**

- Demo scripts (`demo_*.py`, `test_*.py`, `example_*.py`)
- Temporary scripts of any kind
- Documentation files (`.md` files other than `README.md`)
- Documentation directories (`docs/`, `documentation/`, etc.)
- One-off test files or validation scripts
- Any `.py` files other than `main.py` and `setup.py`

**DOCUMENTATION POLICY:**
ALL project documentation MUST be consolidated in this single `copilot-instructions.md` file.
NEVER create separate documentation files or directories.
This includes technical specifications, implementation guides, API documentation, error handling guides, etc.
The single-file approach ensures documentation stays current and prevents documentation sprawl.

**Required locations for other content:**

- All documentation: Consolidated in this `copilot-instructions.md` file ONLY
- All test files: `tests/` directory (if persistent testing is needed)
- All temporary/demo scripts: Create when needed, DELETE IMMEDIATELY after use

Any deviation from this structure will be immediately corrected. When creating temporary scripts for testing or demonstration, they MUST be deleted as soon as they're no longer needed.

## Makefile Integration

The project now includes a comprehensive Makefile for easy project management and common tasks:

### Core Commands

- `make run` - Run all operations (fetch, analyze, notify)
- `make run-fetch` - Fetch new data only
- `make run-analyze` - Analyze existing data only
- `make run-notify` - Check for matching properties and notify
- `make run-verbose` - Run with verbose logging

### Development Commands

- `make install` - Install production dependencies
- `make install-dev` - Install development dependencies
- `make setup` - Initialize project directories and config files
- `make test` - Run test suite with coverage
- `make lint` - Run linting (flake8, mypy)
- `make format` - Format code with black
- `make clean` - Clean generated files and caches

### Utility Commands

- `make help` - Show all available commands
- `make status` - Show project status and configuration
- `make check-config` - Validate configuration files
- `make logs` - Show recent application logs
- `make demo` - Run interactive demo (creates and deletes temp script)

### Recommended Workflows

```bash
# First-time setup
make install-dev && make setup

# Daily usage
make run

# Development workflow
make format lint test

# Check project health
make status && make logs
```

The Makefile follows the project's clean structure principles - any temporary scripts created (like in `make demo`) are automatically deleted after use.

### Import Conventions

Use the organized import structure:

```python
from src.api.rentcast_client import RentCastClient
from src.core.data_fetcher import RealEstateDataFetcher
from src.schemas.rentcast_schemas import PropertyListing, AVMValueResponse
from src.config.config_manager import ConfigManager
```

Or convenience imports from main package:

```python
from src import RentCastClient, RealEstateDataFetcher, ConfigManager
```

## API Integration Architecture

### RentCast API Integration

The project includes comprehensive RentCast API integration with full schema support:

#### Supported Endpoints & Schemas:

1. **Properties Endpoint** (`/properties`)

   - Search properties by location, coordinates, or specific address
   - Full property details with specifications and features

2. **Listings Endpoint** (`/listings`)

   - Both sale and rental listings
   - Complete schemas: `PropertyListing`, `ListingsResponse`
   - Agent, office, and builder information
   - Historical price and status tracking
   - Pagination support with `ListingsResponse`

3. **AVM Endpoints** (`/avm/value`, `/avm/rent/long-term`)

   - Automated property valuations and rental estimates
   - Schemas: `AVMValueResponse`, `AVMRentResponse`, `Comparable`
   - Confidence ranges and comparable property analysis
   - Investment analysis capabilities (rental yield calculations)

4. **Markets Endpoint** (`/markets`)
   - Complete market statistics by zip code
   - Schema: `MarketStatistics` with `MarketSaleData` and `MarketRentalData`
   - Breakdowns by property type and bedroom count
   - Historical monthly data with trend analysis
   - Price/rent per square foot metrics

### HTTP Client Features

- **Rate Limiting**: 20 requests per second (RentCast API limit)
- **Retry Logic**: Exponential backoff for failed requests
- **Error Handling**: Detailed error reporting with status codes
- **Session Management**: Persistent connections for performance
- **Timeout Handling**: Configurable timeouts to prevent hanging
- **Authentication**: Automatic API key header management

### RentCast API Error Handling

Comprehensive error handling system for all RentCast API response codes:

| Code | Type                | Error Class                      | Retryable     |
| ---- | ------------------- | -------------------------------- | ------------- |
| 400  | Invalid parameters  | `RentCastInvalidParametersError` | No            |
| 401  | Auth/billing error  | `RentCastAuthError`              | No            |
| 404  | No results          | `RentCastNoResultsError`         | No            |
| 405  | Method not allowed  | `RentCastMethodNotAllowedError`  | No            |
| 429  | Rate limit exceeded | `RentCastRateLimitError`         | Yes (60s max) |
| 500  | Server error        | `RentCastServerError`            | Yes (20s max) |
| 504  | Timeout error       | `RentCastTimeoutError`           | Yes (30s max) |

**Key Features:**

- RFC 9110 compliant HTTP status code handling
- Intelligent retry logic with exponential backoff
- Graceful handling of "no results" scenarios (404)
- Rate limiting compliance (20 requests/second)
- Detailed error recommendations for debugging
- Automatic error classification and response parsing

## Data Processing & Analysis

### Pagination System

Comprehensive pagination support for handling large datasets:

- **API Pagination**: Automatic handling of paginated RentCast responses
- **Database Pagination**: Efficient querying with offset/limit support
- **Configuration**: Configurable page sizes and limits
- **Progress Tracking**: Built-in logging for long-running operations

Example usage:

```python
# Paginate through all listings
for response in fetcher.fetch_listings_paginated(search_params, max_pages=10):
    listings = response.data
    # Process each page

# Fetch all results automatically
all_properties = fetcher.fetch_all_properties_paginated(search_params)
```

### Search Query System

Structured, type-safe search system supporting:

1. **Specific Address Search** - Find data for particular property addresses
2. **Location Search** - Find properties by city, state, zip code with filters
3. **Geographical Area Search** - Find properties within radius of coordinates

Example usage:

```python
# Location search with filters
properties = fetcher.search_by_location(
    city="Austin", state="TX",
    bedrooms=3, bathrooms=2,
    min_price=300000, max_price=600000
)

# Geographical search
properties = fetcher.search_by_coordinates(
    latitude=33.45141, longitude=-112.073827,
    radius=5, property_type="Single Family"
)
```

### Schema System

Complete type-safe schemas for all RentCast API responses:

- **Full Type Safety**: All schemas use Python type hints with Optional types
- **Serialization**: Every schema implements `from_dict()` and `to_dict()` methods
- **Nested Objects**: Complex nested structures parsed recursively
- **Enumerations**: Categorical fields use Python Enum classes
- **Validation**: Comprehensive test coverage for all schemas

Common schema pattern:

```python
@dataclass
class PropertySchema:
    field_name: Optional[str] = None
    numeric_field: Optional[float] = None
    nested_objects: List[NestedSchema] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertySchema':
        # Parse and validate data
        return cls(field_name=data.get('fieldName'), ...)

    def to_dict(self) -> Dict[str, Any]:
        # Serialize back to dictionary
        return {k: v for k, v in asdict(self).items() if v is not None}
```

## Configuration Management

### YAML Configuration Structure

```yaml
# API configuration
api:
  rentcast_api_key: "${RENTCAST_API_KEY}"
  rentcast_endpoint: "https://api.rentcast.io/v1"
  rentcast_rate_limit: 20
  default_page_size: 50

  # Zip codes configuration for data fetching
  zip_codes:
    - "10804" # Westchester County, NY

  zip_code_processing:
    listings_per_zip: 100
    fetch_sales: true
    fetch_rentals: true
    delay_between_zips: 2
    property_types:
      - "Single Family"
      - "Condo"
      - "Townhouse"
    filters:
      min_beds: 1
      max_beds: 10
      min_baths: 1
      max_price: 10000000

# Search criteria
search_criteria:
  price:
    min: 300000
    max: 800000
  bedrooms:
    min: 2
  bathrooms:
    min: 1.5
  cities:
    in: ["Austin", "Dallas", "Houston"]
  property_type:
    in: ["Single Family", "Condo", "Townhome"]

# Database configuration
database:
  type: "sqlite"
  path: "data/real_estate.db"
  # Tables:
  # - listings: Raw market listings from APIs (sale/rental)
  # - properties: Legacy table (for backward compatibility)
  # - avm_valuations, market_statistics, etc.

# Notification settings
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "${EMAIL_USERNAME}"
    password: "${EMAIL_PASSWORD}"
    recipients: ["${EMAIL_RECIPIENTS}"]
```

## Main Application Flow

The `main.py` orchestrates the entire data pipeline:

1. **Configuration Loading**: Load YAML config and environment variables
2. **Database Initialization**: Set up SQLite/PostgreSQL database
3. **Component Initialization**: Initialize fetcher, analyzer, visualizer, notifications
4. **Data Fetching**: Fetch new listings from configured sources (mode: fetch)
5. **Analysis**: Analyze listings data and generate reports (mode: analyze)
6. **Visualization**: Generate charts and graphs with timestamps
7. **Notifications**: Check for matching listings and send alerts (mode: notify)

Execution modes:

- `python main.py --mode fetch` - Only fetch new data
- `python main.py --mode analyze` - Only analyze existing data
- `python main.py --mode notify` - Only check for matching properties
- `python main.py --mode all` - Run all operations (default)

**Recommended**: Use Makefile commands instead of direct Python execution:

- `make run-fetch` instead of `python main.py --mode fetch`
- `make run-analyze` instead of `python main.py --mode analyze`
- `make run-notify` instead of `python main.py --mode notify`
- `make run` instead of `python main.py --mode all`

## Testing & Validation

Comprehensive test coverage includes:

- **Schema Tests**: Validation of all API response schemas
- **Integration Tests**: End-to-end API integration testing
- **Data Conversion**: Round-trip serialization testing
- **Edge Cases**: Null handling, minimal data, empty responses
- **Performance**: Pagination and large dataset handling

## Development Guidelines

1. **MANDATORY PROJECT ROOT HYGIENE**:

   - NEVER create demo scripts, test scripts, or temporary files in the project root
   - ONLY these files allowed in root: `main.py`, `Makefile`, `setup.py`, `requirements.txt`, `README.md`, `.gitignore`
   - ALL documentation goes in this `copilot-instructions.md` file ONLY
   - ALL test files go in `tests/` directory (if persistent)
   - CREATE temporary scripts when needed, DELETE IMMEDIATELY after use
   - Any `.md` files other than `README.md` are FORBIDDEN in project root
   - NEVER create separate documentation files - consolidate everything here

2. **Always Update This File**: When adding new features, schemas, or documentation, update this copilot-instructions.md file directly instead of creating new .md files

3. **Clean Up Temporary Scripts**: Always delete one-off demo scripts, test scripts, and temporary files after they've served their purpose. Keep the project root clean with only essential files (main.py, setup.py, requirements.txt, README.md). Place persistent test scripts in a `tests/` directory if needed.

4. **Schema-First Development**: Define schemas before implementing API endpoints

5. **Error Handling**: Implement comprehensive error handling with informative messages

6. **Logging**: Use structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR)

7. **Configuration**: Make features configurable rather than hard-coded

8. **Type Safety**: Use type hints and validate data structures

9. **Testing**: Write tests for new functionality before implementation

10. **Documentation**: Include comprehensive docstrings and usage examples

## Current Implementation Status

✅ **Complete RentCast API Integration**

- All major endpoints implemented with full schemas
- Properties, Listings, AVM, and Markets endpoints
- Comprehensive pagination and search support
- Rate limiting and error handling

✅ **Data Processing Pipeline**

- Multi-source data fetching
- Database storage and management
- Market analysis and trend identification
- Investment analysis capabilities

✅ **Visualization & Notifications**

- Chart generation for market analysis
- Multi-channel notification system
- Email, SMS, and webhook support
- Automated property matching and alerts

✅ **Project Management & Development Tools**

- Comprehensive Makefile with 20+ commands
- Easy project setup and dependency management
- Development workflow automation (test, lint, format)
- Automatic cleanup of temporary files and demo scripts
- Configuration validation and project status monitoring
- Color-coded output and helpful error messages
