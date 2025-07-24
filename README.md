# Real Estate Data Analyzer

A comprehensive Python scripting project for fetching, analyzing, and monitoring real estate data. This tool automatically gathers listings from multiple sources, performs market analysis, generates visualizations, and sends notifications when properties matching your criteria are found.

## Quick Start

### 1. Installation & Setup

```bash
# Clone or navigate to the project directory
cd real-estate

# Install dependencies and setup project
make install
make setup
```

### 2. Configuration

The `make setup` command will create template configuration files:

1. Edit `.env` and add your API keys:
   ```bash
   RENTCAST_API_KEY=your_api_key_here
   EMAIL_USERNAME=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   ```

2. Customize `config/config.yaml` for your search criteria and preferences.

### 3. Run the Analyzer

```bash
# See all available commands
make help

# Run all operations (recommended)
make run

# Run specific operations
make run-fetch     # Only fetch new data
make run-analyze   # Only analyze existing data
make run-notify    # Only check for matching properties

# Run with detailed logging
make run-verbose
```

## Makefile Commands

The project uses a comprehensive Makefile for easy project management:

### Setup & Installation
- `make install` - Install production dependencies
- `make install-dev` - Install development dependencies
- `make setup` - Initialize project directories and config files

### Application Execution
- `make run` - Run all operations (fetch, analyze, notify)
- `make run-fetch` - Fetch new real estate data only
- `make run-analyze` - Analyze existing data only
- `make run-notify` - Check for matching properties and notify
- `make run-verbose` - Run with verbose logging
- `make run-web` - Start Flask web application on http://localhost:5000

### Development & Testing
- `make test` - Run test suite with coverage
- `make lint` - Run linting (flake8, mypy)
- `make format` - Format code with black
- `make check-config` - Validate configuration files

### Utilities
- `make clean` - Clean generated files and caches
- `make demo` - Run interactive demo
- `make logs` - Show recent application logs
- `make status` - Show project status and configuration

### Example Workflows

```bash
# First-time setup
make install-dev && make setup

# Daily usage
make run

# Development workflow
make format lint test

# Check project status
make status
make logs
```

## Documentation

**📚 For complete project documentation, development guidelines, API schemas, and detailed usage examples, see [.github/copilot-instructions.md](.github/copilot-instructions.md)**

The copilot-instructions.md file contains:
- Complete API integration documentation
- Schema definitions and usage examples
- Search query system documentation
- Pagination and data processing guides
- Configuration management details
- Development guidelines and best practices

## Features

- **Multi-Source Data Fetching**: Comprehensive RentCast API integration
- **Advanced Analysis**: Market trends, AVM valuations, investment analysis
- **Automated Visualizations**: Charts and graphs for market analysis
- **Smart Notifications**: Multi-channel alerts for matching properties
- **Flexible Configuration**: YAML-based configuration with environment variables
- **Database Storage**: SQLite/PostgreSQL for data persistence
- **Makefile Integration**: Easy project management with make commands
- **Robust Error Handling**: RFC 9110 compliant RentCast API error handling with intelligent retries

## Error Handling

The project includes comprehensive error handling for the RentCast API:

- **RFC 9110 Compliant**: Follows standard HTTP status code specifications
- **RentCast-Specific Errors**: Custom exceptions for each API response code (400, 401, 404, 429, 500, 504)
- **Intelligent Retry Logic**: Automatic retries with exponential backoff for retryable errors
- **Rate Limit Compliance**: Respects RentCast's 20 requests/second limit
- **Graceful Degradation**: Handles "no results" scenarios without failing
- **Detailed Recommendations**: Specific guidance for each error type

See [docs/rentcast_error_handling.md](docs/rentcast_error_handling.md) for complete documentation.

## Project Structure

```
real-estate/
├── Makefile                    # Project management commands
├── main.py                     # Main entry point
├── src/                        # Core modules organized by function
│   ├── api/                   # HTTP clients and API integration
│   ├── core/                  # Business logic and data processing
│   ├── config/                # Configuration management
│   ├── notifications/         # Alert and notification system
│   ├── schemas/               # Data models and API schemas
│   └── visualization/         # Chart and graph generation
├── config/                     # Configuration files
├── data/                       # Data storage
├── output/                     # Generated reports and visualizations
└── logs/                       # Application logs
```

## Requirements

- Python 3.9+
- Make (available on macOS/Linux, Windows with WSL)
- RentCast API key (for real estate data)
- Email credentials (for notifications)

## License

This project is for educational and personal use.
