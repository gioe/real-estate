"""
Real Estate Deal Analyzer for Owner-Occupied Properties

This module provides analysis tools to determine if a property represents
a good deal for someone who will live in it (not rent it out).
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import logging

from ..schemas.rentcast_schemas import PropertyListing, AVMValueResponse, MarketStatistics


@dataclass
class DealScore:
    """Complete deal analysis results"""
    overall_score: float  # 0-100 scale
    price_score: float    # How good is the price vs market value
    market_score: float   # How well positioned in the local market
    property_score: float # Quality/condition indicators
    location_score: float # Market trends and desirability
    
    deal_type: str        # "Excellent", "Good", "Fair", "Poor"
    confidence: float     # How confident we are (0-1)
    
    # Key insights
    estimated_value: Optional[float]
    asking_price: Optional[float]
    value_difference: Optional[float]  # Estimated value - asking price
    value_discount_pct: Optional[float]  # Percentage below market value


class BasicDealAnalyzer:
    """
    Analyzes properties for owner-occupants to determine deal quality.
    
    Focuses on:
    - Purchase price vs market value
    - Property condition and specs
    - Market position and trends
    - Long-term appreciation potential
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Scoring weights for different factors
        self.weights = {
            'price_vs_value': 0.4,      # Most important: getting good price
            'market_position': 0.25,    # Market conditions and positioning
            'property_quality': 0.20,   # Property specs and condition
            'location_trends': 0.15     # Area growth and desirability
        }
    
    def analyze_deal(self, 
                    listing: PropertyListing,
                    avm_value: Optional[AVMValueResponse] = None,
                    market_stats: Optional[MarketStatistics] = None) -> DealScore:
        """
        Calculate comprehensive deal score for an owner-occupied purchase.
        
        Args:
            listing: The property listing to analyze
            avm_value: Automated valuation model data (optional)
            market_stats: Local market statistics (optional)
            
        Returns:
            DealScore with detailed analysis
        """
        try:
            # Calculate component scores (0-100 scale)
            price_score = self._calculate_price_score(listing, avm_value)
            market_score = self._calculate_market_score(listing, market_stats)
            property_score = self._calculate_property_score(listing)
            location_score = self._calculate_location_score(market_stats)
            
            # Calculate weighted overall score
            overall_score = (
                price_score * self.weights['price_vs_value'] +
                market_score * self.weights['market_position'] +
                property_score * self.weights['property_quality'] +
                location_score * self.weights['location_trends']
            )
            
            # Determine confidence based on data availability
            confidence = self._calculate_confidence(avm_value, market_stats)
            
            # Classify deal quality
            deal_type = self._classify_deal(overall_score, confidence)
            
            # Calculate key financial metrics
            value_difference = None
            value_discount_pct = None
            if avm_value and avm_value.price and listing.price:
                value_difference = avm_value.price - listing.price
                value_discount_pct = (value_difference / avm_value.price) * 100
            
            return DealScore(
                overall_score=round(overall_score, 1),
                price_score=round(price_score, 1),
                market_score=round(market_score, 1),
                property_score=round(property_score, 1),
                location_score=round(location_score, 1),
                deal_type=deal_type,
                confidence=round(confidence, 2),
                estimated_value=avm_value.price if avm_value else None,
                asking_price=listing.price,
                value_difference=round(value_difference, 0) if value_difference else None,
                value_discount_pct=round(value_discount_pct, 1) if value_discount_pct else None
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing deal: {e}")
            return self._create_error_score()
    
    def _calculate_price_score(self, 
                              listing: PropertyListing, 
                              avm_value: Optional[AVMValueResponse]) -> float:
        """
        Score based on asking price vs estimated market value.
        Higher score = better deal (lower price relative to value).
        """
        if not listing.price:
            return 50.0  # Neutral score if no price
        
        if not avm_value or not avm_value.price:
            return 50.0  # Can't evaluate without market value estimate
        
        # Calculate discount percentage
        discount_pct = ((avm_value.price - listing.price) / avm_value.price) * 100
        
        # Score based on how much below market value
        if discount_pct >= 15:      # 15%+ below market = excellent deal
            return 95.0
        elif discount_pct >= 10:    # 10-15% below = very good
            return 85.0
        elif discount_pct >= 5:     # 5-10% below = good
            return 75.0
        elif discount_pct >= 0:     # At market value = fair
            return 60.0
        elif discount_pct >= -5:    # Up to 5% above = below average
            return 45.0
        elif discount_pct >= -10:   # 5-10% above = poor
            return 30.0
        else:                       # 10%+ above market = very poor
            return 15.0
    
    def _calculate_market_score(self, 
                               listing: PropertyListing,
                               market_stats: Optional[MarketStatistics]) -> float:
        """
        Score based on market conditions and property's position within market.
        """
        if not market_stats or not listing.price:
            return 50.0  # Neutral if no market data
        
        score = 50.0  # Base score
        
        # Get relevant market data based on property type
        market_data = None
        if listing.property_type == "Single Family" and market_stats.sale_data:
            # For our simplified mock data, just use the market stats directly
            market_data = market_stats.sale_data
        elif listing.property_type in ["Condo", "Townhome"] and market_stats.sale_data:
            # For our simplified mock data, just use the market stats directly  
            market_data = market_stats.sale_data
        
        if not market_data:
            return score
        
        # Compare to market median price
        if market_data.medianSalePrice:
            price_ratio = listing.price / market_data.medianSalePrice
            
            # Score based on position in market price distribution
            if price_ratio <= 0.8:     # Bottom 20% of market = opportunity
                score += 15
            elif price_ratio <= 1.0:   # Below median = good positioning
                score += 8
            elif price_ratio <= 1.2:   # Slightly above median = neutral
                score += 0
            elif price_ratio <= 1.5:   # Above median = higher end
                score -= 8
            else:                      # Top tier = luxury market
                score -= 15
        
        # Market velocity indicator
        if market_data.medianDaysOnMarket:
            if listing.daysOnMarket:
                if listing.daysOnMarket <= market_data.medianDaysOnMarket * 0.5:
                    score += 10  # Moving fast = hot property/good price
                elif listing.daysOnMarket >= market_data.medianDaysOnMarket * 2:
                    score -= 10  # Sitting long = potential issues
        
        return max(0, min(100, score))
    
    def _calculate_property_score(self, listing: PropertyListing) -> float:
        """
        Score based on property specifications, age, and features.
        Higher score = better property for living in.
        """
        score = 50.0  # Base score
        
        # Age factor (important for maintenance and modern features)
        if listing.yearBuilt:
            current_year = datetime.now().year
            property_age = current_year - listing.yearBuilt
            
            if property_age <= 5:       # New construction
                score += 20
            elif property_age <= 15:    # Modern home
                score += 15
            elif property_age <= 25:    # Mature but not old
                score += 5
            elif property_age <= 40:    # Getting older
                score -= 5
            elif property_age <= 60:    # Old home
                score -= 15
            else:                       # Very old (potential major maintenance)
                score -= 25
        
        # Size considerations
        if listing.squareFootage:
            if listing.squareFootage >= 2000:     # Large home
                score += 10
            elif listing.squareFootage >= 1200:   # Medium home
                score += 5
            elif listing.squareFootage >= 800:    # Small but livable
                score += 0
            else:                                 # Very small
                score -= 10
        
        # Bedroom/bathroom adequacy
        if listing.bedrooms and listing.bathrooms:
            # Good ratios for livability
            if listing.bedrooms >= 3 and listing.bathrooms >= 2:
                score += 10  # Family-friendly
            elif listing.bedrooms >= 2 and listing.bathrooms >= 1.5:
                score += 5   # Good for couples/small families
            elif listing.bedrooms >= 1 and listing.bathrooms >= 1:
                score += 0   # Basic adequacy
            else:
                score -= 5   # Inadequate
        
        # Lot size (outdoor space)
        if listing.lotSize:
            if listing.lotSize >= 0.5:    # Half acre+
                score += 8
            elif listing.lotSize >= 0.25: # Quarter acre
                score += 5
            elif listing.lotSize >= 0.1:  # Small yard
                score += 2
        
        return max(0, min(100, score))
    
    def _calculate_location_score(self, market_stats: Optional[MarketStatistics]) -> float:
        """
        Score based on market trends and area desirability indicators.
        """
        if not market_stats:
            return 50.0  # Neutral without data
        
        score = 50.0
        
        # Market activity level (higher activity = more desirable area)
        if market_stats.saleData:
            # Check both property types for overall market health
            sf_data = market_stats.saleData.singleFamily
            condo_data = market_stats.saleData.condo
            
            # Days on market indicator (faster = more desirable)
            days_on_market_scores = []
            
            if sf_data and sf_data.medianDaysOnMarket:
                if sf_data.medianDaysOnMarket <= 30:
                    days_on_market_scores.append(15)  # Very hot market
                elif sf_data.medianDaysOnMarket <= 60:
                    days_on_market_scores.append(8)   # Active market
                elif sf_data.medianDaysOnMarket <= 90:
                    days_on_market_scores.append(0)   # Normal market
                else:
                    days_on_market_scores.append(-10) # Slow market
            
            if condo_data and condo_data.medianDaysOnMarket:
                if condo_data.medianDaysOnMarket <= 45:
                    days_on_market_scores.append(10)
                elif condo_data.medianDaysOnMarket <= 75:
                    days_on_market_scores.append(5)
                elif condo_data.medianDaysOnMarket <= 120:
                    days_on_market_scores.append(0)
                else:
                    days_on_market_scores.append(-8)
            
            if days_on_market_scores:
                score += sum(days_on_market_scores) / len(days_on_market_scores)
        
        return max(0, min(100, score))
    
    def _calculate_confidence(self, 
                            avm_value: Optional[AVMValueResponse],
                            market_stats: Optional[MarketStatistics]) -> float:
        """Calculate confidence level based on available data quality."""
        confidence = 0.0
        
        # AVM data availability and quality
        if avm_value:
            confidence += 0.5
            if avm_value.confidence and avm_value.confidence > 0.7:
                confidence += 0.2
        
        # Market statistics availability
        if market_stats:
            confidence += 0.3
        
        return min(1.0, confidence)
    
    def _classify_deal(self, score: float, confidence: float) -> str:
        """Classify deal quality based on score and confidence."""
        if confidence < 0.4:
            return "Insufficient Data"
        
        # Adjust thresholds based on confidence
        if confidence >= 0.8:
            if score >= 80:
                return "Excellent"
            elif score >= 65:
                return "Good"
            elif score >= 45:
                return "Fair"
            else:
                return "Poor"
        else:
            # More conservative thresholds for lower confidence
            if score >= 85:
                return "Excellent"
            elif score >= 70:
                return "Good"
            elif score >= 50:
                return "Fair"
            else:
                return "Poor"
    
    def _create_error_score(self) -> DealScore:
        """Create a default error score."""
        return DealScore(
            overall_score=0.0,
            price_score=0.0,
            market_score=0.0,
            property_score=0.0,
            location_score=0.0,
            deal_type="Error",
            confidence=0.0,
            estimated_value=None,
            asking_price=None,
            value_difference=None,
            value_discount_pct=None
        )
