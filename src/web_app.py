"""
Flask Web Application for RentCast API Interaction

This module provides a web interface for interacting with the RentCast API,
allowing users to search properties, listings, get AVM values, and view market data.
"""

import logging
import json
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dataclasses import asdict

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
from pathlib import Path

from src.api.rentcast_client import RentCastClient
from src.config.config_manager import ConfigManager
from src.schemas.rentcast_schemas import (
    Property, PropertiesResponse, PropertyListing, ListingsResponse,
    AVMValueResponse, AVMRentResponse, MarketStatistics
)
from src.api.rentcast_errors import RentCastAPIError, RentCastNoResultsError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-change-this')

# Global variables for configuration and client
config_manager = None
rentcast_client = None


def init_app():
    """Initialize the application with configuration and API client."""
    global config_manager, rentcast_client
    
    try:
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
        config_manager = ConfigManager(config_path)
        
        # Initialize RentCast client
        api_config = config_manager.get_api_config()
        rentcast_client = RentCastClient(
            api_key=api_config.get('rentcast_api_key'),
            base_url=api_config.get('rentcast_endpoint', 'https://api.rentcast.io/v1'),
            rate_limit=api_config.get('rentcast_rate_limit', 20)
        )
        
        logger.info("Flask app initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize app: {e}")
        raise


def safe_convert_to_dict(obj) -> Dict[str, Any]:
    """Safely convert dataclass objects to dictionaries for JSON serialization."""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, '__dict__'):
        return asdict(obj)
    elif isinstance(obj, list):
        return [safe_convert_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: safe_convert_to_dict(v) for k, v in obj.items()}
    else:
        return obj


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/properties')
def properties_search():
    """Properties search page."""
    return render_template('properties_search.html')


@app.route('/api/properties/search', methods=['POST'])
def search_properties():
    """API endpoint for searching properties."""
    try:
        data = request.get_json()
        
        # Extract search parameters
        params = {}
        
        # Address search
        if data.get('address'):
            params['address'] = data['address']
        
        # Location search
        if data.get('city'):
            params['city'] = data['city']
        if data.get('state'):
            params['state'] = data['state']
        if data.get('zipcode'):
            params['zipcode'] = data['zipcode']
        
        # Geographical search
        if data.get('latitude') and data.get('longitude'):
            params['latitude'] = float(data['latitude'])
            params['longitude'] = float(data['longitude'])
        if data.get('radius'):
            params['radius'] = float(data['radius'])
        
        # Property filters
        if data.get('property_type'):
            params['propertyType'] = data['property_type']
        if data.get('bedrooms'):
            params['bedrooms'] = int(data['bedrooms'])
        if data.get('bathrooms'):
            params['bathrooms'] = float(data['bathrooms'])
        if data.get('min_sqft'):
            params['minSquareFootage'] = int(data['min_sqft'])
        if data.get('max_sqft'):
            params['maxSquareFootage'] = int(data['max_sqft'])
        if data.get('min_year_built'):
            params['minYearBuilt'] = int(data['min_year_built'])
        if data.get('max_year_built'):
            params['maxYearBuilt'] = int(data['max_year_built'])
        
        # Pagination
        offset = data.get('offset', 0)
        limit = data.get('limit', 20)
        if offset:
            params['offset'] = offset
        if limit:
            params['limit'] = limit
        
        # Make API call
        response = rentcast_client.search_properties(**params)
        
        # Convert response to dict for JSON serialization
        result = safe_convert_to_dict(response)
        
        return jsonify({
            'success': True,
            'data': result,
            'total_count': getattr(response, 'total_count', len(response.properties) if hasattr(response, 'properties') else 1)
        })
        
    except RentCastNoResultsError:
        return jsonify({
            'success': True,
            'data': {'properties': []},
            'total_count': 0,
            'message': 'No properties found matching your criteria'
        })
        
    except RentCastAPIError as e:
        logger.error(f"RentCast API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'recommendation': getattr(e, 'recommendation', 'Please check your search parameters and try again.')
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in property search: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500


@app.route('/listings')
def listings_search():
    """Listings search page."""
    return render_template('listings_search.html')


@app.route('/api/listings/search', methods=['POST'])
def search_listings():
    """API endpoint for searching listings (both sale and rental)."""
    try:
        data = request.get_json()
        listing_type = data.get('listing_type', 'sale')  # 'sale' or 'rental'
        
        # Extract search parameters
        params = {}
        
        # Location search
        if data.get('city'):
            params['city'] = data['city']
        if data.get('state'):
            params['state'] = data['state']
        if data.get('zipcode'):
            params['zipcode'] = data['zipcode']
        
        # Geographical search
        if data.get('latitude') and data.get('longitude'):
            params['latitude'] = float(data['latitude'])
            params['longitude'] = float(data['longitude'])
        if data.get('radius'):
            params['radius'] = float(data['radius'])
        
        # Property filters
        if data.get('property_type'):
            params['propertyType'] = data['property_type']
        if data.get('bedrooms'):
            params['bedrooms'] = int(data['bedrooms'])
        if data.get('bathrooms'):
            params['bathrooms'] = float(data['bathrooms'])
        if data.get('min_sqft'):
            params['minSquareFootage'] = int(data['min_sqft'])
        if data.get('max_sqft'):
            params['maxSquareFootage'] = int(data['max_sqft'])
        
        # Price/rent filters
        if listing_type == 'sale':
            if data.get('min_price'):
                params['minPrice'] = float(data['min_price'])
            if data.get('max_price'):
                params['maxPrice'] = float(data['max_price'])
        else:  # rental
            if data.get('min_rent'):
                params['minRent'] = float(data['min_rent'])
            if data.get('max_rent'):
                params['maxRent'] = float(data['max_rent'])
        
        # Days on market filter
        if data.get('max_days_on_market'):
            params['maxDaysOnMarket'] = int(data['max_days_on_market'])
        
        # Pagination
        offset = data.get('offset', 0)
        limit = data.get('limit', 20)
        if offset:
            params['offset'] = offset
        if limit:
            params['limit'] = limit
        
        # Make API call based on listing type
        if listing_type == 'sale':
            response = rentcast_client.get_listings_sale(**params)
        else:
            response = rentcast_client.get_listings_rental_long_term(**params)
        
        # Convert response to dict for JSON serialization
        result = safe_convert_to_dict(response)
        
        return jsonify({
            'success': True,
            'data': result,
            'listing_type': listing_type
        })
        
    except RentCastNoResultsError:
        return jsonify({
            'success': True,
            'data': {'listings': []},
            'total_count': 0,
            'message': 'No listings found matching your criteria'
        })
        
    except RentCastAPIError as e:
        logger.error(f"RentCast API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'recommendation': getattr(e, 'recommendation', 'Please check your search parameters and try again.')
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in listings search: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500


@app.route('/avm')
def avm_search():
    """AVM (Automated Valuation Model) search page."""
    return render_template('avm_search.html')


@app.route('/api/avm/value', methods=['POST'])
def get_avm_value():
    """API endpoint for getting property value estimates."""
    try:
        data = request.get_json()
        
        # Extract parameters
        params = {}
        
        if data.get('address'):
            params['address'] = data['address']
        if data.get('zipcode'):
            params['zipcode'] = data['zipcode']
        if data.get('latitude') and data.get('longitude'):
            params['latitude'] = float(data['latitude'])
            params['longitude'] = float(data['longitude'])
        
        # Property characteristics for better estimates
        if data.get('bedrooms'):
            params['bedrooms'] = int(data['bedrooms'])
        if data.get('bathrooms'):
            params['bathrooms'] = float(data['bathrooms'])
        if data.get('square_footage'):
            params['squareFootage'] = int(data['square_footage'])
        if data.get('property_type'):
            params['propertyType'] = data['property_type']
        
        # Comparables options
        if data.get('comparables_count'):
            params['compCount'] = int(data['comparables_count'])
        
        # Make API call
        response = rentcast_client.get_avm_value(**params)
        
        # Convert response to dict for JSON serialization
        result = safe_convert_to_dict(response)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except RentCastNoResultsError:
        return jsonify({
            'success': False,
            'error': 'No value estimate available for this property',
            'message': 'Unable to generate a value estimate. This could be due to insufficient comparable data in the area.'
        })
        
    except RentCastAPIError as e:
        logger.error(f"RentCast API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'recommendation': getattr(e, 'recommendation', 'Please check your property details and try again.')
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in AVM value request: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500


@app.route('/api/avm/rent', methods=['POST'])
def get_avm_rent():
    """API endpoint for getting rental estimates."""
    try:
        data = request.get_json()
        
        # Extract parameters
        params = {}
        
        if data.get('address'):
            params['address'] = data['address']
        if data.get('zipcode'):
            params['zipcode'] = data['zipcode']
        if data.get('latitude') and data.get('longitude'):
            params['latitude'] = float(data['latitude'])
            params['longitude'] = float(data['longitude'])
        
        # Property characteristics for better estimates
        if data.get('bedrooms'):
            params['bedrooms'] = int(data['bedrooms'])
        if data.get('bathrooms'):
            params['bathrooms'] = float(data['bathrooms'])
        if data.get('square_footage'):
            params['squareFootage'] = int(data['square_footage'])
        if data.get('property_type'):
            params['propertyType'] = data['property_type']
        
        # Comparables options
        if data.get('comparables_count'):
            params['compCount'] = int(data['comparables_count'])
        
        # Make API call
        response = rentcast_client.get_avm_rent_long_term(**params)
        
        # Convert response to dict for JSON serialization
        result = safe_convert_to_dict(response)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except RentCastNoResultsError:
        return jsonify({
            'success': False,
            'error': 'No rental estimate available for this property',
            'message': 'Unable to generate a rental estimate. This could be due to insufficient comparable rental data in the area.'
        })
        
    except RentCastAPIError as e:
        logger.error(f"RentCast API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'recommendation': getattr(e, 'recommendation', 'Please check your property details and try again.')
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in AVM rent request: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500


@app.route('/markets')
def markets_search():
    """Market statistics search page."""
    return render_template('markets_search.html')


@app.route('/api/markets/search', methods=['POST'])
def search_markets():
    """API endpoint for getting market statistics."""
    try:
        data = request.get_json()
        
        # Extract parameters
        params = {}
        
        # Location parameters
        if data.get('city'):
            params['city'] = data['city']
        if data.get('state'):
            params['state'] = data['state']
        if data.get('zipcode'):
            params['zipcode'] = data['zipcode']
        
        # Make API call
        response = rentcast_client.get_markets(**params)
        
        # Convert response to dict for JSON serialization
        result = safe_convert_to_dict(response)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except RentCastNoResultsError:
        return jsonify({
            'success': False,
            'error': 'No market data available for this location',
            'message': 'Market statistics are not available for the specified location.'
        })
        
    except RentCastAPIError as e:
        logger.error(f"RentCast API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'recommendation': getattr(e, 'recommendation', 'Please check your location and try again.')
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in markets request: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }), 500


@app.route('/property/<property_id>')
def property_details(property_id):
    """Property details page."""
    try:
        property_data = rentcast_client.get_property_details(property_id)
        return render_template('property_details.html', property=safe_convert_to_dict(property_data))
    except RentCastAPIError as e:
        flash(f"Error loading property details: {e}", 'error')
        return redirect(url_for('properties_search'))


@app.route('/listing/<listing_type>/<listing_id>')
def listing_details(listing_type, listing_id):
    """Listing details page."""
    try:
        if listing_type == 'sale':
            listing_data = rentcast_client.get_listing_sale_details(listing_id)
        else:
            listing_data = rentcast_client.get_listing_rental_long_term_details(listing_id)
        
        return render_template('listing_details.html', 
                             listing=safe_convert_to_dict(listing_data),
                             listing_type=listing_type)
    except RentCastAPIError as e:
        flash(f"Error loading listing details: {e}", 'error')
        return redirect(url_for('listings_search'))


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500


def create_app():
    """Application factory function."""
    init_app()
    return app


if __name__ == '__main__':
    # Initialize the app
    init_app()
    
    # Run the development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('FLASK_PORT', 5001)),  # Changed default from 5000 to 5001
        debug=bool(os.environ.get('FLASK_DEBUG', True))
    )
