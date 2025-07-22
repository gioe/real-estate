# Scripts Directory

This directory contains utility scripts and application runners for the Real Estate Data Analyzer project.

## Contents

### `run_web.py`
Flask web application launcher. Starts the web interface for the real estate analyzer.

**Usage:**
```bash
# From project root
make run-web

# Or directly
python scripts/run_web.py
```

**Features:**
- Web interface available at http://localhost:5001
- Interactive property search and analysis
- Data visualization dashboard
- AVM and market statistics lookup

## Guidelines

- All utility scripts and application runners should be placed in this directory
- Keep the project root clean with only essential files (main.py, setup.py, etc.)
- Scripts should be well-documented with usage examples
- Use the Makefile commands when available for easier execution

## Development

When creating new scripts:
1. Place them in this `scripts/` directory
2. Add appropriate documentation
3. Update the Makefile if the script should have a make target
4. Follow the project's coding standards and type hints
