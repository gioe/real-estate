"""
Database Manager Module

This module handles database operations for storing and retrieving real estate data.
Supports SQLite by default with options for PostgreSQL integration.
Includes comprehensive pagination support for handling large datasets.
"""

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class PaginationParams:
    """Parameters for database pagination."""
    limit: int = 50
    offset: int = 0
    
    def __post_init__(self):
        """Validate pagination parameters."""
        if self.limit < 1 or self.limit > 500:
            raise ValueError("Limit must be between 1 and 500")
        if self.offset < 0:
            raise ValueError("Offset must be non-negative")


@dataclass
class PaginatedResult:
    """Result container for paginated database queries."""
    data: List[Dict[str, Any]]
    total_count: int
    limit: int
    offset: int
    has_more: bool
    next_offset: Optional[int] = None
    
    def __post_init__(self):
        """Calculate pagination metadata."""
        self.has_more = (self.offset + len(self.data)) < self.total_count
        if self.has_more:
            self.next_offset = self.offset + self.limit
        else:
            self.next_offset = None


class DatabaseManager:
    """Main class for managing database operations."""
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        Initialize the database manager with configuration.
        
        Args:
            db_config: Dictionary containing database configuration
        """
        self.config = db_config
        self.db_type = db_config.get('type', 'sqlite')
        
        if self.db_type == 'sqlite':
            self.db_path = Path(db_config.get('sqlite_path', 'data/real_estate.db'))
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_sqlite_database()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _init_sqlite_database(self) -> None:
        """Initialize SQLite database and create tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create properties table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS properties (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        property_id TEXT UNIQUE,
                        source TEXT NOT NULL,
                        address TEXT,
                        city TEXT,
                        state TEXT,
                        zip_code TEXT,
                        price REAL,
                        bedrooms INTEGER,
                        bathrooms REAL,
                        square_feet INTEGER,
                        lot_size REAL,
                        year_built INTEGER,
                        property_type TEXT,
                        listing_date TEXT,
                        days_on_market INTEGER,
                        url TEXT,
                        latitude REAL,
                        longitude REAL,
                        description TEXT,
                        raw_data TEXT,
                        fetched_at TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create listings table (new approach for storing market listings)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS listings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        listing_id TEXT UNIQUE,
                        property_id TEXT,
                        source TEXT NOT NULL,
                        listing_type TEXT NOT NULL, -- 'sale' or 'rental'
                        address TEXT,
                        city TEXT,
                        state TEXT,
                        zip_code TEXT,
                        price REAL,
                        bedrooms INTEGER,
                        bathrooms REAL,
                        square_feet INTEGER,
                        lot_size REAL,
                        year_built INTEGER,
                        property_type TEXT,
                        listing_date TEXT,
                        days_on_market INTEGER,
                        status TEXT, -- 'active', 'pending', 'sold', etc.
                        url TEXT,
                        latitude REAL,
                        longitude REAL,
                        description TEXT,
                        raw_data TEXT,
                        fetched_at TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create analysis_results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        analysis_type TEXT NOT NULL,
                        results TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create AVM (Automated Valuation Model) data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS avm_valuations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        property_id TEXT NOT NULL,
                        address TEXT NOT NULL,
                        estimated_value REAL,
                        estimated_rent REAL,
                        confidence_score REAL,
                        value_range_low REAL,
                        value_range_high REAL,
                        rent_range_low REAL,
                        rent_range_high REAL,
                        comparables_count INTEGER,
                        cap_rate REAL,
                        cash_flow REAL,
                        roi_percentage REAL,
                        raw_avm_data TEXT,
                        fetched_at DATETIME NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (property_id) REFERENCES properties(property_id)
                    )
                ''')
                
                # Create market statistics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS market_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        zip_code TEXT NOT NULL,
                        city TEXT,
                        state TEXT,
                        property_type TEXT,
                        bedrooms INTEGER,
                        avg_sale_price REAL,
                        median_sale_price REAL,
                        avg_rent_price REAL,
                        median_rent_price REAL,
                        avg_price_per_sqft REAL,
                        avg_rent_per_sqft REAL,
                        inventory_count INTEGER,
                        avg_days_on_market INTEGER,
                        rent_yield_percentage REAL,
                        price_trend_3m TEXT,
                        price_trend_6m TEXT,
                        price_trend_12m TEXT,
                        raw_market_data TEXT,
                        analysis_month TEXT NOT NULL,
                        fetched_at DATETIME NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(zip_code, property_type, bedrooms, analysis_month)
                    )
                ''')
                
                # Create property comparables table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS property_comparables (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_property_id TEXT NOT NULL,
                        comparable_property_id TEXT,
                        comparable_address TEXT,
                        sale_price REAL,
                        sale_date TEXT,
                        distance_miles REAL,
                        bedrooms INTEGER,
                        bathrooms REAL,
                        square_feet INTEGER,
                        price_per_sqft REAL,
                        days_on_market INTEGER,
                        similarity_score REAL,
                        raw_comparable_data TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (source_property_id) REFERENCES properties(property_id)
                    )
                ''')
                
                # Create investment analysis table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS investment_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        property_id TEXT NOT NULL,
                        purchase_price REAL NOT NULL,
                        estimated_rent REAL,
                        estimated_expenses REAL,
                        cap_rate REAL,
                        cash_on_cash_return REAL,
                        gross_yield REAL,
                        net_yield REAL,
                        monthly_cash_flow REAL,
                        annual_cash_flow REAL,
                        break_even_ratio REAL,
                        investment_score REAL,
                        risk_level TEXT,
                        analysis_notes TEXT,
                        analysis_date DATE NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (property_id) REFERENCES properties(property_id)
                    )
                ''')
                
                # Create price history tracking table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS price_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        property_id TEXT NOT NULL,
                        price REAL NOT NULL,
                        price_type TEXT NOT NULL, -- 'list', 'sale', 'estimated'
                        date_recorded DATE NOT NULL,
                        source TEXT NOT NULL,
                        notes TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (property_id) REFERENCES properties(property_id)
                    )
                ''')
                
                # Create notifications_log table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notifications_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        notification_type TEXT NOT NULL,
                        recipient TEXT NOT NULL,
                        subject TEXT,
                        status TEXT NOT NULL,
                        property_count INTEGER,
                        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_properties_city 
                    ON properties(city)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_properties_price 
                    ON properties(price)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_listings_city 
                    ON listings(city)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_listings_price 
                    ON listings(price)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_listings_type 
                    ON listings(listing_type)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_listings_status 
                    ON listings(status)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_properties_listing_date 
                    ON properties(listing_date)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_properties_fetched_at 
                    ON properties(fetched_at)
                ''')
                
                # AVM valuations indexes
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_avm_property_id 
                    ON avm_valuations(property_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_avm_estimated_value 
                    ON avm_valuations(estimated_value)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_avm_fetched_at 
                    ON avm_valuations(fetched_at)
                ''')
                
                # Market statistics indexes
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_market_zip_code 
                    ON market_statistics(zip_code)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_market_analysis_month 
                    ON market_statistics(analysis_month)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_market_property_type 
                    ON market_statistics(property_type)
                ''')
                
                # Comparables indexes
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_comparables_source_property 
                    ON property_comparables(source_property_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_comparables_similarity 
                    ON property_comparables(similarity_score)
                ''')
                
                # Investment analysis indexes
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_investment_property_id 
                    ON investment_analysis(property_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_investment_score 
                    ON investment_analysis(investment_score)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_investment_cap_rate 
                    ON investment_analysis(cap_rate)
                ''')
                
                # Price history indexes
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_price_history_property_id 
                    ON price_history(property_id)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_price_history_date 
                    ON price_history(date_recorded)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_price_history_type 
                    ON price_history(price_type)
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def save_properties(self, properties: List[Dict[str, Any]]) -> int:
        """
        Save properties to the database.
        
        Args:
            properties: List of property dictionaries
            
        Returns:
            Number of properties saved
        """
        if not properties:
            return 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                saved_count = 0
                
                for prop in properties:
                    # Prepare property data
                    property_data = self._prepare_property_data(prop)
                    
                    # Try to insert or update
                    cursor.execute('''
                        INSERT OR REPLACE INTO properties 
                        (property_id, source, address, city, state, zip_code, price, 
                         bedrooms, bathrooms, square_feet, lot_size, year_built, 
                         property_type, listing_date, days_on_market, url, 
                         latitude, longitude, description, raw_data, fetched_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', property_data)
                    
                    saved_count += 1
                
                conn.commit()
                logger.info(f"Saved {saved_count} properties to database")
                return saved_count
                
        except Exception as e:
            logger.error(f"Error saving properties: {str(e)}")
            return 0
    
    def save_listings(self, listings: List[Dict[str, Any]]) -> int:
        """
        Save listings to the database.
        
        Args:
            listings: List of listing dictionaries from APIs
            
        Returns:
            Number of listings saved
        """
        if not listings:
            return 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                saved_count = 0
                
                for listing in listings:
                    # Prepare listing data
                    listing_data = self._prepare_listing_data(listing)
                    
                    # Try to insert or update
                    cursor.execute('''
                        INSERT OR REPLACE INTO listings 
                        (listing_id, property_id, source, listing_type, address, city, state, zip_code, price, 
                         bedrooms, bathrooms, square_feet, lot_size, year_built, 
                         property_type, listing_date, days_on_market, status, url, 
                         latitude, longitude, description, raw_data, fetched_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', listing_data)
                    
                    saved_count += 1
                
                conn.commit()
                logger.info(f"Saved {saved_count} listings to database")
                return saved_count
                
        except Exception as e:
            logger.error(f"Error saving listings: {str(e)}")
            return 0
    
    def get_all_properties(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all properties from the database.
        
        Args:
            limit: Optional limit on number of properties to return
            
        Returns:
            List of property dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM properties ORDER BY created_at DESC"
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                properties = []
                for row in rows:
                    prop = dict(row)
                    # Parse raw_data if it exists
                    if prop.get('raw_data'):
                        try:
                            prop['raw_data'] = json.loads(prop['raw_data'])
                        except json.JSONDecodeError:
                            pass
                    properties.append(prop)
                
                return properties
                
        except Exception as e:
            logger.error(f"Error getting properties: {str(e)}")
            return []
    
    def get_all_listings(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all listings from the database.
        
        Args:
            limit: Optional limit on number of listings to return
            
        Returns:
            List of listing dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM listings ORDER BY created_at DESC"
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query)
                rows = cursor.fetchall()
                
                listings = []
                for row in rows:
                    listing = dict(row)
                    # Parse raw_data if it exists
                    if listing.get('raw_data'):
                        try:
                            listing['raw_data'] = json.loads(listing['raw_data'])
                        except json.JSONDecodeError:
                            pass
                    listings.append(listing)
                
                return listings
                
        except Exception as e:
            logger.error(f"Error getting listings: {str(e)}")
            return []
    
    def get_recent_properties(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get properties fetched in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recent property dictionaries
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM properties 
                    WHERE fetched_at > ? 
                    ORDER BY fetched_at DESC
                ''', (cutoff_date,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting recent properties: {str(e)}")
            return []
    
    def get_properties_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get properties matching specific criteria.
        
        Args:
            criteria: Dictionary with search criteria
            
        Returns:
            List of matching property dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Build query based on criteria
                query = "SELECT * FROM properties WHERE 1=1"
                params = []
                
                # Price range
                if 'price' in criteria:
                    price_criteria = criteria['price']
                    if 'min' in price_criteria:
                        query += " AND price >= ?"
                        params.append(price_criteria['min'])
                    if 'max' in price_criteria:
                        query += " AND price <= ?"
                        params.append(price_criteria['max'])
                
                # Bedrooms
                if 'bedrooms' in criteria:
                    bed_criteria = criteria['bedrooms']
                    if 'min' in bed_criteria:
                        query += " AND bedrooms >= ?"
                        params.append(bed_criteria['min'])
                
                # Bathrooms
                if 'bathrooms' in criteria:
                    bath_criteria = criteria['bathrooms']
                    if 'min' in bath_criteria:
                        query += " AND bathrooms >= ?"
                        params.append(bath_criteria['min'])
                
                # Square feet
                if 'square_feet' in criteria:
                    sqft_criteria = criteria['square_feet']
                    if 'min' in sqft_criteria:
                        query += " AND square_feet >= ?"
                        params.append(sqft_criteria['min'])
                    if 'max' in sqft_criteria:
                        query += " AND square_feet <= ?"
                        params.append(sqft_criteria['max'])
                
                # Cities
                if 'cities' in criteria and 'in' in criteria['cities']:
                    cities = criteria['cities']['in']
                    placeholders = ','.join(['?' for _ in cities])
                    query += f" AND city IN ({placeholders})"
                    params.extend(cities)
                
                # Property type
                if 'property_type' in criteria and 'in' in criteria['property_type']:
                    types = criteria['property_type']['in']
                    placeholders = ','.join(['?' for _ in types])
                    query += f" AND property_type IN ({placeholders})"
                    params.extend(types)
                
                # Days on market
                if 'days_on_market' in criteria:
                    dom_criteria = criteria['days_on_market']
                    if 'max' in dom_criteria:
                        query += " AND days_on_market <= ?"
                        params.append(dom_criteria['max'])
                
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting properties by criteria: {str(e)}")
            return []
    
    # Paginated query methods
    
    def get_properties_paginated(self, pagination: PaginationParams, 
                                criteria: Optional[Dict[str, Any]] = None) -> PaginatedResult:
        """
        Get properties with pagination support.
        
        Args:
            pagination: Pagination parameters (limit, offset)
            criteria: Optional search criteria
            
        Returns:
            PaginatedResult containing properties and pagination metadata
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Build base query
                base_query = "FROM properties WHERE 1=1"
                params = []
                
                # Add criteria filters if provided
                if criteria:
                    query_parts, filter_params = self._build_criteria_query(criteria)
                    base_query += query_parts
                    params.extend(filter_params)
                
                # Get total count
                count_query = f"SELECT COUNT(*) {base_query}"
                cursor.execute(count_query, params)
                total_count = cursor.fetchone()[0]
                
                # Get paginated data
                data_query = f"SELECT * {base_query} ORDER BY created_at DESC LIMIT ? OFFSET ?"
                cursor.execute(data_query, params + [pagination.limit, pagination.offset])
                rows = cursor.fetchall()
                
                # Process results
                properties = []
                for row in rows:
                    prop = dict(row)
                    # Parse raw_data if it exists
                    if prop.get('raw_data'):
                        try:
                            prop['raw_data'] = json.loads(prop['raw_data'])
                        except json.JSONDecodeError:
                            pass
                    properties.append(prop)
                
                return PaginatedResult(
                    data=properties,
                    total_count=total_count,
                    limit=pagination.limit,
                    offset=pagination.offset,
                    has_more=False  # Will be calculated in __post_init__
                )
                
        except Exception as e:
            logger.error(f"Error getting paginated properties: {str(e)}")
            return PaginatedResult(
                data=[],
                total_count=0,
                limit=pagination.limit,
                offset=pagination.offset,
                has_more=False
            )
    
    def get_recent_properties_paginated(self, days: int = 7,
                                       pagination: PaginationParams = PaginationParams()
                                       ) -> PaginatedResult:
        """
        Get recent properties with pagination support.
        
        Args:
            days: Number of days to look back
            pagination: Pagination parameters
            
        Returns:
            PaginatedResult containing recent properties and pagination metadata
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get total count
                cursor.execute('''
                    SELECT COUNT(*) FROM properties 
                    WHERE fetched_at > ?
                ''', (cutoff_date,))
                total_count = cursor.fetchone()[0]
                
                # Get paginated data
                cursor.execute('''
                    SELECT * FROM properties 
                    WHERE fetched_at > ? 
                    ORDER BY fetched_at DESC
                    LIMIT ? OFFSET ?
                ''', (cutoff_date, pagination.limit, pagination.offset))
                
                rows = cursor.fetchall()
                properties = [dict(row) for row in rows]
                
                return PaginatedResult(
                    data=properties,
                    total_count=total_count,
                    limit=pagination.limit,
                    offset=pagination.offset,
                    has_more=False  # Will be calculated in __post_init__
                )
                
        except Exception as e:
            logger.error(f"Error getting paginated recent properties: {str(e)}")
            return PaginatedResult(
                data=[],
                total_count=0,
                limit=pagination.limit,
                offset=pagination.offset,
                has_more=False
            )
    
    def _build_criteria_query(self, criteria: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """
        Build SQL query parts and parameters from search criteria.
        
        Args:
            criteria: Search criteria dictionary
            
        Returns:
            Tuple of (query_string, parameters_list)
        """
        query_parts = []
        params = []
        
        # Price range
        if 'price' in criteria:
            price_criteria = criteria['price']
            if 'min' in price_criteria:
                query_parts.append("AND price >= ?")
                params.append(price_criteria['min'])
            if 'max' in price_criteria:
                query_parts.append("AND price <= ?")
                params.append(price_criteria['max'])
        
        # Bedrooms
        if 'bedrooms' in criteria:
            bed_criteria = criteria['bedrooms']
            if 'min' in bed_criteria:
                query_parts.append("AND bedrooms >= ?")
                params.append(bed_criteria['min'])
        
        # Bathrooms
        if 'bathrooms' in criteria:
            bath_criteria = criteria['bathrooms']
            if 'min' in bath_criteria:
                query_parts.append("AND bathrooms >= ?")
                params.append(bath_criteria['min'])
        
        # Square feet
        if 'square_feet' in criteria:
            sqft_criteria = criteria['square_feet']
            if 'min' in sqft_criteria:
                query_parts.append("AND square_feet >= ?")
                params.append(sqft_criteria['min'])
            if 'max' in sqft_criteria:
                query_parts.append("AND square_feet <= ?")
                params.append(sqft_criteria['max'])
        
        # Cities
        if 'cities' in criteria and 'in' in criteria['cities']:
            cities = criteria['cities']['in']
            placeholders = ','.join(['?' for _ in cities])
            query_parts.append(f"AND city IN ({placeholders})")
            params.extend(cities)
        
        # Property type
        if 'property_type' in criteria and 'in' in criteria['property_type']:
            types = criteria['property_type']['in']
            placeholders = ','.join(['?' for _ in types])
            query_parts.append(f"AND property_type IN ({placeholders})")
            params.extend(types)
        
        # Days on market
        if 'days_on_market' in criteria:
            dom_criteria = criteria['days_on_market']
            if 'max' in dom_criteria:
                query_parts.append("AND days_on_market <= ?")
                params.append(dom_criteria['max'])
        
        return ' ' + ' '.join(query_parts), params
    
    def get_city_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics grouped by city."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT 
                        city,
                        COUNT(*) as property_count,
                        AVG(price) as avg_price,
                        MIN(price) as min_price,
                        MAX(price) as max_price,
                        AVG(square_feet) as avg_sqft,
                        AVG(days_on_market) as avg_days_on_market
                    FROM properties 
                    WHERE city IS NOT NULL AND city != ''
                    GROUP BY city
                    ORDER BY property_count DESC
                ''')
                
                rows = cursor.fetchall()
                
                columns = ['city', 'property_count', 'avg_price', 'min_price', 
                          'max_price', 'avg_sqft', 'avg_days_on_market']
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting city statistics: {str(e)}")
            return []
    
    def save_analysis_results(self, analysis_type: str, results: Dict[str, Any]) -> bool:
        """
        Save analysis results to the database.
        
        Args:
            analysis_type: Type of analysis performed
            results: Analysis results dictionary
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO analysis_results (analysis_type, results)
                    VALUES (?, ?)
                ''', (analysis_type, json.dumps(results)))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving analysis results: {str(e)}")
            return False
    
    def save_avm_valuation(self, property_id: str, address: str, avm_data: Dict[str, Any]) -> bool:
        """
        Save AVM (Automated Valuation Model) data for a property.
        
        Args:
            property_id: Unique property identifier
            address: Property address
            avm_data: AVM response data
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract key AVM metrics
                estimated_value = avm_data.get('value')
                estimated_rent = (avm_data.get('rent', {}).get('estimate')
                                if avm_data.get('rent') else None)
                confidence = avm_data.get('confidence')
                
                # Value ranges
                value_range = avm_data.get('valueRange', {})
                value_low = value_range.get('low')
                value_high = value_range.get('high')
                
                # Rent ranges
                rent_data = avm_data.get('rent', {})
                rent_range = rent_data.get('rentRange', {})
                rent_low = rent_range.get('low')
                rent_high = rent_range.get('high')
                
                # Comparables count
                comparables_count = len(avm_data.get('comparables', []))
                
                # Calculate investment metrics if possible
                cap_rate = None
                cash_flow = None
                roi_percentage = None
                
                if estimated_value and estimated_rent:
                    annual_rent = estimated_rent * 12
                    cap_rate = (annual_rent / estimated_value) * 100
                    # Estimate expenses as 30% of rent (industry standard)
                    estimated_expenses = annual_rent * 0.3
                    cash_flow = annual_rent - estimated_expenses
                    roi_percentage = (cash_flow / estimated_value) * 100
                
                cursor.execute('''
                    INSERT OR REPLACE INTO avm_valuations 
                    (property_id, address, estimated_value, estimated_rent, confidence_score,
                     value_range_low, value_range_high, rent_range_low, rent_range_high,
                     comparables_count, cap_rate, cash_flow, roi_percentage, raw_avm_data,
                     fetched_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    property_id, address, estimated_value, estimated_rent, confidence,
                    value_low, value_high, rent_low, rent_high, comparables_count,
                    cap_rate, cash_flow, roi_percentage, json.dumps(avm_data),
                    datetime.now().isoformat(), datetime.now().isoformat()
                ))
                
                conn.commit()
                logger.info(f"Saved AVM valuation for property {property_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving AVM valuation: {str(e)}")
            return False
    
    def save_market_statistics(self, zip_code: str, market_data: Dict[str, Any]) -> bool:
        """
        Save market statistics for a specific area.
        
        Args:
            zip_code: ZIP code for the market data
            market_data: Market statistics data
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Extract market data by property type
                for property_type, type_data in market_data.get('propertyTypes', {}).items():
                    for bedroom_count, bedroom_data in type_data.get('bedrooms', {}).items():
                        sale_data = bedroom_data.get('saleData', {})
                        rental_data = bedroom_data.get('rentalData', {})
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO market_statistics 
                            (zip_code, city, state, property_type, bedrooms,
                             avg_sale_price, median_sale_price, avg_rent_price, median_rent_price,
                             avg_price_per_sqft, avg_rent_per_sqft, inventory_count, 
                             avg_days_on_market, rent_yield_percentage, 
                             price_trend_3m, price_trend_6m, price_trend_12m,
                             raw_market_data, analysis_month, fetched_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            zip_code,
                            market_data.get('city'),
                            market_data.get('state'),
                            property_type,
                            int(bedroom_count) if bedroom_count.isdigit() else None,
                            sale_data.get('averagePrice'),
                            sale_data.get('medianPrice'),
                            rental_data.get('averagePrice'),
                            rental_data.get('medianPrice'),
                            sale_data.get('averagePricePerSquareFoot'),
                            rental_data.get('averagePricePerSquareFoot'),
                            sale_data.get('inventoryCount'),
                            sale_data.get('averageDaysOnMarket'),
                            # Calculate rent yield if we have both sale and rental prices
                            (((rental_data.get('averagePrice', 0) * 12) /
                              sale_data.get('averagePrice', 1) * 100)
                             if sale_data.get('averagePrice') else None),
                            # Price trends (would need historical data)
                            None, None, None,
                            json.dumps(market_data),
                            datetime.now().strftime('%Y-%m'),
                            datetime.now().isoformat()
                        ))
                
                conn.commit()
                logger.info(f"Saved market statistics for ZIP {zip_code}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving market statistics: {str(e)}")
            return False
    
    def save_property_comparables(self, source_property_id: str,
                                 comparables: List[Dict[str, Any]]) -> bool:
        """
        Save comparable properties data.
        
        Args:
            source_property_id: ID of the source property
            comparables: List of comparable properties
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for comp in comparables:
                    cursor.execute('''
                        INSERT OR REPLACE INTO property_comparables 
                        (source_property_id, comparable_property_id, comparable_address,
                         sale_price, sale_date, distance_miles, bedrooms, bathrooms,
                         square_feet, price_per_sqft, days_on_market, similarity_score,
                         raw_comparable_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        source_property_id,
                        comp.get('id'),
                        comp.get('address'),
                        comp.get('price'),
                        comp.get('saleDate'),
                        comp.get('distance'),
                        comp.get('bedrooms'),
                        comp.get('bathrooms'),
                        comp.get('squareFootage'),
                        comp.get('pricePerSquareFoot'),
                        comp.get('daysOnMarket'),
                        comp.get('similarityScore', 0.8),  # Default similarity
                        json.dumps(comp)
                    ))
                
                conn.commit()
                logger.info(f"Saved {len(comparables)} comparables "
                           f"for property {source_property_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving property comparables: {str(e)}")
            return False
    
    def save_investment_analysis(self, property_id: str, investment_data: Dict[str, Any]) -> bool:
        """
        Save investment analysis for a property.
        
        Args:
            property_id: Unique property identifier
            investment_data: Investment analysis results
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO investment_analysis 
                    (property_id, purchase_price, estimated_rent, estimated_expenses,
                     cap_rate, cash_on_cash_return, gross_yield, net_yield,
                     monthly_cash_flow, annual_cash_flow, break_even_ratio,
                     investment_score, risk_level, analysis_notes, analysis_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    property_id,
                    investment_data.get('purchase_price'),
                    investment_data.get('estimated_rent'),
                    investment_data.get('estimated_expenses'),
                    investment_data.get('cap_rate'),
                    investment_data.get('cash_on_cash_return'),
                    investment_data.get('gross_yield'),
                    investment_data.get('net_yield'),
                    investment_data.get('monthly_cash_flow'),
                    investment_data.get('annual_cash_flow'),
                    investment_data.get('break_even_ratio'),
                    investment_data.get('investment_score'),
                    investment_data.get('risk_level'),
                    investment_data.get('analysis_notes'),
                    datetime.now().date().isoformat()
                ))
                
                conn.commit()
                logger.info(f"Saved investment analysis for property {property_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving investment analysis: {str(e)}")
            return False
    
    def save_price_history(self, property_id: str, price: float, price_type: str, 
                          date_recorded: str, source: str, notes: Optional[str] = None) -> bool:
        """
        Save price history entry for a property.
        
        Args:
            property_id: Unique property identifier
            price: Price value
            price_type: Type of price ('list', 'sale', 'estimated')
            date_recorded: Date when price was recorded
            source: Source of the price data
            notes: Optional notes about the price
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO price_history 
                    (property_id, price, price_type, date_recorded, source, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (property_id, price, price_type, date_recorded, source, notes))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving price history: {str(e)}")
            return False
    
    def log_notification(self, notification_type: str, recipient: str, 
                        subject: str, status: str, property_count: int = 0) -> bool:
        """
        Log notification to the database.
        
        Args:
            notification_type: Type of notification (email, sms, etc.)
            recipient: Recipient of the notification
            subject: Subject/title of the notification
            status: Status (sent, failed, etc.)
            property_count: Number of properties in the notification
            
        Returns:
            True if logged successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO notifications_log 
                    (notification_type, recipient, subject, status, property_count)
                    VALUES (?, ?, ?, ?, ?)
                ''', (notification_type, recipient, subject, status, property_count))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error logging notification: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Get table counts
                tables = [
                    'properties', 'analysis_results', 'notifications_log',
                    'avm_valuations', 'market_statistics', 'property_comparables',
                    'investment_analysis', 'price_history', 'deal_analyses', 'deal_insights'
                ]
                
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        stats[f'{table}_count'] = count
                    except sqlite3.OperationalError:
                        # Table doesn't exist
                        stats[f'{table}_count'] = 0
                
                # Get date ranges for main tables
                for table in ['properties', 'avm_valuations', 'market_statistics']:
                    try:
                        date_column = ('created_at' if table == 'properties'
                                      else 'fetched_at')
                        cursor.execute(f"SELECT MIN({date_column}), "
                                      f"MAX({date_column}) FROM {table}")
                        date_range = cursor.fetchone()
                        stats[f'{table}_date_range'] = {
                            'earliest': date_range[0],
                            'latest': date_range[1]
                        }
                    except sqlite3.OperationalError:
                        stats[f'{table}_date_range'] = {'earliest': None, 'latest': None}
                
                # Get unique sources
                try:
                    cursor.execute("SELECT DISTINCT source FROM properties")
                    sources = [row[0] for row in cursor.fetchall()]
                    stats['data_sources'] = sources
                except sqlite3.OperationalError:
                    stats['data_sources'] = []
                
                # Get unique ZIP codes from market data
                try:
                    cursor.execute("SELECT DISTINCT zip_code FROM market_statistics")
                    zip_codes = [row[0] for row in cursor.fetchall()]
                    stats['market_zip_codes'] = zip_codes
                except sqlite3.OperationalError:
                    stats['market_zip_codes'] = []
                
                # Get top investment properties
                try:
                    cursor.execute('''
                        SELECT COUNT(*) FROM investment_analysis 
                        WHERE cap_rate >= 8.0 AND monthly_cash_flow >= 200
                    ''')
                    good_investments = cursor.fetchone()[0]
                    stats['good_investment_count'] = good_investments
                except sqlite3.OperationalError:
                    stats['good_investment_count'] = 0
                
                # Database file size
                stats['database_size_mb'] = (
                    self.db_path.stat().st_size / (1024 * 1024) 
                    if self.db_path.exists() else 0
                )
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """
        Clean up old data from the database.
        
        Args:
            days_to_keep: Number of days of data to keep
            
        Returns:
            Number of records deleted
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete old properties
                cursor.execute("DELETE FROM properties WHERE created_at < ?", (cutoff_date,))
                deleted_properties = cursor.rowcount
                
                # Delete old analysis results
                cursor.execute("DELETE FROM analysis_results WHERE created_at < ?", (cutoff_date,))
                deleted_analysis = cursor.rowcount
                
                # Delete old notification logs
                cursor.execute("DELETE FROM notifications_log WHERE sent_at < ?", (cutoff_date,))
                deleted_notifications = cursor.rowcount
                
                conn.commit()
                
                total_deleted = deleted_properties + deleted_analysis + deleted_notifications
                logger.info(f"Cleaned up {total_deleted} old records from database")
                
                return total_deleted
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {str(e)}")
            return 0
    
    # New retrieval methods for analysis data
    
    def get_avm_valuation(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get AVM valuation data for a specific property."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM avm_valuations 
                    WHERE property_id = ? 
                    ORDER BY fetched_at DESC LIMIT 1
                ''', (property_id,))
                
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    # Parse raw_avm_data if it exists
                    if result.get('raw_avm_data'):
                        try:
                            result['raw_avm_data'] = json.loads(result['raw_avm_data'])
                        except json.JSONDecodeError:
                            pass
                    return result
                return None
                
        except Exception as e:
            logger.error(f"Error getting AVM valuation: {str(e)}")
            return None
    
    def get_market_statistics(self, zip_code: str,
                             property_type: Optional[str] = None,
                             bedrooms: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get market statistics for a specific area."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM market_statistics WHERE zip_code = ?"
                params = [zip_code]
                
                if property_type:
                    query += " AND property_type = ?"
                    params.append(property_type)
                
                if bedrooms is not None:
                    query += " AND bedrooms = ?"
                    params.append(bedrooms)  # type: ignore
                
                query += " ORDER BY analysis_month DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    result = dict(row)
                    # Parse raw_market_data if it exists
                    if result.get('raw_market_data'):
                        try:
                            result['raw_market_data'] = json.loads(result['raw_market_data'])
                        except json.JSONDecodeError:
                            pass
                    results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"Error getting market statistics: {str(e)}")
            return []
    
    def get_property_comparables(self, property_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get comparable properties for a specific property."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM property_comparables 
                    WHERE source_property_id = ? 
                    ORDER BY similarity_score DESC LIMIT ?
                ''', (property_id, limit))
                
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    result = dict(row)
                    # Parse raw_comparable_data if it exists
                    if result.get('raw_comparable_data'):
                        try:
                            result['raw_comparable_data'] = json.loads(
                                result['raw_comparable_data'])
                        except json.JSONDecodeError:
                            pass
                    results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"Error getting property comparables: {str(e)}")
            return []
    
    def get_investment_analysis(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get investment analysis for a specific property."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM investment_analysis 
                    WHERE property_id = ? 
                    ORDER BY analysis_date DESC LIMIT 1
                ''', (property_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Error getting investment analysis: {str(e)}")
            return None
    
    def get_price_history(self, property_id: str) -> List[Dict[str, Any]]:
        """Get price history for a specific property."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM price_history 
                    WHERE property_id = ? 
                    ORDER BY date_recorded DESC
                ''', (property_id,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting price history: {str(e)}")
            return []
    
    def get_top_investment_opportunities(self, min_cap_rate: float = 8.0, 
                                       min_cash_flow: float = 200, 
                                       limit: int = 20) -> List[Dict[str, Any]]:
        """Get top investment opportunities based on financial metrics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT ia.*, p.address, p.city, p.state, p.price, p.bedrooms, p.bathrooms,
                           av.estimated_value, av.confidence_score
                    FROM investment_analysis ia
                    JOIN properties p ON ia.property_id = p.property_id
                    LEFT JOIN avm_valuations av ON ia.property_id = av.property_id
                    WHERE ia.cap_rate >= ? AND ia.monthly_cash_flow >= ?
                    ORDER BY ia.investment_score DESC, ia.cap_rate DESC
                    LIMIT ?
                ''', (min_cap_rate, min_cash_flow, limit))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting investment opportunities: {str(e)}")
            return []
    
    def get_market_trends(self, zip_code: str, months_back: int = 12) -> Dict[str, Any]:
        """Get market trends for a specific area over time."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get historical data
                cursor.execute('''
                    SELECT analysis_month, AVG(avg_sale_price) as avg_price,
                           AVG(avg_rent_price) as avg_rent,
                           AVG(avg_days_on_market) as avg_dom,
                           COUNT(*) as data_points
                    FROM market_statistics 
                    WHERE zip_code = ? AND analysis_month >= date('now', '-{} months')
                    GROUP BY analysis_month
                    ORDER BY analysis_month DESC
                '''.format(months_back), (zip_code,))
                
                rows = cursor.fetchall()
                historical_data = [dict(row) for row in rows]
                
                # Calculate trends
                trends = {
                    'zip_code': zip_code,
                    'historical_data': historical_data,
                    'price_trend': None,
                    'rent_trend': None,
                    'dom_trend': None
                }
                
                if len(historical_data) >= 2:
                    latest = historical_data[0]
                    previous = historical_data[-1]
                    
                    if latest['avg_price'] and previous['avg_price']:
                        price_change = (((latest['avg_price'] - previous['avg_price']) /
                                        previous['avg_price']) * 100)
                        trends['price_trend'] = round(price_change, 2)
                    
                    if latest['avg_rent'] and previous['avg_rent']:
                        rent_change = (((latest['avg_rent'] - previous['avg_rent']) /
                                       previous['avg_rent']) * 100)
                        trends['rent_trend'] = round(rent_change, 2)
                    
                    if latest['avg_dom'] and previous['avg_dom']:
                        dom_change = (((latest['avg_dom'] - previous['avg_dom']) /
                                      previous['avg_dom']) * 100)
                        trends['dom_trend'] = round(dom_change, 2)
                
                return trends
                
        except Exception as e:
            logger.error(f"Error getting market trends: {str(e)}")
            return {}
    
    def _prepare_property_data(self, prop: Dict[str, Any]) -> Tuple:
        """Prepare property data for database insertion."""
        return (
            prop.get('property_id', ''),
            prop.get('source', ''),
            prop.get('address', ''),
            prop.get('city', ''),
            prop.get('state', ''),
            prop.get('zip_code', ''),
            prop.get('price'),
            prop.get('bedrooms'),
            prop.get('bathrooms'),
            prop.get('square_feet'),
            prop.get('lot_size'),
            prop.get('year_built'),
            prop.get('property_type', ''),
            prop.get('listing_date', ''),
            prop.get('days_on_market'),
            prop.get('url', ''),
            prop.get('latitude'),
            prop.get('longitude'),
            prop.get('description', ''),
            json.dumps(prop) if isinstance(prop, dict) else '',
            prop.get('fetched_at', datetime.now().isoformat()),
            datetime.now().isoformat()
        )
    
    def _prepare_listing_data(self, listing: Dict[str, Any]) -> Tuple:
        """Prepare listing data for database insertion."""
        # Determine listing type based on source and data
        listing_type = 'sale'  # Default
        if 'rental' in listing.get('source', '').lower() or listing.get('rental_type'):
            listing_type = 'rental'
        
        return (
            listing.get('listing_id', listing.get('property_id', '')),  # Use listing_id if available
            listing.get('property_id', ''),
            listing.get('source', ''),
            listing_type,
            listing.get('address', ''),
            listing.get('city', ''),
            listing.get('state', ''),
            listing.get('zip_code', ''),
            listing.get('price'),
            listing.get('bedrooms'),
            listing.get('bathrooms'),
            listing.get('square_feet'),
            listing.get('lot_size'),
            listing.get('year_built'),
            listing.get('property_type', ''),
            listing.get('listing_date', ''),
            listing.get('days_on_market'),
            listing.get('status', 'active'),  # Default to active
            listing.get('url', ''),
            listing.get('latitude'),
            listing.get('longitude'),
            listing.get('description', ''),
            json.dumps(listing) if isinstance(listing, dict) else '',
            listing.get('fetched_at', datetime.now().isoformat()),
            datetime.now().isoformat()
        )
    
    def close(self) -> None:
        """Close database connections."""
        # For SQLite, connections are closed automatically when using context manager
        pass
    
    def create_deal_analysis_tables(self):
        """Create tables for deal analysis pipeline."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Main deal analyses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deal_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT UNIQUE NOT NULL,
                    property_address TEXT NOT NULL,
                    property_data TEXT NOT NULL,
                    avm_data TEXT,
                    market_data TEXT,
                    deal_score_data TEXT NOT NULL,
                    analysis_timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Deal insights summary table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deal_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    property_address TEXT NOT NULL,
                    zip_code TEXT,
                    property_type TEXT,
                    bedrooms INTEGER,
                    bathrooms REAL,
                    square_footage INTEGER,
                    asking_price INTEGER,
                    estimated_value INTEGER,
                    overall_score REAL NOT NULL,
                    deal_type TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    value_discount_pct REAL,
                    analysis_date DATE NOT NULL,
                    FOREIGN KEY (analysis_id) REFERENCES deal_analyses(analysis_id)
                )
            ''')
            
            # Create indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_deal_insights_score 
                ON deal_insights(overall_score DESC)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_deal_insights_type 
                ON deal_insights(deal_type)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_deal_insights_zip 
                ON deal_insights(zip_code)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_deal_insights_date 
                ON deal_insights(analysis_date DESC)
            ''')
            
            conn.commit()
            logger.info("Deal analysis database tables created successfully")
    
    def store_deal_analysis(self, analysis_id: str, property_data: Dict[str, Any],
                           avm_data: Optional[Dict[str, Any]],
                           market_data: Optional[Dict[str, Any]],
                           deal_score_data: Dict[str, Any],
                           analysis_timestamp: datetime):
        """Store complete deal analysis results."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store in main analyses table
            cursor.execute('''
                INSERT OR REPLACE INTO deal_analyses 
                (analysis_id, property_address, property_data, avm_data, 
                 market_data, deal_score_data, analysis_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_id, property_data.get('formattedAddress', ''),
                json.dumps(property_data),
                json.dumps(avm_data) if avm_data else None,
                json.dumps(market_data) if market_data else None,
                json.dumps(deal_score_data),
                analysis_timestamp.isoformat()
            ))
            
            # Store in insights summary table
            cursor.execute('''
                INSERT OR REPLACE INTO deal_insights 
                (analysis_id, property_address, zip_code, property_type, bedrooms, bathrooms, 
                 square_footage, asking_price, estimated_value, overall_score, deal_type, 
                 confidence, value_discount_pct, analysis_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_id, property_data.get('formattedAddress', ''),
                property_data.get('zipCode'),
                property_data.get('propertyType'), property_data.get('bedrooms'),
                property_data.get('bathrooms'),
                property_data.get('squareFootage'), property_data.get('price'),
                deal_score_data.get('estimated_value'),
                deal_score_data.get('overall_score'), deal_score_data.get('deal_type'),
                deal_score_data.get('confidence'), deal_score_data.get('value_discount_pct'),
                analysis_timestamp.date().isoformat()
            ))
            
            conn.commit()
    
    def get_best_deals(self, zip_code: Optional[str] = None,
                      min_score: float = 70.0,
                      limit: int = 20) -> List[Dict[str, Any]]:
        """Get the best deals from recent analyses."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = ('SELECT * FROM deal_insights WHERE overall_score >= ? '
                    'AND analysis_date >= date("now", "-30 days")')
            params = [min_score]
            
            if zip_code:
                query += ' AND zip_code = ?'
                params.append(zip_code)  # type: ignore
            
            query += ' ORDER BY overall_score DESC LIMIT ?'
            params.append(limit)  # type: ignore
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
