import os
import sqlite3
import logging
from contextlib import contextmanager
import hashlib
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'crop_health.db')

@contextmanager
def get_db_connection():
    """Context manager for SQLite database connections"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def init_db():
    """Initialize SQLite database tables"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create fields table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fields (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    location TEXT,
                    latitude REAL,
                    longitude REAL,
                    area_hectares REAL,
                    crop_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    field_id INTEGER REFERENCES fields(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    data_filename TEXT,
                    health_score REAL,
                    ndvi_value REAL,
                    confidence REAL,
                    status TEXT,
                    prediction_data TEXT,  -- JSON as TEXT in SQLite
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    field_id INTEGER REFERENCES fields(id) ON DELETE CASCADE,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    alert_type TEXT,
                    message TEXT,
                    severity TEXT,
                    is_read BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fields_user_id ON fields(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_field_id ON predictions(field_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id)")
            
            conn.commit()
            logger.info(f"SQLite database initialized at {DB_PATH}")
            
            # Create demo user if it doesn't exist
            cursor.execute("SELECT id FROM users WHERE email = ?", ('demo@crophealth.com',))
            if not cursor.fetchone():
                demo_password_hash = hashlib.sha256('demo123'.encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash)
                    VALUES (?, ?, ?)
                """, ('demo', 'demo@crophealth.com', demo_password_hash))
                
                user_id = cursor.lastrowid
                
                # Create demo field
                cursor.execute("""
                    INSERT INTO fields (user_id, name, location, latitude, longitude, area_hectares, crop_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, 'Demo Farm Field', 'New York, USA', 40.7128, -74.0060, 25.5, 'Corn'))
                
                conn.commit()
                logger.info("Demo user and field created")
            
    except Exception as e:
        logger.error(f"Error initializing SQLite database: {e}")
        raise

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

# User model functions for SQLite
class UserModel:
    @staticmethod
    def create_user(username, email, password):
        """Create a new user"""
        password_hash = hash_password(password)
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash)
                    VALUES (?, ?, ?)
                """, (username, email, password_hash))
                
                user_id = cursor.lastrowid
                conn.commit()
                
                # Fetch the created user
                cursor.execute("""
                    SELECT id, username, email, created_at
                    FROM users WHERE id = ?
                """, (user_id,))
                user = cursor.fetchone()
                return dict(user) if user else None
        except sqlite3.IntegrityError as e:
            logger.error(f"User creation failed: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, username, email, password_hash, created_at
                    FROM users WHERE email = ?
                """, (email,))
                user = cursor.fetchone()
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, username, email, created_at
                    FROM users WHERE id = ?
                """, (user_id,))
                user = cursor.fetchone()
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None

# Field model functions for SQLite
class FieldModel:
    @staticmethod
    def create_field(user_id, name, location, latitude, longitude, area_hectares, crop_type):
        """Create a new field"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO fields (user_id, name, location, latitude, longitude, area_hectares, crop_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, name, location, latitude, longitude, area_hectares, crop_type))
                
                field_id = cursor.lastrowid
                conn.commit()
                
                # Fetch the created field
                cursor.execute("""
                    SELECT id, user_id, name, location, latitude, longitude, area_hectares, crop_type, created_at, updated_at
                    FROM fields WHERE id = ?
                """, (field_id,))
                field = cursor.fetchone()
                return dict(field) if field else None
        except Exception as e:
            logger.error(f"Error creating field: {e}")
            return None
    
    @staticmethod
    def get_fields_by_user(user_id):
        """Get all fields for a user"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, user_id, name, location, latitude, longitude, area_hectares, crop_type, created_at, updated_at
                    FROM fields WHERE user_id = ?
                    ORDER BY created_at DESC
                """, (user_id,))
                fields = cursor.fetchall()
                return [dict(field) for field in fields]
        except Exception as e:
            logger.error(f"Error fetching fields: {e}")
            return []
    
    @staticmethod
    def get_field_by_id(field_id, user_id):
        """Get a specific field by ID and user"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, user_id, name, location, latitude, longitude, area_hectares, crop_type, created_at, updated_at
                    FROM fields WHERE id = ? AND user_id = ?
                """, (field_id, user_id))
                field = cursor.fetchone()
                return dict(field) if field else None
        except Exception as e:
            logger.error(f"Error fetching field: {e}")
            return None

# Prediction model functions for SQLite
class PredictionModel:
    @staticmethod
    def create_prediction(field_id, user_id, data_filename, health_score, ndvi_value, confidence, status, prediction_data=None):
        """Create a new prediction"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                prediction_json = json.dumps(prediction_data) if prediction_data else None
                cursor.execute("""
                    INSERT INTO predictions (field_id, user_id, data_filename, health_score, ndvi_value, confidence, status, prediction_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (field_id, user_id, data_filename, health_score, ndvi_value, confidence, status, prediction_json))
                
                prediction_id = cursor.lastrowid
                conn.commit()
                
                # Fetch the created prediction
                cursor.execute("""
                    SELECT id, field_id, user_id, data_filename, health_score, ndvi_value, confidence, status, prediction_data, created_at
                    FROM predictions WHERE id = ?
                """, (prediction_id,))
                prediction = cursor.fetchone()
                
                if prediction:
                    result = dict(prediction)
                    # Parse JSON data
                    if result['prediction_data']:
                        result['prediction_data'] = json.loads(result['prediction_data'])
                    return result
                return None
        except Exception as e:
            logger.error(f"Error creating prediction: {e}")
            return None
    
    @staticmethod
    def get_predictions_by_field(field_id, user_id):
        """Get all predictions for a field"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, field_id, user_id, data_filename, health_score, ndvi_value, confidence, status, prediction_data, created_at
                    FROM predictions WHERE field_id = ? AND user_id = ?
                    ORDER BY created_at DESC
                """, (field_id, user_id))
                predictions = cursor.fetchall()
                
                result = []
                for prediction in predictions:
                    pred_dict = dict(prediction)
                    # Parse JSON data
                    if pred_dict['prediction_data']:
                        pred_dict['prediction_data'] = json.loads(pred_dict['prediction_data'])
                    result.append(pred_dict)
                return result
        except Exception as e:
            logger.error(f"Error fetching predictions: {e}")
            return []
