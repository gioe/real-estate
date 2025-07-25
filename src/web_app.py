"""
Flask Web Application for Real Estate Deal Analysis

This module provides a streamlined web interface focused on real estate deal analysis,
allowing users to search and analyze investment opportunities.
"""

import logging
from typing import Dict, Any, List, Union
from dataclasses import asdict

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os

from src.api.rentcast_client import RentCastClient
from src.config.config_manager import ConfigManager
from src.core.database import DatabaseManager

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
            api_key=api_config.get('rentcast_api_key', ''),
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


def safe_convert_to_dict(obj) -> Union[Dict[str, Any], List[Any], Any]:
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
        # Extract key metrics with proper null handling
        score = deal.get('overall_score') or deal.get('investment_score') or 0
        cap_rate = deal.get('cap_rate') or 0
        cash_flow = deal.get('monthly_cash_flow') or 0
        confidence = deal.get('confidence') or deal.get('confidence_score') or 0
        
        # Ensure all numeric values are numbers, not None
        score = float(score) if score is not None else 0.0
        cap_rate = float(cap_rate) if cap_rate is not None else 0.0
        cash_flow = float(cash_flow) if cash_flow is not None else 0.0
        confidence = float(confidence) if confidence is not None else 0.0
        
        # Property details
        property_type = deal.get('property_type', 'Property')
        bedrooms = deal.get('bedrooms') or 0
        bathrooms = deal.get('bathrooms') or 0
        sqft = deal.get('square_footage') or deal.get('square_feet') or 0
        
        # Financial details with null handling
        asking_price = deal.get('asking_price') or deal.get('price') or deal.get('purchase_price') or 0
        estimated_value = deal.get('estimated_value') or 0
        estimated_rent = deal.get('estimated_rent') or 0
        deal_type = deal.get('deal_type') or deal.get('source') or 'investment'
        
        # Ensure financial values are numbers
        asking_price = float(asking_price) if asking_price is not None else 0.0
        estimated_value = float(estimated_value) if estimated_value is not None else 0.0
        estimated_rent = float(estimated_rent) if estimated_rent is not None else 0.0
        
        # Start building description
        description_parts = []
        
        # Property overview with null checks
        if bedrooms and bathrooms:
            property_desc = f"{int(bedrooms)}BR/{bathrooms}BA {property_type.lower()}"
        else:
            property_desc = property_type
            
        if sqft and sqft > 0:
            property_desc += f" ({int(sqft):,} sqft)"
            
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
            
        if financial_highlights:
            description_parts.append(f"featuring {' and '.join(financial_highlights)}.")
        
        # Investment details
        investment_highlights = []
        
        if asking_price and estimated_value:
            equity_gain = estimated_value - asking_price
            if equity_gain > 50000:
                investment_highlights.append(f"immediate ${equity_gain:,.0f} equity gain")
            elif equity_gain > 20000:
                investment_highlights.append(f"${equity_gain:,.0f} potential equity")
        
        if estimated_rent and asking_price:
            rent_to_price_ratio = (estimated_rent * 12) / asking_price if asking_price > 0 else 0
            if rent_to_price_ratio >= 0.12:
                investment_highlights.append(f"exceptional {rent_to_price_ratio:.1%} rent-to-price ratio")
            elif rent_to_price_ratio >= 0.10:
                investment_highlights.append(f"strong {rent_to_price_ratio:.1%} rent-to-price ratio")
        
        if investment_highlights:
            description_parts.append(f"This property offers {', '.join(investment_highlights)}.")
        
        # Market context and recommendation
        if confidence >= 90:
            description_parts.append(f"🎯 **HIGH CONFIDENCE** ({confidence:.0f}%) - Data backed by comprehensive market analysis.")
        elif confidence >= 80:
            description_parts.append(f"📈 **STRONG CONFIDENCE** ({confidence:.0f}%) - Reliable data supports this opportunity.")
        elif confidence >= 70:
            description_parts.append(f"📊 **GOOD CONFIDENCE** ({confidence:.0f}%) - Solid data foundation.")
        
        # Call to action based on score
        if score >= 85:
            description_parts.append("⚡ **IMMEDIATE ACTION RECOMMENDED** - This exceptional deal won't last long in today's market.")
        elif score >= 80:
            description_parts.append("🏃 **QUICK EVALUATION SUGGESTED** - Strong fundamentals warrant serious consideration.")
        elif score >= 75:
            description_parts.append("📋 **WORTH INVESTIGATING** - Good opportunity for detailed due diligence.")
        else:
            description_parts.append("📝 **REVIEW AND ANALYZE** - Consider alongside your investment criteria.")
        
        return " ".join(description_parts)
        
    except Exception as e:
        logger.warning(f"Error generating agent description: {e}")
        return f"Investment opportunity with {score:.1f}/100 score and {cap_rate:.1f}% cap rate."


# Routes
@app.route('/')
def index():
    """Redirect to deals search page."""
    return redirect(url_for('deals_search'))


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
