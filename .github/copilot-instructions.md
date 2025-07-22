# Copilot Instructions for Real Estate Data Analyzer

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is a Python scripting project for real estate data analysis with the following key components:

## Project Purpose

- Fetch real estate data from various APIs (MLS, Zillow, Redfin, etc.)
- Generate graphs and visualizations for market analysis
- Send notifications when properties matching specific criteria are found
- Perform data analysis and market trend identification

## Key Technologies

- Python 3.9+
- requests for API calls
- pandas for data manipulation
- matplotlib/seaborn for visualization
- smtplib/twilio for notifications
- schedule for automated tasks
- python-dotenv for configuration management

## Code Style Guidelines

- Follow PEP 8 conventions
- Use type hints for function parameters and return values
- Include comprehensive docstrings for all functions and classes
- Implement proper error handling and logging
- Use configuration files for API keys and settings
- Structure code with clear separation of concerns (data fetching, analysis, visualization, notifications)

## Architecture

- Modular design with separate modules for each major function
- Configuration-driven approach for flexibility
- Async support for efficient API calls
- Database integration for data persistence (SQLite by default)
