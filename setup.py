#!/usr/bin/env python3
"""
Setup Script for Real Estate Data Analyzer

This script helps set up the project by:
1. Installing dependencies
2. Creating necessary directories
3. Setting up configuration files
4. Initializing the database
"""

import subprocess
import sys
import os
from pathlib import Path


def install_dependencies():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    return True


def create_directories():
    """Create necessary directories."""
    print("Creating project directories...")
    directories = [
        "data",
        "output", 
        "logs",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")


def setup_config():
    """Set up configuration files."""
    print("Setting up configuration...")
    
    # Copy .env.example to .env if it doesn't exist
    env_example = Path("config/.env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your API keys and credentials")
    
    config_file = Path("config/config.yaml")
    if config_file.exists():
        print("✅ Configuration file found")
    else:
        print("⚠️  No configuration file found - using defaults")


def initialize_database():
    """Initialize the database."""
    print("Initializing database...")
    try:
        # Import here to avoid import errors if dependencies aren't installed
        sys.path.append("src")
        from config_manager import ConfigManager
        from database import DatabaseManager
        
        config = ConfigManager()
        db = DatabaseManager(config.get_database_config())
        print("✅ Database initialized successfully")
        
        # Display database stats
        stats = db.get_database_stats()
        print(f"📊 Database stats: {stats}")
        
    except Exception as e:
        print(f"❌ Failed to initialize database: {str(e)}")
        return False
    return True


def run_test():
    """Run a basic test to ensure everything works."""
    print("Running basic test...")
    try:
        subprocess.check_call([sys.executable, "main.py", "--help"])
        print("✅ Basic test passed - application can start")
    except subprocess.CalledProcessError:
        print("❌ Basic test failed")
        return False
    return True


def main():
    """Main setup function."""
    print("🏠 Real Estate Data Analyzer Setup")
    print("=" * 40)
    
    success = True
    
    # Step 1: Install dependencies
    if not install_dependencies():
        success = False
    
    # Step 2: Create directories
    create_directories()
    
    # Step 3: Setup configuration
    setup_config()
    
    # Step 4: Initialize database
    if not initialize_database():
        success = False
    
    # Step 5: Run basic test
    if not run_test():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Setup completed successfully!")
        print("\n📚 Next steps:")
        print("1. Edit .env file with your API keys")
        print("2. Customize config/config.yaml for your preferences")
        print("3. Run: python main.py --mode fetch")
    else:
        print("⚠️  Setup completed with some errors")
        print("Please check the error messages above and fix any issues")


if __name__ == "__main__":
    main()
