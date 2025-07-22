"""
Database Manager Module

This module handles database operations for storing and retrieving real estate data.
Supports SQLite by default with options for PostgreSQL integration.
"""

import sqlite3
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json

logger = logging.getLogger(__name__)


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
