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
from src.core.database import DatabaseManager
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
database_manager = None


def init_app():
    """Initialize the application with configuration and API client."""
    global config_manager, rentcast_client, database_manager
    
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
        
        # Initialize Database Manager
        db_config = config_manager.get_database_config()
        database_manager = DatabaseManager(db_config)
        
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


def generate_agent_description(deal: Dict[str, Any]) -> str:
    """
    Generate a human-readable description from a real estate agent's perspective.
    
    Args:
        deal: Dictionary containing deal data
        
    Returns:
        Human-readable description of the investment opportunity
    """
    try:
        # Extract key metrics
        score = deal.get('overall_score', deal.get('investment_score', 0))
        cap_rate = deal.get('cap_rate', 0)
        cash_flow = deal.get('monthly_cash_flow', 0)
        confidence = deal.get('confidence', deal.get('confidence_score', 0))
        
        # Property details
        property_type = deal.get('property_type', 'Property')
        bedrooms = deal.get('bedrooms', 0)
        bathrooms = deal.get('bathrooms', 0)
        sqft = deal.get('square_footage', deal.get('square_feet', 0))
        
        # Financial details
        asking_price = deal.get('asking_price', deal.get('price', deal.get('purchase_price', 0)))
        estimated_value = deal.get('estimated_value', 0)
        estimated_rent = deal.get('estimated_rent', 0)
        deal_type = deal.get('deal_type', deal.get('source', 'investment'))
        
        # Start building description
        description_parts = []
        
        # Property overview
        if bedrooms and bathrooms:
            property_desc = f"{bedrooms}BR/{bathrooms}BA {property_type.lower()}"
        else:
            property_desc = property_type
            
        if sqft:
            property_desc += f" ({sqft:,} sqft)"
            
        # Score-based opening
        if score >= 90:
            description_parts.append(f"🌟 **EXCEPTIONAL OPPORTUNITY** - This {property_desc} scores {score:.1f}/100")
        elif score >= 85:
            description_parts.append(f"⭐ **EXCELLENT DEAL** - This {property_desc} scores {score:.1f}/100")
        elif score >= 80:
            description_parts.append(f"✅ **STRONG INVESTMENT** - This {property_desc} scores {score:.1f}/100")
        elif score >= 75:
            description_parts.append(f"👍 **SOLID OPPORTUNITY** - This {property_desc} scores {score:.1f}/100")
        else:
            description_parts.append(f"📊 **INVESTMENT PROSPECT** - This {property_desc} scores {score:.1f}/100")
            
        # Financial analysis
        financial_highlights = []
        
        if cap_rate >= 10:
            financial_highlights.append(f"outstanding {cap_rate:.1f}% cap rate")
        elif cap_rate >= 8:
            financial_highlights.append(f"strong {cap_rate:.1f}% cap rate")
        elif cap_rate >= 6:
            financial_highlights.append(f"solid {cap_rate:.1f}% cap rate")
        elif cap_rate > 0:
            financial_highlights.append(f"{cap_rate:.1f}% cap rate")
            
        if cash_flow >= 1000:
            financial_highlights.append(f"excellent ${cash_flow:,.0f}/month cash flow")
        elif cash_flow >= 500:
            financial_highlights.append(f"strong ${cash_flow:,.0f}/month cash flow")
        elif cash_flow >= 200:
            financial_highlights.append(f"positive ${cash_flow:,.0f}/month cash flow")
        elif cash_flow > 0:
            financial_highlights.append(f"${cash_flow:,.0f}/month cash flow")
        elif cash_flow < 0:
            financial_highlights.append(f"${abs(cash_flow):,.0f}/month negative cash flow")
            
        if financial_highlights:
            description_parts.append(f"Features {' and '.join(financial_highlights)}.")
            
        # Value analysis
        if asking_price and estimated_value:
            value_diff_pct = ((estimated_value - asking_price) / asking_price) * 100
            if value_diff_pct >= 10:
                description_parts.append(f"💎 **UNDERVALUED** - Listed at ${asking_price:,} vs estimated value of ${estimated_value:,} ({value_diff_pct:+.1f}%)")
            elif value_diff_pct >= 5:
                description_parts.append(f"💰 **GOOD VALUE** - Listed at ${asking_price:,} vs estimated value of ${estimated_value:,} ({value_diff_pct:+.1f}%)")
            elif value_diff_pct >= 0:
                description_parts.append(f"✅ **FAIR VALUE** - Listed at ${asking_price:,} vs estimated value of ${estimated_value:,} ({value_diff_pct:+.1f}%)")
            else:
                description_parts.append(f"⚠️ **PREMIUM PRICING** - Listed at ${asking_price:,} vs estimated value of ${estimated_value:,} ({value_diff_pct:+.1f}%)")
        elif asking_price:
            description_parts.append(f"Listed at ${asking_price:,}")
            
        # Rental potential
        if estimated_rent and asking_price:
            monthly_yield = (estimated_rent / asking_price) * 100
            if monthly_yield >= 1.5:
                description_parts.append(f"🏠 **EXCELLENT RENTAL YIELD** - Estimated rent of ${estimated_rent:,}/month ({monthly_yield:.2f}% monthly yield)")
            elif monthly_yield >= 1.0:
                description_parts.append(f"🏠 **STRONG RENTAL POTENTIAL** - Estimated rent of ${estimated_rent:,}/month ({monthly_yield:.2f}% monthly yield)")
            elif monthly_yield >= 0.8:
                description_parts.append(f"🏠 **DECENT RENTAL INCOME** - Estimated rent of ${estimated_rent:,}/month ({monthly_yield:.2f}% monthly yield)")
            elif estimated_rent:
                description_parts.append(f"🏠 **RENTAL POTENTIAL** - Estimated rent of ${estimated_rent:,}/month")
                
        # Investment strategy
        strategy_notes = []
        if deal_type == 'flip':
            strategy_notes.append("🔨 **FLIP CANDIDATE** - Ideal for renovation and resale")
        elif deal_type == 'buy_and_hold':
            strategy_notes.append("📈 **BUY & HOLD** - Perfect for long-term rental income")
        elif deal_type == 'luxury_hold':
            strategy_notes.append("💎 **LUXURY RENTAL** - High-end investment property")
            
        if cap_rate >= 8 and cash_flow >= 500:
            strategy_notes.append("💰 **CASH COW** - Strong immediate returns")
        elif score >= 85:
            strategy_notes.append("⭐ **PORTFOLIO BUILDER** - Excellent addition to any investment portfolio")
            
        if strategy_notes:
            description_parts.append(" ".join(strategy_notes))
            
        # Confidence and risk assessment
        if confidence >= 0.9:
            description_parts.append("🎯 **HIGH CONFIDENCE** - Very reliable data analysis")
        elif confidence >= 0.8:
            description_parts.append("✅ **RELIABLE DATA** - Good confidence in projections")
        elif confidence >= 0.7:
            description_parts.append("📊 **MODERATE CONFIDENCE** - Decent data reliability")
        elif confidence > 0:
            description_parts.append("⚠️ **LIMITED DATA** - Lower confidence in projections")
            
        # Final recommendation
        if score >= 90 and cap_rate >= 8:
            description_parts.append("🚀 **AGENT RECOMMENDATION: IMMEDIATE ACTION** - This is a rare find that won't last long!")
        elif score >= 85:
            description_parts.append("👨‍💼 **AGENT RECOMMENDATION: HIGHLY RECOMMENDED** - Strong investment opportunity")
        elif score >= 80:
            description_parts.append("👨‍💼 **AGENT RECOMMENDATION: RECOMMENDED** - Solid investment choice")
        elif score >= 75:
            description_parts.append("👨‍💼 **AGENT RECOMMENDATION: CONSIDER** - Worth further analysis")
        else:
            description_parts.append("👨‍💼 **AGENT RECOMMENDATION: PROCEED WITH CAUTION** - Requires careful due diligence")
            
        return " ".join(description_parts)
        
    except Exception as e:
        logger.warning(f"Error generating agent description: {e}")
        return "Investment opportunity with detailed analysis available. Contact agent for more information."


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


@app.route('/deals')
def deals_search():
    """Deals search page."""
    return render_template('deals_search.html')


@app.route('/api/deals/search', methods=['POST'])
def search_deals():
    """API endpoint for searching deals by zip code."""
    try:
        data = request.get_json()
        
        # Extract search parameters
        zip_code = data.get('zip_code')
        min_score = float(data.get('min_score', 70.0))
        min_cap_rate = float(data.get('min_cap_rate', 0.0))
        min_cash_flow = float(data.get('min_cash_flow', 0.0))
        limit = int(data.get('limit', 20))
        
        deals = []
        
        if not database_manager:
            return jsonify({
                'success': False,
                'error': 'Database not initialized'
            }), 500
        
        # Get best deals from deal_insights table
        if zip_code:
            best_deals = database_manager.get_best_deals(
                zip_code=zip_code,
                min_score=min_score,
                limit=limit
            )
            deals.extend(best_deals)
        
        # Also get investment opportunities
        investment_opportunities = database_manager.get_top_investment_opportunities(
            min_cap_rate=min_cap_rate,
            min_cash_flow=min_cash_flow,
            limit=limit
        )
        
        # Filter by zip code if specified
        if zip_code:
            investment_opportunities = [
                opp for opp in investment_opportunities 
                if opp.get('zip_code') == zip_code or 
                   (opp.get('address') and zip_code in str(opp.get('address', '')))
            ]
        
        # Combine and deduplicate deals
        all_deals = []
        seen_properties = set()
        
        # Add best deals first
        for deal in deals:
            # For deal_insights, use analysis_id as unique identifier
            deal_id = deal.get('property_id') or deal.get('analysis_id') or deal.get('id')
            if deal_id and deal_id not in seen_properties:
                deal['source'] = 'deal_analysis'
                deal['agent_description'] = generate_agent_description(deal)
                all_deals.append(deal)
                seen_properties.add(deal_id)
        
        # Add investment opportunities
        for opp in investment_opportunities:
            # For investment_analysis, use property_id as unique identifier
            opp_id = opp.get('property_id') or opp.get('id')
            if opp_id and opp_id not in seen_properties:
                opp['source'] = 'investment_analysis'
                opp['agent_description'] = generate_agent_description(opp)
                all_deals.append(opp)
                seen_properties.add(opp_id)
        
        # Sort by score/investment_score
        all_deals.sort(key=lambda x: x.get('overall_score', x.get('investment_score', 0)), reverse=True)
        
        return jsonify({
            'success': True,
            'data': all_deals[:limit],
            'total_count': len(all_deals),
            'zip_code': zip_code
        })
        
    except Exception as e:
        logger.error(f"Error searching deals: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/deals/summary/<zip_code>')
def get_deals_summary(zip_code):
    """Get summary statistics for deals in a zip code."""
    try:
        if not database_manager:
            return jsonify({
                'success': False,
                'error': 'Database not initialized'
            }), 500
        
        # Get all deals for the zip code
        deals = database_manager.get_best_deals(zip_code=zip_code, min_score=0.0, limit=100)
        investment_opportunities = database_manager.get_top_investment_opportunities(
            min_cap_rate=0.0, min_cash_flow=0.0, limit=100
        )
        
        # Filter investment opportunities by zip code
        investment_opportunities = [
            opp for opp in investment_opportunities 
            if opp.get('zip_code') == zip_code or 
               (opp.get('address') and zip_code in str(opp.get('address', '')))
        ]
        
        # Calculate summary statistics
        total_deals = len(deals)
        total_investments = len(investment_opportunities)
        
        # Deal score statistics
        deal_scores = [deal.get('overall_score', 0) for deal in deals if deal.get('overall_score')]
        avg_deal_score = sum(deal_scores) / len(deal_scores) if deal_scores else 0
        
        # Investment statistics
        cap_rates = [inv.get('cap_rate', 0) for inv in investment_opportunities if inv.get('cap_rate')]
        avg_cap_rate = sum(cap_rates) / len(cap_rates) if cap_rates else 0
        
        cash_flows = [inv.get('monthly_cash_flow', 0) for inv in investment_opportunities if inv.get('monthly_cash_flow')]
        avg_cash_flow = sum(cash_flows) / len(cash_flows) if cash_flows else 0
        
        # Get market trends for context
        market_trends = database_manager.get_market_trends(zip_code, months_back=6)
        
        summary = {
            'zip_code': zip_code,
            'total_deals': total_deals,
            'total_investment_opportunities': total_investments,
            'avg_deal_score': round(avg_deal_score, 1),
            'avg_cap_rate': round(avg_cap_rate, 2),
            'avg_monthly_cash_flow': round(avg_cash_flow, 0),
            'high_score_deals': len([d for d in deals if d.get('overall_score', 0) >= 80]),
            'market_trends': market_trends
        }
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting deals summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
