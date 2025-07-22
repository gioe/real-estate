"""
Configuration Manager Module

This module handles loading and managing configuration for the real estate analyzer.
Supports YAML, JSON, and environment variable configuration.
"""

import yaml
import json
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class ConfigManager:
    """Main class for managing application configuration."""
    
    def __init__(self, config_file_path: str = 'config/config.yaml'):
        """
        Initialize the configuration manager.
        
        Args:
            config_file_path: Path to the configuration file
        """
        self.config_file_path = Path(config_file_path)
        self.config = {}
        self._load_config()
        self._apply_environment_overrides()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            if not self.config_file_path.exists():
                logger.warning(f"Configuration file not found: {self.config_file_path}")
                self.config = self._get_default_config()
                return
            
            if self.config_file_path.suffix.lower() in ['.yaml', '.yml']:
                with open(self.config_file_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
            elif self.config_file_path.suffix.lower() == '.json':
                with open(self.config_file_path, 'r') as f:
                    self.config = json.load(f)
            else:
                logger.error(f"Unsupported configuration file format: {self.config_file_path.suffix}")
                self.config = self._get_default_config()
                
            logger.info(f"Configuration loaded from {self.config_file_path}")
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self.config = self._get_default_config()
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            'REAL_ESTATE_DB_PATH': ['database', 'sqlite_path'],
            'REAL_ESTATE_LOG_LEVEL': ['logging', 'level'],
            'RENTCAST_API_KEY': ['apis', 'rentcast_api_key'],
            'ZILLOW_API_KEY': ['apis', 'zillow_api_key'],
            'MLS_API_KEY': ['apis', 'mls_config', 'api_key'],
            'EMAIL_USERNAME': ['notifications', 'email', 'username'],
            'EMAIL_PASSWORD': ['notifications', 'email', 'password'],
            'EMAIL_RECIPIENTS': ['notifications', 'email', 'recipients'],
            'SLACK_WEBHOOK_URL': ['notifications', 'slack', 'webhook_url'],
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                # Handle special cases
                if env_var == 'EMAIL_RECIPIENTS':
                    env_value = env_value.split(',')
                
                # Set nested configuration value
                current = self.config
                for key in config_path[:-1]:
                    current = current.setdefault(key, {})
                current[config_path[-1]] = env_value
                
                logger.info(f"Applied environment override for {env_var}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if no config file is found."""
        return {
            'database': {
                'type': 'sqlite',
                'sqlite_path': 'data/real_estate.db',
                'backup_enabled': True,
                'backup_interval_days': 7
            },
            'apis': {
                'zillow': {
                    'enabled': False,
                    'api_key': '',
                    'endpoint': 'https://api.example.com/zillow',
                    'rate_limit': 60,
                    'search_params': {
                        'locations': ['San Francisco, CA', 'New York, NY'],
                        'property_types': ['house', 'condo']
                    }
                },
                'redfin': {
                    'enabled': False,
                    'api_key': '',
                    'endpoint': 'https://api.example.com/redfin',
                    'rate_limit': 60
                },
                'mls': {
                    'enabled': False,
                    'api_key': '',
                    'endpoint': 'https://api.example.com/mls',
                    'rate_limit': 30
                },
                'custom_apis': {}
            },
            'search_criteria': {
                'price': {
                    'min': 300000,
                    'max': 800000
                },
                'bedrooms': {
                    'min': 2
                },
                'bathrooms': {
                    'min': 1.5
                },
                'square_feet': {
                    'min': 1200
                },
                'property_type': {
                    'in': ['house', 'condo', 'townhome']
                },
                'days_on_market': {
                    'max': 30
                },
                'cities': {
                    'in': ['San Francisco', 'Oakland', 'San Jose']
                }
            },
            'notifications': {
                'enabled_channels': ['email'],
                'email': {
                    'enabled': True,
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'username': '',
                    'password': '',
                    'recipients': []
                },
                'sms': {
                    'enabled': False,
                    'provider': 'twilio',
                    'account_sid': '',
                    'auth_token': '',
                    'phone_numbers': []
                },
                'slack': {
                    'enabled': False,
                    'webhook_url': '',
                    'channel': '#real-estate-alerts'
                },
                'webhook': {
                    'enabled': False,
                    'url': '',
                    'headers': {}
                }
            },
            'visualization': {
                'figure_size': [12, 8],
                'dpi': 300,
                'format': 'png',
                'style': 'seaborn-v0_8',
                'color_palette': 'husl'
            },
            'analysis': {
                'enable_market_trends': True,
                'enable_price_analysis': True,
                'enable_location_analysis': True,
                'enable_investment_analysis': True,
                'outlier_detection': True,
                'trend_window_days': 90
            },
            'scheduling': {
                'enabled': False,
                'fetch_interval_hours': 6,
                'analysis_interval_hours': 24,
                'notification_check_interval_hours': 1
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file_enabled': True,
                'file_path': 'logs/real_estate_analyzer.log',
                'max_file_size_mb': 10,
                'backup_count': 5
            }
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        return self.config.get('apis', {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self.config.get('database', {})
    
    def get_notification_config(self) -> Dict[str, Any]:
        """Get notification configuration."""
        return self.config.get('notifications', {})
    
    def get_visualization_config(self) -> Dict[str, Any]:
        """Get visualization configuration."""
        return self.config.get('visualization', {})
    
    def get_search_criteria(self) -> Dict[str, Any]:
        """Get search criteria for property matching."""
        return self.config.get('search_criteria', {})
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis configuration."""
        return self.config.get('analysis', {})
    
    def get_scheduling_config(self) -> Dict[str, Any]:
        """Get scheduling configuration."""
        return self.config.get('scheduling', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.config.get('logging', {})
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key (supports dot notation)."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            config = config.setdefault(k, {})
        
        config[keys[-1]] = value
    
    def save_config(self, file_path: Optional[str] = None) -> bool:
        """
        Save current configuration to file.
        
        Args:
            file_path: Optional file path, uses current config file if not provided
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            save_path = Path(file_path) if file_path else self.config_file_path
            
            # Create directory if it doesn't exist
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            if save_path.suffix.lower() in ['.yaml', '.yml']:
                with open(save_path, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
            elif save_path.suffix.lower() == '.json':
                with open(save_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
            else:
                logger.error(f"Unsupported file format for saving: {save_path.suffix}")
                return False
            
            logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def validate_config(self) -> List[str]:
        """
        Validate the current configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate API configuration
        apis = self.get_api_config()
        for api_name, api_config in apis.items():
            if api_name == 'custom_apis':
                continue
            
            # Handle both dict and primitive values
            if isinstance(api_config, dict):
                if api_config.get('enabled', False):
                    if not api_config.get('api_key'):
                        errors.append(f"{api_name} API is enabled but no API key provided")
                    if not api_config.get('endpoint'):
                        errors.append(f"{api_name} API is enabled but no endpoint provided")
            elif api_name.endswith('_enabled') and api_config:
                # Handle boolean enabled flags
                api_base_name = api_name.replace('_enabled', '')
                key_name = f"{api_base_name}_api_key"
                if not apis.get(key_name):
                    errors.append(f"{api_base_name} API is enabled but no API key provided")
        
        # Validate notification configuration
        notifications = self.get_notification_config()
        enabled_channels = notifications.get('enabled_channels', [])
        
        if 'email' in enabled_channels:
            email_config = notifications.get('email', {})
            if not email_config.get('username') or not email_config.get('password'):
                errors.append("Email notifications enabled but username/password not provided")
            if not email_config.get('recipients'):
                errors.append("Email notifications enabled but no recipients specified")
        
        if 'sms' in enabled_channels:
            sms_config = notifications.get('sms', {})
            provider = sms_config.get('provider')
            if provider == 'twilio':
                if not sms_config.get('account_sid') or not sms_config.get('auth_token'):
                    errors.append("Twilio SMS enabled but credentials not provided")
        
        if 'slack' in enabled_channels:
            slack_config = notifications.get('slack', {})
            if not slack_config.get('webhook_url'):
                errors.append("Slack notifications enabled but webhook URL not provided")
        
        # Validate database configuration
        db_config = self.get_database_config()
        db_type = db_config.get('type', 'sqlite')
        if db_type == 'sqlite':
            db_path = Path(db_config.get('sqlite_path', ''))
            if not db_path.parent.exists():
                try:
                    db_path.parent.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Cannot create database directory: {str(e)}")
        
        return errors
    
    def get_sample_config(self) -> str:
        """Get a sample configuration file content."""
        sample_config = self._get_default_config()
        
        # Add comments to the sample
        sample_yaml = """# Real Estate Data Analyzer Configuration
# Copy this file to config/config.yaml and customize as needed

database:
  type: sqlite
  sqlite_path: data/real_estate.db
  backup_enabled: true
  backup_interval_days: 7

apis:
  zillow:
    enabled: false
    api_key: "your_zillow_api_key_here"
    endpoint: "https://api.example.com/zillow"
    rate_limit: 60
    search_params:
      locations:
        - "San Francisco, CA"
        - "New York, NY"
      property_types:
        - "house"
        - "condo"
  
  mls:
    enabled: false
    api_key: "your_mls_api_key_here"
    endpoint: "https://api.example.com/mls"
    rate_limit: 30

search_criteria:
  price:
    min: 300000
    max: 800000
  bedrooms:
    min: 2
  bathrooms:
    min: 1.5
  square_feet:
    min: 1200
  property_type:
    in: ["house", "condo", "townhome"]
  days_on_market:
    max: 30
  cities:
    in: ["San Francisco", "Oakland", "San Jose"]

notifications:
  enabled_channels: ["email"]
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your_email@gmail.com"
    password: "your_app_password"
    recipients:
      - "alert_recipient@email.com"
  
  slack:
    enabled: false
    webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    channel: "#real-estate-alerts"

visualization:
  figure_size: [12, 8]
  dpi: 300
  format: "png"
  style: "seaborn-v0_8"

logging:
  level: "INFO"
  file_enabled: true
  file_path: "logs/real_estate_analyzer.log"
"""
        
        return sample_yaml
