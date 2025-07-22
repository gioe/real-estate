"""
Data Analyzer Module

This module handles analysis of real estate data, including market trends,
price analysis, and property matching based on user criteria.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class RealEstateAnalyzer:
    """Main class for analyzing real estate data."""
    
    def __init__(self, database_manager):
        """
        Initialize the analyzer with database connection.
        
        Args:
            database_manager: DatabaseManager instance
        """
        self.db = database_manager
        self.analysis_cache = {}
        
    def run_analysis(self) -> Dict[str, Any]:
        """
        Run comprehensive analysis on all available data.
        
        Returns:
            Dictionary containing analysis results
        """
        logger.info("Starting comprehensive real estate analysis")
        
        try:
            # Get all properties from database
            properties = self.db.get_all_properties()
            
            if not properties:
                logger.warning("No properties found in database")
                return {}
            
            df = pd.DataFrame(properties)
            
            # Run various analyses
            analysis_results = {
                'market_trends': self.analyze_market_trends(df),
                'price_analysis': self.analyze_prices(df),
                'location_analysis': self.analyze_locations(df),
                'property_type_analysis': self.analyze_property_types(df),
                'time_on_market': self.analyze_time_on_market(df),
                'investment_opportunities': self.find_investment_opportunities(df),
                'market_summary': self.generate_market_summary(df),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            logger.info("Analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            return {}
    
    def analyze_market_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze market trends over time.
        
        Args:
            df: DataFrame containing property data
            
        Returns:
            Dictionary with trend analysis
        """
        logger.info("Analyzing market trends")
        
        try:
            # Convert listing_date to datetime
            df['listing_date'] = pd.to_datetime(df['listing_date'], errors='coerce')
            df = df.dropna(subset=['listing_date', 'price'])
            
            # Group by month
            df['year_month'] = df['listing_date'].dt.to_period('M')
            monthly_stats = df.groupby('year_month').agg({
                'price': ['mean', 'median', 'count'],
                'square_feet': 'mean',
                'days_on_market': 'mean'
            }).round(2)
            
            # Calculate trends
            price_trend = self._calculate_trend(monthly_stats[('price', 'mean')])
            volume_trend = self._calculate_trend(monthly_stats[('price', 'count')])
            
            return {
                'monthly_stats': monthly_stats.to_dict(),
                'price_trend': price_trend,
                'volume_trend': volume_trend,
                'avg_price_change': self._calculate_percentage_change(monthly_stats[('price', 'mean')]),
                'avg_volume_change': self._calculate_percentage_change(monthly_stats[('price', 'count')])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {str(e)}")
            return {}
    
    def analyze_prices(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze price distributions and statistics.
        
        Args:
            df: DataFrame containing property data
            
        Returns:
            Dictionary with price analysis
        """
        logger.info("Analyzing price distributions")
        
        try:
            df = df.dropna(subset=['price'])
            prices = df['price'].astype(float)
            
            # Basic statistics
            price_stats = {
                'mean': float(prices.mean()),
                'median': float(prices.median()),
                'std': float(prices.std()),
                'min': float(prices.min()),
                'max': float(prices.max()),
                'q25': float(prices.quantile(0.25)),
                'q75': float(prices.quantile(0.75))
            }
            
            # Price ranges
            price_ranges = self._categorize_prices(prices)
            
            # Price per square foot analysis
            df_with_sqft = df.dropna(subset=['square_feet'])
            df_with_sqft = df_with_sqft[df_with_sqft['square_feet'] > 0]
            
            if not df_with_sqft.empty:
                df_with_sqft['price_per_sqft'] = df_with_sqft['price'] / df_with_sqft['square_feet']
                price_per_sqft_stats = {
                    'mean': float(df_with_sqft['price_per_sqft'].mean()),
                    'median': float(df_with_sqft['price_per_sqft'].median()),
                    'std': float(df_with_sqft['price_per_sqft'].std())
                }
            else:
                price_per_sqft_stats = {}
            
            return {
                'price_statistics': price_stats,
                'price_ranges': price_ranges,
                'price_per_sqft': price_per_sqft_stats,
                'outliers': self._find_price_outliers(prices).tolist()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing prices: {str(e)}")
            return {}
    
    def analyze_locations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze properties by location (city, zip code, etc.).
        
        Args:
            df: DataFrame containing property data
            
        Returns:
            Dictionary with location analysis
        """
        logger.info("Analyzing locations")
        
        try:
            location_analysis = {}
            
            # City analysis
            if 'city' in df.columns:
                city_stats = df.groupby('city').agg({
                    'price': ['mean', 'median', 'count'],
                    'square_feet': 'mean',
                    'days_on_market': 'mean'
                }).round(2)
                
                location_analysis['cities'] = city_stats.to_dict()
            
            # ZIP code analysis
            if 'zip_code' in df.columns:
                zip_stats = df.groupby('zip_code').agg({
                    'price': ['mean', 'median', 'count'],
                    'square_feet': 'mean',
                    'days_on_market': 'mean'
                }).round(2)
                
                location_analysis['zip_codes'] = zip_stats.to_dict()
            
            # Find hotspots (areas with most activity)
            if 'city' in df.columns:
                hotspots = df['city'].value_counts().head(10).to_dict()
                location_analysis['hotspots'] = hotspots
            
            return location_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing locations: {str(e)}")
            return {}
    
    def analyze_property_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze properties by type (house, condo, etc.).
        
        Args:
            df: DataFrame containing property data
            
        Returns:
            Dictionary with property type analysis
        """
        logger.info("Analyzing property types")
        
        try:
            if 'property_type' not in df.columns:
                return {}
            
            type_stats = df.groupby('property_type').agg({
                'price': ['mean', 'median', 'count'],
                'square_feet': 'mean',
                'bedrooms': 'mean',
                'bathrooms': 'mean',
                'days_on_market': 'mean'
            }).round(2)
            
            return {
                'type_statistics': type_stats.to_dict(),
                'type_distribution': df['property_type'].value_counts().to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing property types: {str(e)}")
            return {}
    
    def analyze_time_on_market(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze time properties spend on the market.
        
        Args:
            df: DataFrame containing property data
            
        Returns:
            Dictionary with time on market analysis
        """
        logger.info("Analyzing time on market")
        
        try:
            if 'days_on_market' not in df.columns:
                return {}
            
            dom_data = df.dropna(subset=['days_on_market'])
            dom_data = dom_data[dom_data['days_on_market'] >= 0]  # Remove negative values
            
            if dom_data.empty:
                return {}
            
            dom_stats = {
                'mean': float(dom_data['days_on_market'].mean()),
                'median': float(dom_data['days_on_market'].median()),
                'std': float(dom_data['days_on_market'].std()),
                'min': int(dom_data['days_on_market'].min()),
                'max': int(dom_data['days_on_market'].max())
            }
            
            # Categorize by time ranges
            dom_categories = {
                'quick_sale_0_30_days': len(dom_data[dom_data['days_on_market'] <= 30]),
                'normal_31_90_days': len(dom_data[(dom_data['days_on_market'] > 30) & 
                                                 (dom_data['days_on_market'] <= 90)]),
                'slow_91_180_days': len(dom_data[(dom_data['days_on_market'] > 90) & 
                                                (dom_data['days_on_market'] <= 180)]),
                'stale_over_180_days': len(dom_data[dom_data['days_on_market'] > 180])
            }
            
            return {
                'statistics': dom_stats,
                'categories': dom_categories
            }
            
        except Exception as e:
            logger.error(f"Error analyzing time on market: {str(e)}")
            return {}
    
    def find_investment_opportunities(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Identify potential investment opportunities.
        
        Args:
            df: DataFrame containing property data
            
        Returns:
            Dictionary with investment opportunities
        """
        logger.info("Finding investment opportunities")
        
        try:
            opportunities = {}
            
            # Find underpriced properties (below median price per sqft)
            if 'square_feet' in df.columns:
                df_with_sqft = df.dropna(subset=['price', 'square_feet'])
                df_with_sqft = df_with_sqft[df_with_sqft['square_feet'] > 0]
                
                if not df_with_sqft.empty:
                    df_with_sqft['price_per_sqft'] = df_with_sqft['price'] / df_with_sqft['square_feet']
                    median_price_per_sqft = df_with_sqft['price_per_sqft'].median()
                    
                    underpriced = df_with_sqft[
                        df_with_sqft['price_per_sqft'] < median_price_per_sqft * 0.8
                    ].sort_values('price_per_sqft')
                    
                    opportunities['underpriced_properties'] = underpriced.head(10).to_dict('records')
            
            # Find properties with long days on market (potential for negotiation)
            if 'days_on_market' in df.columns:
                long_dom = df[df['days_on_market'] > 90].sort_values('days_on_market', ascending=False)
                opportunities['long_on_market'] = long_dom.head(10).to_dict('records')
            
            # Find properties in hot markets with good value
            if 'city' in df.columns:
                city_activity = df['city'].value_counts()
                hot_cities = city_activity.head(5).index.tolist()
                
                hot_market_deals = df[
                    df['city'].isin(hot_cities)
                ].sort_values('price')
                
                opportunities['hot_market_deals'] = hot_market_deals.head(10).to_dict('records')
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error finding investment opportunities: {str(e)}")
            return {}
    
    def generate_market_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a high-level market summary.
        
        Args:
            df: DataFrame containing property data
            
        Returns:
            Dictionary with market summary
        """
        logger.info("Generating market summary")
        
        try:
            summary = {
                'total_properties': len(df),
                'date_range': {
                    'start': df['listing_date'].min() if 'listing_date' in df.columns else None,
                    'end': df['listing_date'].max() if 'listing_date' in df.columns else None
                },
                'price_summary': {
                    'median_price': float(df['price'].median()) if 'price' in df.columns else None,
                    'average_price': float(df['price'].mean()) if 'price' in df.columns else None
                }
            }
            
            if 'city' in df.columns:
                summary['geographic_coverage'] = {
                    'cities_covered': df['city'].nunique(),
                    'top_cities': df['city'].value_counts().head(5).to_dict()
                }
            
            if 'property_type' in df.columns:
                summary['property_types'] = df['property_type'].value_counts().to_dict()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating market summary: {str(e)}")
            return {}
    
    def find_matching_properties(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find properties matching specific criteria for notifications.
        
        Args:
            criteria: Dictionary with search criteria
            
        Returns:
            List of matching properties
        """
        logger.info("Finding properties matching notification criteria")
        
        try:
            properties = self.db.get_recent_properties(days=1)  # Only check recent properties
            
            if not properties:
                return []
            
            df = pd.DataFrame(properties)
            matching = df.copy()
            
            # Apply filters based on criteria
            for field, conditions in criteria.items():
                if field not in df.columns:
                    continue
                
                if isinstance(conditions, dict):
                    if 'min' in conditions:
                        matching = matching[matching[field] >= conditions['min']]
                    if 'max' in conditions:
                        matching = matching[matching[field] <= conditions['max']]
                    if 'equals' in conditions:
                        matching = matching[matching[field] == conditions['equals']]
                    if 'in' in conditions:
                        matching = matching[matching[field].isin(conditions['in'])]
                else:
                    # Simple equality check
                    matching = matching[matching[field] == conditions]
            
            return matching.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error finding matching properties: {str(e)}")
            return []
    
    def _calculate_trend(self, series: pd.Series) -> str:
        """Calculate trend direction from a time series."""
        if len(series) < 2:
            return "insufficient_data"
        
        # Simple linear trend
        x = np.arange(len(series))
        y = series.values
        
        # Remove NaN values
        mask = ~np.isnan(y)
        if np.sum(mask) < 2:
            return "insufficient_data"
        
        x = x[mask]
        y = y[mask]
        
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0:
            return "increasing"
        elif slope < 0:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_percentage_change(self, series: pd.Series) -> float:
        """Calculate percentage change from first to last value."""
        if len(series) < 2:
            return 0.0
        
        first_val = series.iloc[0]
        last_val = series.iloc[-1]
        
        if first_val == 0:
            return 0.0
        
        return ((last_val - first_val) / first_val) * 100
    
    def _categorize_prices(self, prices: pd.Series) -> Dict[str, int]:
        """Categorize prices into ranges."""
        return {
            'under_200k': len(prices[prices < 200000]),
            '200k_400k': len(prices[(prices >= 200000) & (prices < 400000)]),
            '400k_600k': len(prices[(prices >= 400000) & (prices < 600000)]),
            '600k_800k': len(prices[(prices >= 600000) & (prices < 800000)]),
            '800k_1m': len(prices[(prices >= 800000) & (prices < 1000000)]),
            'over_1m': len(prices[prices >= 1000000])
        }
    
    def _find_price_outliers(self, prices: pd.Series) -> pd.Series:
        """Find price outliers using IQR method."""
        Q1 = prices.quantile(0.25)
        Q3 = prices.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return prices[(prices < lower_bound) | (prices > upper_bound)]
