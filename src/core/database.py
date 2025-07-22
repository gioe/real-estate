"""
Database Manager Module

This module handles database operations for storing and retrieving real estate data.
Supports SQLite by default with options for PostgreSQL integration.
Includes comprehensive pagination support for handling large datasets.
"""

import sqlite3
import logging
from typing import Dict, List, Any, Optional, Tuple, NamedTuple
from datetime import datetime, timedelta
from pathlib import Path
import json
from dataclasses import dataclass

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
                
                # Create analysis_results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        analysis_type TEXT NOT NULL,
                        results TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
                    CREATE INDEX IF NOT EXISTS idx_properties_listing_date 
                    ON properties(listing_date)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_properties_fetched_at 
                    ON properties(fetched_at)
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
                                       pagination: PaginationParams = PaginationParams()) -> PaginatedResult:
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
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get table counts
                cursor.execute("SELECT COUNT(*) FROM properties")
                property_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM analysis_results")
                analysis_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM notifications_log")
                notification_count = cursor.fetchone()[0]
                
                # Get date ranges
                cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM properties")
                date_range = cursor.fetchone()
                
                # Get unique sources
                cursor.execute("SELECT DISTINCT source FROM properties")
                sources = [row[0] for row in cursor.fetchall()]
                
                return {
                    'property_count': property_count,
                    'analysis_count': analysis_count,
                    'notification_count': notification_count,
                    'date_range': {
                        'earliest': date_range[0],
                        'latest': date_range[1]
                    },
                    'sources': sources,
                    'database_size_mb': self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
                }
                
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
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_deal_insights_score ON deal_insights(overall_score DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_deal_insights_type ON deal_insights(deal_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_deal_insights_zip ON deal_insights(zip_code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_deal_insights_date ON deal_insights(analysis_date DESC)')
            
            conn.commit()
            logger.info("Deal analysis database tables created successfully")
    
    def store_deal_analysis(self, analysis_id: str, property_data: Dict[str, Any], 
                           avm_data: Optional[Dict[str, Any]], market_data: Optional[Dict[str, Any]],
                           deal_score_data: Dict[str, Any], analysis_timestamp: datetime):
        """Store complete deal analysis results."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Store in main analyses table
            cursor.execute('''
                INSERT OR REPLACE INTO deal_analyses 
                (analysis_id, property_address, property_data, avm_data, market_data, deal_score_data, analysis_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_id, property_data.get('formattedAddress', ''),
                json.dumps(property_data), json.dumps(avm_data) if avm_data else None,
                json.dumps(market_data) if market_data else None, json.dumps(deal_score_data),
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
                analysis_id, property_data.get('formattedAddress', ''), property_data.get('zipCode'),
                property_data.get('propertyType'), property_data.get('bedrooms'), property_data.get('bathrooms'),
                property_data.get('squareFootage'), property_data.get('price'), deal_score_data.get('estimated_value'),
                deal_score_data.get('overall_score'), deal_score_data.get('deal_type'),
                deal_score_data.get('confidence'), deal_score_data.get('value_discount_pct'),
                analysis_timestamp.date().isoformat()
            ))
            
            conn.commit()
    
    def get_best_deals(self, zip_code: Optional[str] = None, min_score: float = 70.0, limit: int = 20) -> List[Dict[str, Any]]:
        """Get the best deals from recent analyses."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = 'SELECT * FROM deal_insights WHERE overall_score >= ? AND analysis_date >= date("now", "-30 days")'
            params = [min_score]
            
            if zip_code:
                query += ' AND zip_code = ?'
                params.append(zip_code)
            
            query += ' ORDER BY overall_score DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
