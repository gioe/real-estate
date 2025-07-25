# Real Estate Data Analyzer Makefile
# Provides convenient commands for common development and execution tasks

## run-web: Start Flask web application
run-web:
	@echo "$(GREEN)Starting Flask web application...$(NC)"
	@echo "$(YELLOW)Web interface will be available at http://localhost:5001$(NC)"
	@$(PYTHON) scripts/run_web.py

## kill-web: Kill all running Flask/Python web applications
kill-web:
	@echo "$(YELLOW)Killing all running Flask/Python web applications...$(NC)"
	@echo "$(CYAN)Looking for Flask processes...$(NC)"
	@-pkill -f "flask|python.*web_app.py|python.*run_web.py" 2>/dev/null || true
	@echo "$(CYAN)Looking for Python processes on common web ports...$(NC)"
	@-lsof -ti:5000 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:5001 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:5002 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:5003 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:5004 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@-lsof -ti:8080 | xargs kill -9 2>/dev/null || true
	@echo "$(GREEN)✅ All web applications killed!$(NC)"
	@echo "$(BLUE)Note: If processes were running, they may take a moment to fully terminate$(NC)"

## restart-web: Kill all web apps and start fresh
restart-web: kill-web
	@sleep 2
	@$(MAKE) run-web

## init-db: Initialize database with enhanced schema
init-db:
	@echo "$(GREEN)Initializing enhanced database schema...$(NC)"
	@$(PYTHON) -c "from src.core.database import DatabaseManager; db = DatabaseManager({'type': 'sqlite', 'sqlite_path': 'data/real_estate.db'}); print('✅ Database initialized successfully!')"

## db-stats: Show database statistics
db-stats:
	@echo "$(GREEN)Database Statistics:$(NC)"
	@$(PYTHON) -c "from src.core.database import DatabaseManager; import json; db = DatabaseManager({'type': 'sqlite', 'sqlite_path': 'data/real_estate.db'}); stats = db.get_database_stats(); print(json.dumps(stats, indent=2))"

## db-sample: Add sample data for testing
db-sample:
	@echo "$(GREEN)Adding sample data to database...$(NC)"
	@$(PYTHON) -c "import sqlite3; from datetime import datetime; conn = sqlite3.connect('data/real_estate.db'); c = conn.cursor(); c.execute('INSERT OR REPLACE INTO properties (property_id, source, address, city, state, zip_code, price, bedrooms, bathrooms, square_feet, property_type, fetched_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', ('SAMPLE_001', 'demo', '123 Main St', 'Austin', 'TX', '78701', 450000, 3, 2.0, 1800, 'Single Family', datetime.now().isoformat())); conn.commit(); conn.close(); print('✅ Sample data added!')"

.PHONY: help install install-dev setup clean test lint format run run-fetch run-analyze run-notify run-verbose run-web kill-web restart-web init-db db-stats db-sample check-config demo

# Default Python interpreter (use virtual environment if available)
# Check for virtual environment and validate it works
PYTHON := $(shell \
	if [ -f .venv/bin/python ] && .venv/bin/python -c "import sys" 2>/dev/null; then \
		echo .venv/bin/python; \
	else \
		echo python3; \
	fi)
PIP := $(shell \
	if [ -f .venv/bin/pip ] && .venv/bin/pip --version 2>/dev/null >/dev/null; then \
		echo .venv/bin/pip; \
	else \
		echo pip3; \
	fi)

# Project directories
SRC_DIR := src
CONFIG_DIR := config
DATA_DIR := data
LOGS_DIR := logs
OUTPUT_DIR := output

# Color codes for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[1;37m
NC := \033[0m # No Color

## help: Show this help message
help:
	@echo "$(CYAN)Real Estate Data Analyzer - Available Commands$(NC)"
	@echo "=================================================="
	@echo ""
	@echo "$(GREEN)Setup & Installation:$(NC)"
	@echo "  make venv-check   - Check virtual environment status"
	@echo "  make venv-create  - Create a fresh virtual environment"
	@echo "  make venv-reset   - Reset venv and reinstall dependencies"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make setup        - Initialize project directories and config"
	@echo ""
	@echo "$(GREEN)Application Execution:$(NC)"
	@echo "  make run          - Run all operations (fetch, analyze, notify)"
	@echo "  make run-fetch    - Fetch new real estate data only"
	@echo "  make run-analyze  - Analyze existing data only"
	@echo "  make run-notify   - Check for matching properties and notify"
	@echo "  make run-verbose  - Run with verbose logging"
	@echo "  make run-web      - Start Flask web application"
	@echo "  make kill-web     - Kill all running Flask/Python web apps"
	@echo "  make restart-web  - Kill all web apps and start fresh"
	@echo ""
	@echo "$(GREEN)Database Management:$(NC)"
	@echo "  make init-db      - Initialize database with enhanced schema"
	@echo "  make db-stats     - Show database statistics and table info"
	@echo "  make db-sample    - Add sample data for testing"
	@echo ""
	@echo "$(GREEN)Development & Testing:$(NC)"
	@echo "  make test         - Run test suite"
	@echo "  make lint         - Run linting (flake8, mypy)"
	@echo "  make format       - Format code with black"
	@echo "  make check-config - Validate configuration files"
	@echo ""
		@echo "$(GREEN)Utilities:$(NC)"
	@echo "  make env-check    - Run comprehensive environment diagnostics"
	@echo "  make status       - Show comprehensive project status"
	@echo "  make clean        - Clean temporary files and caches"
	@echo "  make demo         - Create sample project demo"
	@echo "  make logs         - Show recent application logs"
	@echo "  make status       - Show project status and configuration"
	@echo ""
	@echo "$(YELLOW)Usage Examples:$(NC)"
	@echo "  make install && make setup    # First-time setup"
	@echo "  make run-fetch run-analyze    # Fetch then analyze"
	@echo "  make format lint test         # Code quality checks"

## venv-check: Check virtual environment status
venv-check:
	@echo "$(GREEN)Virtual Environment Status:$(NC)"
	@echo "Current PYTHON: $(PYTHON)"
	@echo "Current PIP: $(PIP)"
	@if [ "$(PYTHON)" = "python3" ]; then \
		echo "$(YELLOW)⚠️  Using system Python - consider creating a virtual environment$(NC)"; \
		echo "$(CYAN)Run: python3 -m venv .venv && make install$(NC)"; \
	else \
		echo "$(GREEN)✅ Using virtual environment$(NC)"; \
		$(PYTHON) --version; \
		echo "Installed packages: $$($(PIP) list | wc -l) packages"; \
	fi

## venv-create: Create a fresh virtual environment
venv-create:
	@echo "$(GREEN)Creating fresh virtual environment...$(NC)"
	@if [ -d .venv ]; then \
		echo "$(YELLOW)Removing existing .venv directory...$(NC)"; \
		rm -rf .venv; \
	fi
	@if [ -d venv ]; then \
		echo "$(YELLOW)Removing existing venv directory...$(NC)"; \
		rm -rf venv; \
	fi
	python3 -m venv .venv
	@echo "$(GREEN)Virtual environment created at .venv/$(NC)"
	@echo "$(CYAN)Next step: make install$(NC)"

## venv-reset: Reset virtual environment and reinstall dependencies
venv-reset: venv-create install
	@echo "$(GREEN)Virtual environment reset complete!$(NC)"

## install: Install production dependencies
install:
	@echo "$(GREEN)Installing production dependencies...$(NC)"
	$(PIP) install -r requirements.txt

## install-dev: Install development dependencies
install-dev: install
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	$(PIP) install pytest pytest-cov black flake8 mypy

## setup: Initialize project directories and configuration
setup:
	@echo "$(GREEN)Setting up project directories...$(NC)"
	@mkdir -p $(DATA_DIR) $(LOGS_DIR) $(OUTPUT_DIR)
	@if [ ! -f $(CONFIG_DIR)/config.yaml ]; then \
		echo "$(YELLOW)Creating default config.yaml...$(NC)"; \
		cp $(CONFIG_DIR)/config.yaml.example $(CONFIG_DIR)/config.yaml 2>/dev/null || \
		echo "$(RED)Warning: No config.yaml.example found. Please create $(CONFIG_DIR)/config.yaml manually.$(NC)"; \
	fi
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env file...$(NC)"; \
		cp .env.example .env 2>/dev/null || \
		echo "$(RED)Warning: No .env.example found. Please create .env manually.$(NC)"; \
	fi
	@echo "$(GREEN)Project setup complete!$(NC)"

## run: Run all operations (fetch, analyze, notify)
run:
	@echo "$(GREEN)Running Real Estate Analyzer - All Operations$(NC)"
	$(PYTHON) main.py --mode all

## run-fetch: Fetch new real estate data only
run-fetch:
	@echo "$(GREEN)Fetching new real estate data...$(NC)"
	$(PYTHON) main.py --mode fetch

## run-analyze: Analyze existing data only
run-analyze:
	@echo "$(GREEN)Analyzing existing data...$(NC)"
	$(PYTHON) main.py --mode analyze

## run-notify: Check for matching properties and send notifications
run-notify:
	@echo "$(GREEN)Checking for matching properties...$(NC)"
	$(PYTHON) main.py --mode notify

## run-verbose: Run with verbose logging
run-verbose:
	@echo "$(GREEN)Running with verbose logging...$(NC)"
	$(PYTHON) main.py --mode all --verbose

## test: Run test suite
test:
	@echo "$(GREEN)Running test suite...$(NC)"
	@if command -v pytest >/dev/null 2>&1; then \
		pytest $(SRC_DIR)/ -v --cov=$(SRC_DIR) --cov-report=term-missing; \
	else \
		echo "$(YELLOW)pytest not installed. Installing...$(NC)"; \
		$(PIP) install pytest pytest-cov; \
		pytest $(SRC_DIR)/ -v --cov=$(SRC_DIR) --cov-report=term-missing; \
	fi

## lint: Run linting (flake8, mypy)
lint:
	@echo "$(GREEN)Running linting checks...$(NC)"
	@if command -v flake8 >/dev/null 2>&1; then \
		echo "$(BLUE)Running flake8...$(NC)"; \
		flake8 $(SRC_DIR)/ main.py --max-line-length=100 --ignore=E203,W503; \
	else \
		echo "$(YELLOW)flake8 not installed. Run 'make install-dev' first.$(NC)"; \
	fi
	@if command -v mypy >/dev/null 2>&1; then \
		echo "$(BLUE)Running mypy...$(NC)"; \
		mypy $(SRC_DIR)/ main.py --ignore-missing-imports; \
	else \
		echo "$(YELLOW)mypy not installed. Run 'make install-dev' first.$(NC)"; \
	fi

## format: Format code with black
format:
	@echo "$(GREEN)Formatting code with black...$(NC)"
	@if command -v black >/dev/null 2>&1; then \
		black $(SRC_DIR)/ main.py --line-length=100; \
	else \
		echo "$(YELLOW)black not installed. Installing...$(NC)"; \
		$(PIP) install black; \
		black $(SRC_DIR)/ main.py --line-length=100; \
	fi

## check-config: Validate configuration files
check-config:
	@echo "$(GREEN)Validating configuration...$(NC)"
	@if [ -f $(CONFIG_DIR)/config.yaml ]; then \
		echo "$(BLUE)✓ config.yaml found$(NC)"; \
		$(PYTHON) -c "import yaml; yaml.safe_load(open('$(CONFIG_DIR)/config.yaml'))" && echo "$(BLUE)✓ config.yaml is valid YAML$(NC)" || echo "$(RED)✗ config.yaml has syntax errors$(NC)"; \
	else \
		echo "$(RED)✗ config.yaml not found$(NC)"; \
	fi
	@if [ -f .env ]; then \
		echo "$(BLUE)✓ .env file found$(NC)"; \
		grep -q "RENTCAST_API_KEY" .env && echo "$(BLUE)✓ RENTCAST_API_KEY configured$(NC)" || echo "$(YELLOW)⚠ RENTCAST_API_KEY not set in .env$(NC)"; \
	else \
		echo "$(YELLOW)⚠ .env file not found$(NC)"; \
	fi

## demo: Run interactive demo (creates temporary demo script)
demo:
	@echo "$(GREEN)Creating and running interactive demo...$(NC)"
	@echo "#!/usr/bin/env python3" > temp_demo.py
	@echo "\"\"\"Temporary demo script - will be auto-deleted\"\"\"" >> temp_demo.py
	@echo "import sys, os" >> temp_demo.py
	@echo "sys.path.append('.')" >> temp_demo.py
	@echo "print('Real Estate Analyzer Demo')" >> temp_demo.py
	@echo "print('=' * 40)" >> temp_demo.py
	@echo "try:" >> temp_demo.py
	@echo "    from src.config.config_manager import ConfigManager" >> temp_demo.py
	@echo "    from src.core.data_fetcher import RealEstateDataFetcher" >> temp_demo.py
	@echo "    config = ConfigManager()" >> temp_demo.py
	@echo "    fetcher = RealEstateDataFetcher(config.get_api_config())" >> temp_demo.py
	@echo "    print('✓ Configuration loaded successfully')" >> temp_demo.py
	@echo "    print('✓ Data fetcher initialized')" >> temp_demo.py
	@echo "    print('Demo completed successfully!')" >> temp_demo.py
	@echo "except Exception as e:" >> temp_demo.py
	@echo "    print(f'Demo failed: {e}')" >> temp_demo.py
	@echo "    print('Note: Run \"make install\" to install dependencies')" >> temp_demo.py
	@$(PYTHON) temp_demo.py || true
	@rm -f temp_demo.py
	@echo "$(GREEN)Demo completed and temporary script cleaned up$(NC)"

## logs: Show recent application logs
logs:
	@echo "$(GREEN)Recent application logs:$(NC)"
	@if [ -f $(LOGS_DIR)/real_estate_analyzer.log ]; then \
		tail -20 $(LOGS_DIR)/real_estate_analyzer.log; \
	else \
		echo "$(YELLOW)No log file found at $(LOGS_DIR)/real_estate_analyzer.log$(NC)"; \
	fi

## status: Show project status and configuration
status:
	@echo "$(CYAN)Real Estate Analyzer - Project Status$(NC)"
	@echo "======================================"
	@echo "$(GREEN)Python Environment:$(NC)"
	@$(PYTHON) --version
	@echo ""
	@echo "$(GREEN)Project Structure:$(NC)"
	@ls -la | head -10
	@echo ""
	@echo "$(GREEN)Configuration Status:$(NC)"
	@make check-config --no-print-directory
	@echo ""
	@echo "$(GREEN)Data Directory:$(NC)"
	@ls -la $(DATA_DIR)/ 2>/dev/null | head -5 || echo "$(YELLOW)Data directory empty or doesn't exist$(NC)"
	@echo ""
	@echo "$(GREEN)Recent Activity:$(NC)"
	@if [ -f $(LOGS_DIR)/real_estate_analyzer.log ]; then \
		tail -3 $(LOGS_DIR)/real_estate_analyzer.log; \
	else \
		echo "$(YELLOW)No recent activity logs$(NC)"; \
	fi

## env-check: Run comprehensive environment diagnostics
env-check:
	@echo "$(GREEN)Running comprehensive environment check...$(NC)"
	@./scripts/env_check.sh

## status: Show comprehensive project status
status: venv-check
	@echo ""
	@echo "$(GREEN)Project Structure:$(NC)"
	@echo "  Source directory: $(SRC_DIR)/"
	@echo "  Config directory: $(CONFIG_DIR)/"
	@echo "  Data directory: $(DATA_DIR)/"
	@echo "  Logs directory: $(LOGS_DIR)/"
	@echo "  Output directory: $(OUTPUT_DIR)/"
	@echo ""
	@echo "$(GREEN)Configuration Files:$(NC)"
	@if [ -f $(CONFIG_DIR)/config.yaml ]; then 
		echo "  ✅ config.yaml exists"; 
	else 
		echo "  ❌ config.yaml missing"; 
	fi
	@if [ -f .env ]; then 
		echo "  ✅ .env exists"; 
	else 
		echo "  ❌ .env missing"; 
	fi
	@echo ""
	@echo "$(GREEN)Database:$(NC)"
	@if [ -f $(DATA_DIR)/real_estate.db ]; then 
		echo "  ✅ Database exists"; 
	else 
		echo "  ❌ Database missing - run 'make init-db'"; 
	fi

## clean: Clean up temporary files and caches
clean:
	@echo "$(GREEN)Cleaning generated files and caches...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "temp_*.py" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleanup completed$(NC)"

# Advanced targets for development workflow

## dev-setup: Complete development environment setup
dev-setup: install-dev setup
	@echo "$(GREEN)Development environment ready!$(NC)"

## ci: Run continuous integration checks (format, lint, test)
ci: format lint test
	@echo "$(GREEN)All CI checks passed!$(NC)"

## quick-run: Quick test run with minimal output
quick-run:
	@$(PYTHON) main.py --mode fetch --config $(CONFIG_DIR)/config.yaml 2>/dev/null || echo "$(YELLOW)Quick run completed with warnings$(NC)"

## watch-logs: Watch log file in real-time (requires tail)
watch-logs:
	@echo "$(GREEN)Watching logs... (Press Ctrl+C to stop)$(NC)"
	@tail -f $(LOGS_DIR)/real_estate_analyzer.log 2>/dev/null || echo "$(YELLOW)No log file to watch$(NC)"
