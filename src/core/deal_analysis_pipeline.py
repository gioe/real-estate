"""
Real Estate Deal Analysis Pipeline

This module provides a comprehensive pipeline for analyzing real estate deals,
storing results in a database, and retrieving historical analyses.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import asdict

from .deal_analyzer import BasicDealAnalyzer, DealScore
from .database import DatabaseManager
from ..schemas.rentcast_schemas import PropertyListing, AVMValueResponse, MarketStatistics
from ..api.rentcast_client import RentCastClient
from ..config.config_manager import ConfigManager


class DealAnalysisPipeline:
    """
    Orchestrates the complete deal analysis workflow:
    1. Fetches property, valuation, and market data
    2. Runs deal analysis
    3. Stores results in database
    4. Provides retrieval and comparison capabilities
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.db_manager = DatabaseManager(config_manager)
        self.deal_analyzer = BasicDealAnalyzer()
        self.rentcast_client = RentCastClient(config_manager)
        
        # Ensure database tables exist
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables for deal analysis storage."""
        try:
            self.db_manager.create_deal_analysis_tables()
            self.logger.info("Deal analysis database tables initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize database tables: {e}")
            raise
    
    def analyze_property(self, 
                        property_listing: PropertyListing,
                        store_results: bool = True) -> DealScore:
        """
        Run complete analysis pipeline for a single property.
        
        Args:
            property_listing: The property to analyze
            store_results: Whether to store results in database
            
        Returns:
            DealScore with complete analysis
        """
        analysis_id = None
        
        try:
            # Generate unique analysis ID
            analysis_id = self._generate_analysis_id(property_listing)
            
            self.logger.info(f"Starting deal analysis for {property_listing.formattedAddress}")
            
            # Step 1: Fetch AVM valuation data
            avm_value = None
            try:
                avm_value = self.rentcast_client.get_avm_value(property_listing.formattedAddress)
                self.logger.debug(f"Retrieved AVM value: ${avm_value.value:,}" if avm_value else "No AVM data")
            except Exception as e:
                self.logger.warning(f"Failed to fetch AVM data: {e}")
            
            # Step 2: Fetch market statistics
            market_stats = None
            try:
                if property_listing.zipCode:
                    market_stats = self.rentcast_client.get_market_statistics(property_listing.zipCode)
                    self.logger.debug("Retrieved market statistics")
            except Exception as e:
                self.logger.warning(f"Failed to fetch market stats: {e}")
            
            # Step 3: Run deal analysis
            deal_score = self.deal_analyzer.analyze_deal(
                property_listing, 
                avm_value, 
                market_stats
            )
            
            self.logger.info(
                f"Analysis complete: {deal_score.deal_type} "
                f"(Score: {deal_score.overall_score}/100)"
            )
            
            # Step 4: Store results in database
            if store_results:
                self._store_analysis_results(
                    analysis_id,
                    property_listing,
                    avm_value,
                    market_stats,
                    deal_score
                )
            
            return deal_score
            
        except Exception as e:
            self.logger.error(f"Analysis pipeline failed for {analysis_id}: {e}")
            raise
    
    def analyze_property_list(self, 
                             properties: List[PropertyListing],
                             filter_good_deals: bool = True) -> List[Dict[str, Any]]:
        """
        Analyze multiple properties and optionally filter for good deals.
        
        Args:
            properties: List of properties to analyze
            filter_good_deals: Only return properties with Good/Excellent scores
            
        Returns:
            List of analysis results with property and score data
        """
        results = []
        
        for i, property_listing in enumerate(properties, 1):
            try:
                self.logger.info(f"Analyzing property {i}/{len(properties)}")
                
                deal_score = self.analyze_property(property_listing)
                
                # Apply filtering if requested
                if filter_good_deals and deal_score.deal_type not in ["Excellent", "Good"]:
                    continue
                
                results.append({
                    'property': property_listing,
                    'deal_score': deal_score,
                    'analysis_date': datetime.now(),
                    'recommendation': self._generate_recommendation(deal_score)
                })
                
            except Exception as e:
                self.logger.error(f"Failed to analyze property {i}: {e}")
                continue
        
        # Sort by overall score (best deals first)
        results.sort(key=lambda x: x['deal_score'].overall_score, reverse=True)
        
        self.logger.info(f"Analysis complete: {len(results)} properties analyzed")
        return results
    
    def get_analysis_history(self, 
                           property_address: Optional[str] = None,
                           deal_type: Optional[str] = None,
                           days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Retrieve historical deal analyses from database.
        
        Args:
            property_address: Filter by specific property address
            deal_type: Filter by deal quality ("Excellent", "Good", etc.)
            days_back: Number of days back to search
            
        Returns:
            List of historical analysis records
        """
        try:
            return self.db_manager.get_deal_analyses(
                property_address=property_address,
                deal_type=deal_type,
                days_back=days_back
            )
        except Exception as e:
            self.logger.error(f"Failed to retrieve analysis history: {e}")
            return []
    
    def get_best_deals(self, 
                      zip_code: Optional[str] = None,
                      min_score: float = 70.0,
                      limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get the best deals from recent analyses.
        
        Args:
            zip_code: Filter by specific zip code
            min_score: Minimum deal score threshold
            limit: Maximum number of results
            
        Returns:
            List of best deal records
        """
        try:
            return self.db_manager.get_best_deals(
                zip_code=zip_code,
                min_score=min_score,
                limit=limit
            )
        except Exception as e:
            self.logger.error(f"Failed to retrieve best deals: {e}")
            return []
    
    def compare_property_to_market(self, property_listing: PropertyListing) -> Dict[str, Any]:
        """
        Compare a property's deal score to similar properties in the market.
        
        Args:
            property_listing: Property to compare
            
        Returns:
            Comparison analysis with market context
        """
        # Analyze the target property
        deal_score = self.analyze_property(property_listing, store_results=False)
        
        # Get similar properties from database
        similar_deals = self.db_manager.get_similar_properties(
            zip_code=property_listing.zipCode,
            property_type=property_listing.propertyType,
            bedrooms=property_listing.bedrooms,
            price_range_pct=20  # +/- 20% price range
        )
        
        # Calculate market comparison metrics
        if similar_deals:
            similar_scores = [deal['overall_score'] for deal in similar_deals]
            avg_market_score = sum(similar_scores) / len(similar_scores)
            score_percentile = len([s for s in similar_scores if s <= deal_score.overall_score]) / len(similar_scores) * 100
        else:
            avg_market_score = None
            score_percentile = None
        
        return {
            'property': property_listing,
            'deal_score': deal_score,
            'market_context': {
                'avg_market_score': avg_market_score,
                'score_percentile': score_percentile,
                'similar_properties_count': len(similar_deals),
                'comparison': 'Above Average' if score_percentile and score_percentile > 70 else
                             'Average' if score_percentile and score_percentile > 30 else
                             'Below Average' if score_percentile else 'Insufficient Data'
            }
        }
    
    def _generate_analysis_id(self, property_listing: PropertyListing) -> str:
        """Generate unique analysis ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        address_hash = abs(hash(property_listing.formattedAddress)) % 10000
        return f"analysis_{timestamp}_{address_hash:04d}"
    
    def _store_analysis_results(self,
                               analysis_id: str,
                               property_listing: PropertyListing,
                               avm_value: Optional[AVMValueResponse],
                               market_stats: Optional[MarketStatistics],
                               deal_score: DealScore):
        """Store complete analysis results in database."""
        try:
            # Store in deal_analyses table
            self.db_manager.store_deal_analysis(
                analysis_id=analysis_id,
                property_data=asdict(property_listing),
                avm_data=asdict(avm_value) if avm_value else None,
                market_data=asdict(market_stats) if market_stats else None,
                deal_score_data=asdict(deal_score),
                analysis_timestamp=datetime.now()
            )
            
            self.logger.debug(f"Stored analysis results for {analysis_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to store analysis results: {e}")
            # Don't fail the entire analysis if storage fails
    
    def _generate_recommendation(self, deal_score: DealScore) -> str:
        """Generate detailed recommendation based on deal score."""
        base_recommendations = {
            "Excellent": "🟢 STRONG BUY - Exceptional value opportunity",
            "Good": "🔵 BUY - Solid investment with good fundamentals", 
            "Fair": "🟡 CONSIDER - Average deal, evaluate personal needs",
            "Poor": "🔴 PASS - Significant concerns about value/risk",
            "Insufficient Data": "⚪ MORE DATA NEEDED - Gather additional information"
        }
        
        base_rec = base_recommendations.get(deal_score.deal_type, "❓ UNKNOWN")
        
        # Add specific insights
        insights = []
        
        if deal_score.value_discount_pct and deal_score.value_discount_pct > 10:
            insights.append(f"Great value at {deal_score.value_discount_pct:.1f}% below market")
        
        if deal_score.property_score > 80:
            insights.append("Excellent property condition/specs")
        
        if deal_score.confidence < 0.5:
            insights.append("Low confidence - verify data independently")
        
        if insights:
            return f"{base_rec}. {'. '.join(insights)}."
        
        return base_rec
