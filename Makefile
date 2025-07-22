# Real Estate Data Analyzer Makefile
# Provides convenient commands for common development and execution ta## run-verbose: Run with verbose logging enabled
run-verbose:
	@echo "$(GREEN)Running real estate analyzer with verbose logging...$(NC)"
	@$(PYTHON) main.py --verbose --config $(CONFIG_DIR)/config.yaml

## run-web: Start Flask web application
run-web:
	@echo "$(GREEN)Starting Flask web application...$(NC)"
	@echo "$(YELLOW)Web interface will be available at http://localhost:5001$(NC)"
	@$(PYTHON) scripts/run_web.py
.PHONY: help install install-dev setup clean test lint format run run-fetch run-analyze run-notify run-verbose run-web check-config demo

# Default Python interpreter (use virtual environment if available)
PYTHON := $(shell if [ -f .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)
PIP := pip3

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
	@echo ""
	@echo "$(GREEN)Development & Testing:$(NC)"
	@echo "  make test         - Run test suite"
	@echo "  make lint         - Run linting (flake8, mypy)"
	@echo "  make format       - Format code with black"
	@echo "  make check-config - Validate configuration files"
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  make clean        - Clean generated files and caches"
	@echo "  make demo         - Run interactive demo (creates temp script)"
	@echo "  make logs         - Show recent application logs"
	@echo "  make status       - Show project status and configuration"
	@echo ""
	@echo "$(YELLOW)Usage Examples:$(NC)"
	@echo "  make install && make setup    # First-time setup"
	@echo "  make run-fetch run-analyze    # Fetch then analyze"
	@echo "  make format lint test         # Code quality checks"

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

## clean: Clean generated files and caches
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
