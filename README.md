# Real Estate Data Analyzer

A comprehensive Python scripting project for fetching, analyzing, and monitoring real estate data. This tool automatically gathers property listings from multiple sources, performs market analysis, generates visualizations, and sends notifications when properties matching your criteria are found.

## Features

- **Multi-Source Data Fetching**: Supports multiple real estate APIs (Zillow, MLS, Redfin, custom APIs)
- **Comprehensive Analysis**: Market trends, price analysis, location insights, and investment opportunities
- **Automated Visualizations**: Generates charts and graphs for market analysis
- **Smart Notifications**: Email, SMS, Slack, and webhook notifications for matching properties
- **Flexible Configuration**: YAML-based configuration with environment variable support
- **Database Storage**: SQLite database for data persistence and historical analysis
- **Scheduling Support**: Run analysis on a schedule or manually

## Project Structure

```
real-estate/
├── main.py                     # Main entry point
├── src/                        # Core modules
│   ├── data_fetcher.py        # Data fetching from various APIs
│   ├── data_analyzer.py       # Market analysis and insights
│   ├── visualization.py       # Graph and chart generation
│   ├── notification_system.py # Alert notifications
│   ├── config_manager.py      # Configuration management
│   └── database.py            # Database operations
├── config/                     # Configuration files
│   ├── config.yaml            # Main configuration
│   └── .env.example          # Environment variables template
├── data/                       # Data storage (SQLite database)
├── output/                     # Generated reports and visualizations
├── logs/                       # Application logs
└── requirements.txt           # Python dependencies
```

## Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd real-estate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

1. Copy the environment variables template:
   ```bash
   cp config/.env.example .env
   ```

2. Edit `.env` and add your API keys and notification credentials:
   ```bash
   EMAIL_USERNAME=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_RECIPIENTS=alerts@yourdomain.com
   ```

3. Customize `config/config.yaml` for your search criteria and preferences.

### 3. Run the Analyzer

```bash
# Run all operations (fetch, analyze, notify)
python main.py

# Run specific operations
python main.py --mode fetch     # Only fetch new data
python main.py --mode analyze   # Only analyze existing data
python main.py --mode notify    # Only check for matching properties

# Enable verbose logging
python main.py --verbose
```

## Configuration

### Search Criteria

Customize `config/config.yaml` to define what properties you're interested in:

```yaml
search_criteria:
  price:
    min: 300000
    max: 800000
  bedrooms:
    min: 2
  bathrooms:
    min: 1.5
  cities:
    in: ["San Francisco", "Oakland", "San Jose"]
  property_type:
    in: ["house", "condo", "townhome"]
  days_on_market:
    max: 30
```

### Notification Channels

Enable multiple notification channels:

```yaml
notifications:
  enabled_channels: ["email", "slack"]
  email:
    enabled: true
    recipients:
      - "your-email@example.com"
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### API Sources

Configure multiple data sources:

```yaml
apis:
  zillow_enabled: true
  zillow_api_key: "your_api_key"
  
  mls_enabled: true
  mls_config:
    api_key: "your_mls_key"
    endpoint: "https://api.mls.com/search"
```

## API Integration

### Supported Sources

- **Zillow**: Requires API key (limited access)
- **MLS**: Multiple Listing Service integration
- **Redfin**: Limited public API
- **Custom APIs**: Configure any REST API endpoint

### Adding Custom Data Sources

Add custom API sources in your configuration:

```yaml
apis:
  custom_apis:
    my_custom_api:
      endpoint: "https://api.example.com/properties"
      headers:
        Authorization: "Bearer YOUR_TOKEN"
      properties_key: "listings"
      field_mapping:
        property_id: "id"
        address: "full_address"
        price: "listing_price"
```

## Analysis Features

### Market Trends
- Price trends over time
- Listing volume analysis
- Market direction indicators

### Price Analysis
- Price distribution statistics
- Price per square foot analysis
- Outlier detection

### Location Analysis
- City-by-city comparisons
- Market hotspots identification
- Geographic price variations

### Investment Opportunities
- Underpriced property identification
- Long-time-on-market properties
- High-potential areas

## Generated Outputs

The analyzer creates:

- **Visualizations**: Graphs and charts in `output/[timestamp]/`
- **Database**: SQLite database with all fetched properties
- **Logs**: Detailed execution logs in `logs/`
- **Notifications**: Alerts for matching properties

## Scheduling

Set up automated runs using the built-in scheduler or cron:

```yaml
# In config.yaml
scheduling:
  enabled: true
  fetch_interval_hours: 6      # Fetch new data every 6 hours
  analysis_interval_hours: 24  # Run analysis daily
  notification_check_interval_hours: 1  # Check for matches hourly
```

Or use cron for system-level scheduling:
```bash
# Run every 6 hours
0 */6 * * * cd /path/to/real-estate && python main.py --mode fetch

# Daily analysis at 8 AM
0 8 * * * cd /path/to/real-estate && python main.py --mode analyze
```

## Notification Examples

### Email Alerts
Receive formatted emails when properties match your criteria:

```
Subject: New Property Alert - 3 Properties Found

Found 3 properties matching your criteria:

1. 123 Main St, San Francisco, CA
   Price: $750,000 | 3/2 | 1,500 sq ft
   Days on Market: 5
```

### Slack Integration
Get instant Slack notifications with property details and direct links.

## Database Schema

The SQLite database includes:
- `properties`: All fetched property data
- `analysis_results`: Historical analysis results
- `notifications_log`: Notification history

## Development

### Adding New Features

1. **New Data Sources**: Add fetcher methods in `data_fetcher.py`
2. **Analysis Types**: Extend `data_analyzer.py` with new analysis functions
3. **Visualizations**: Add chart types in `visualization.py`
4. **Notification Channels**: Implement new notifiers in `notification_system.py`

### Testing

```bash
# Run with verbose logging to debug
python main.py --verbose

# Check database contents
sqlite3 data/real_estate.db "SELECT COUNT(*) FROM properties;"
```

## Security Notes

- Never commit API keys or credentials to version control
- Use environment variables for sensitive configuration
- Respect API rate limits and terms of service
- Consider using API key rotation for production use

## Troubleshooting

### Common Issues

1. **No properties found**: Check API keys and search criteria
2. **Email notifications not working**: Verify SMTP settings and app passwords
3. **Database errors**: Ensure write permissions to `data/` directory
4. **API rate limits**: Reduce fetch frequency or implement caching

### Logging

Enable detailed logging:
```bash
python main.py --verbose
```

Check logs in `logs/real_estate_analyzer.log` for detailed error information.

## License

This project is for educational and personal use. Ensure compliance with all API terms of service and applicable laws regarding data collection and use.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the analyzer.

---

For questions or support, check the logs directory or enable verbose mode for detailed troubleshooting information.
