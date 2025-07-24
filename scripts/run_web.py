#!/usr/bin/env python3
"""
Simple script to run the Flask web application
"""

import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import and run the web app
from src.web_app import create_app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('FLASK_PORT', 5001))  # Changed default from 5000 to 5001
    print("🏠 Real Estate Deal Analyzer starting...")
    print(f"📡 Web interface: http://localhost:{port}")
    print("💰 Investment deals and analysis tools available")
    print("🔍 Use Ctrl+C to stop the server")
    
    try:
        app.run(
            host='0.0.0.0',
            port=port,
            debug=bool(os.environ.get('FLASK_DEBUG', True))
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Real Estate Deal Analyzer...")
