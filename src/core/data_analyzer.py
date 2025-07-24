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
            # Get all listings from database
            listings = self.db.get_all_listings()
            
            if not listings:
                logger.warning("No listings found in database")
                return {}
            
            df = pd.DataFrame(listings)
            
            # Run various analyses
            analysis_results = {
                'market_trends': self.analyze_market_trends(df),
                'price_analysis': self.analyze_prices(df),
                'location_analysis': self.analyze_locations(df),
                'property_type_analysis': self.analyze_property_types(df),
                'time_on_market': self.analyze_time_on_market(df),
                'listing_analysis': self.analyze_listings(df),  # New listing-specific analysis
                'source_analysis': self.analyze_sources(df),   # New source comparison
                'market_velocity': self.analyze_market_velocity(df),  # New velocity analysis
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
    
    def analyze_listings(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze listing-specific data (status, type, etc.).
        
        Args:
            df: DataFrame containing listings data
            
        Returns:
            Dictionary with listing analysis
        """
        logger.info("Analyzing listings data")
        
        try:
            listing_analysis = {}
            
            # Listing type distribution
            if 'listing_type' in df.columns:
                listing_analysis['type_distribution'] = df['listing_type'].value_counts().to_dict()
            
            # Listing status analysis
            if 'status' in df.columns:
                listing_analysis['status_distribution'] = df['status'].value_counts().to_dict()
            
            # Active vs inactive listings
            if 'status' in df.columns:
                active_count = len(df[df['status'] == 'active'])
                total_count = len(df)
                listing_analysis['active_ratio'] = active_count / total_count if total_count > 0 else 0
            
            # Sale vs rental analysis
            if 'listing_type' in df.columns:
                sale_listings = df[df['listing_type'] == 'sale']
                rental_listings = df[df['listing_type'] == 'rental']
                
                if not sale_listings.empty and not rental_listings.empty:
                    listing_analysis['sale_vs_rental'] = {
                        'sale_count': len(sale_listings),
                        'rental_count': len(rental_listings),
                        'avg_sale_price': float(sale_listings['price'].mean()) if 'price' in sale_listings.columns else None,
                        'avg_rental_price': float(rental_listings['price'].mean()) if 'price' in rental_listings.columns else None
                    }
            
            return listing_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing listings: {str(e)}")
            return {}
    
    def analyze_sources(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze data sources and their quality.
        
        Args:
            df: DataFrame containing listings data
            
        Returns:
            Dictionary with source analysis
        """
        logger.info("Analyzing data sources")
        
        try:
            source_analysis = {}
            
            if 'source' not in df.columns:
                return source_analysis
            
            # Source distribution
            source_analysis['distribution'] = df['source'].value_counts().to_dict()
            
            # Source quality metrics
            source_counts = df.groupby('source').size()
            source_analysis['source_counts'] = source_counts.to_dict()
            
            # Basic completeness check
            completeness_by_source = {}
            for source in df['source'].unique():
                source_data = df[df['source'] == source]
                total = len(source_data)
                complete_price = len(source_data.dropna(subset=['price']))
                complete_beds = len(source_data.dropna(subset=['bedrooms']))
                complete_sqft = len(source_data.dropna(subset=['square_feet']))
                
                completeness_by_source[source] = {
                    'total_listings': total,
                    'price_completeness': (complete_price / total) * 100 if total > 0 else 0,
                    'bedrooms_completeness': (complete_beds / total) * 100 if total > 0 else 0,
                    'sqft_completeness': (complete_sqft / total) * 100 if total > 0 else 0
                }
            
            source_analysis['completeness_by_source'] = completeness_by_source
            
            return source_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sources: {str(e)}")
            return {}
    
    def analyze_market_velocity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze market velocity and listing turnover.
        
        Args:
            df: DataFrame containing listings data
            
        Returns:
            Dictionary with market velocity analysis
        """
        logger.info("Analyzing market velocity")
        
        try:
            velocity_analysis = {}
            
            # Convert dates for time-based analysis
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
                df = df.dropna(subset=['created_at'])
                
                # Daily listing volume
                daily_volume = df.groupby(df['created_at'].dt.date).size()
                velocity_analysis['daily_volume'] = {
                    'mean': float(daily_volume.mean()),
                    'std': float(daily_volume.std()),
                    'trend': self._calculate_trend(daily_volume)
                }
                
                # Weekly patterns
                df['day_of_week'] = df['created_at'].dt.day_name()
                velocity_analysis['weekly_pattern'] = df['day_of_week'].value_counts().to_dict()
            
            # Listing freshness
            if 'fetched_at' in df.columns:
                df['fetched_at'] = pd.to_datetime(df['fetched_at'], errors='coerce')
                df = df.dropna(subset=['fetched_at'])
                now = pd.Timestamp.now()
                
                # Calculate age in hours for each listing
                listing_ages = []
                for fetch_time in df['fetched_at']:
                    age_hours = (now - fetch_time).total_seconds() / 3600
                    listing_ages.append(age_hours)
                
                df['listing_age_hours'] = listing_ages
                
                velocity_analysis['listing_freshness'] = {
                    'avg_age_hours': float(df['listing_age_hours'].mean()),
                    'fresh_listings_24h': len(df[df['listing_age_hours'] <= 24]),
                    'stale_listings_7d': len(df[df['listing_age_hours'] >= 168])  # 7 days
                }
            
            # Price change velocity (if multiple listings for same property)
            if 'property_id' in df.columns:
                property_counts = df['property_id'].value_counts()
                repeat_properties = property_counts[property_counts > 1]
                velocity_analysis['repeat_listings'] = {
                    'properties_with_multiple_listings': len(repeat_properties),
                    'avg_listings_per_property': float(property_counts.mean())
                }
            
            return velocity_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing market velocity: {str(e)}")
            return {}
    
    def generate_market_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a high-level market summary from listings data.
        
        Args:
            df: DataFrame containing listings data
            
        Returns:
            Dictionary with market summary
        """
        logger.info("Generating market summary")
        
        try:
            summary = {
                'total_listings': len(df),
                'date_range': {
                    'start': df['listing_date'].min() if 'listing_date' in df.columns else None,
                    'end': df['listing_date'].max() if 'listing_date' in df.columns else None
                },
                'price_summary': {
                    'median_price': float(df['price'].median()) if 'price' in df.columns else None,
                    'average_price': float(df['price'].mean()) if 'price' in df.columns else None
                }
            }
            
            # Listing type breakdown
            if 'listing_type' in df.columns:
                summary['listing_types'] = df['listing_type'].value_counts().to_dict()
            
            if 'city' in df.columns:
                summary['geographic_coverage'] = {
                    'cities_covered': df['city'].nunique(),
                    'top_cities': df['city'].value_counts().head(5).to_dict()
                }
            
            if 'property_type' in df.columns:
                summary['property_types'] = df['property_type'].value_counts().to_dict()
            
            # Source breakdown
            if 'source' in df.columns:
                summary['data_sources'] = df['source'].value_counts().to_dict()
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating market summary: {str(e)}")
            return {}
    
    def find_matching_properties(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find listings matching specific criteria for notifications.
        
        Args:
            criteria: Dictionary with search criteria
            
        Returns:
            List of matching listings
        """
        logger.info("Finding listings matching notification criteria")
        
        try:
            # Get recent listings instead of properties
            recent_listings = self.db.get_all_listings(limit=1000)  # Limit for performance
            
            if not recent_listings:
                return []
            
            df = pd.DataFrame(recent_listings)
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
            
            # Convert to list of dictionaries
            result = []
            for _, row in matching.iterrows():
                result.append(dict(row))
            return result
            
        except Exception as e:
            logger.error(f"Error finding matching listings: {str(e)}")
            return []
    
    def _calculate_trend(self, series: pd.Series) -> str:
        """Calculate trend direction from a time series."""
        if len(series) < 2:
            return "insufficient_data"
        
        # Simple linear trend
        x = np.arange(len(series))
        y = series.values
        
        # Remove NaN values
        try:
            y_array = np.array(y, dtype=float)
            mask = ~np.isnan(y_array)
        except (ValueError, TypeError):
            return "insufficient_data"
            
        if np.sum(mask) < 2:
            return "insufficient_data"
        
        x = x[mask]
        y_array = y_array[mask]
        
        slope = np.polyfit(x, y_array, 1)[0]
        
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
