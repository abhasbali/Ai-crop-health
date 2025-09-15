import os
import logging
# Use SQLite for demo purposes
try:
    # Try to use SQLite for demo
    from .sqlite_db import (
        get_db_connection, init_db, hash_password, verify_password,
        UserModel, FieldModel, PredictionModel
    )
    logger = logging.getLogger(__name__)
    logger.info("Using SQLite database for demo")
except ImportError:
    # Fallback to PostgreSQL if needed
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from contextlib import contextmanager
    import hashlib
    from datetime import datetime
    logger = logging.getLogger(__name__)
    logger.info("Using PostgreSQL database")

logger = logging.getLogger(__name__)

# Database connection configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://cropuser:croppass@localhost:5432/cropdb')

def get_db_config():
    """Parse database URL and return connection parameters"""
    url = DATABASE_URL.replace('postgresql+psycopg2://', '')
    if '@' in url:
        credentials, host_db = url.split('@')
        user, password = credentials.split(':')
        host_port, database = host_db.split('/')
        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host, port = host_port, '5432'
    else:
        # Fallback for simple configurations
        host, port, user, password, database = 'localhost', '5432', 'cropuser', 'croppass', 'cropdb'
    
    return {
        'host': host,
        'port': int(port),
        'user': user,
        'password': password,
        'database': database
    }

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    config = get_db_config()
    conn = None
    try:
        conn = psycopg2.connect(**config, cursor_factory=RealDictCursor)
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
    """Initialize database tables"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Create users table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create fields table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS fields (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        name VARCHAR(100) NOT NULL,
                        location VARCHAR(255),
                        latitude DECIMAL(10, 8),
                        longitude DECIMAL(11, 8),
                        area_hectares DECIMAL(10, 2),
                        crop_type VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create predictions table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        id SERIAL PRIMARY KEY,
                        field_id INTEGER REFERENCES fields(id) ON DELETE CASCADE,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        data_filename VARCHAR(255),
                        health_score DECIMAL(5, 2),
                        ndvi_value DECIMAL(5, 2),
                        confidence DECIMAL(5, 2),
                        status VARCHAR(20),
                        prediction_data JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create alerts table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS alerts (
                        id SERIAL PRIMARY KEY,
                        field_id INTEGER REFERENCES fields(id) ON DELETE CASCADE,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        alert_type VARCHAR(50),
                        message TEXT,
                        severity VARCHAR(20),
                        is_read BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cur.execute("CREATE INDEX IF NOT EXISTS idx_fields_user_id ON fields(user_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_predictions_field_id ON predictions(field_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id)")
                
                conn.commit()
                logger.info("Database tables created successfully")
                
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

# User model functions
class UserModel:
    @staticmethod
    def create_user(username, email, password):
        """Create a new user"""
        password_hash = hash_password(password)
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO users (username, email, password_hash)
                        VALUES (%s, %s, %s) RETURNING id, username, email, created_at
                    """, (username, email, password_hash))
                    user = cur.fetchone()
                    conn.commit()
                    return dict(user) if user else None
        except psycopg2.IntegrityError as e:
            logger.error(f"User creation failed: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, username, email, password_hash, created_at
                        FROM users WHERE email = %s
                    """, (email,))
                    user = cur.fetchone()
                    return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, username, email, created_at
                        FROM users WHERE id = %s
                    """, (user_id,))
                    user = cur.fetchone()
                    return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None

# Field model functions
class FieldModel:
    @staticmethod
    def create_field(user_id, name, location, latitude, longitude, area_hectares, crop_type):
        """Create a new field"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO fields (user_id, name, location, latitude, longitude, area_hectares, crop_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s) 
                        RETURNING id, user_id, name, location, latitude, longitude, area_hectares, crop_type, created_at, updated_at
                    """, (user_id, name, location, latitude, longitude, area_hectares, crop_type))
                    field = cur.fetchone()
                    conn.commit()
                    return dict(field) if field else None
        except Exception as e:
            logger.error(f"Error creating field: {e}")
            return None
    
    @staticmethod
    def get_fields_by_user(user_id):
        """Get all fields for a user"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT f.*, p.health_score, p.status, p.created_at as last_prediction
                        FROM fields f
                        LEFT JOIN LATERAL (
                            SELECT health_score, status, created_at
                            FROM predictions 
                            WHERE field_id = f.id 
                            ORDER BY created_at DESC 
                            LIMIT 1
                        ) p ON true
                        WHERE f.user_id = %s
                        ORDER BY f.created_at DESC
                    """, (user_id,))
                    fields = cur.fetchall()
                    return [dict(field) for field in fields]
        except Exception as e:
            logger.error(f"Error fetching fields: {e}")
            return []
    
    @staticmethod
    def get_field_by_id(field_id, user_id):
        """Get a field by ID (with user ownership check)"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT * FROM fields 
                        WHERE id = %s AND user_id = %s
                    """, (field_id, user_id))
                    field = cur.fetchone()
                    return dict(field) if field else None
        except Exception as e:
            logger.error(f"Error fetching field: {e}")
            return None
    
    @staticmethod
    def update_field(field_id, user_id, **kwargs):
        """Update a field"""
        try:
            set_clauses = []
            values = []
            for key, value in kwargs.items():
                if value is not None:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)
            
            if not set_clauses:
                return None
            
            values.extend([field_id, user_id])
            
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        UPDATE fields 
                        SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s AND user_id = %s
                        RETURNING *
                    """, values)
                    field = cur.fetchone()
                    conn.commit()
                    return dict(field) if field else None
        except Exception as e:
            logger.error(f"Error updating field: {e}")
            return None
    
    @staticmethod
    def delete_field(field_id, user_id):
        """Delete a field"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM fields 
                        WHERE id = %s AND user_id = %s
                        RETURNING id
                    """, (field_id, user_id))
                    result = cur.fetchone()
                    conn.commit()
                    return result is not None
        except Exception as e:
            logger.error(f"Error deleting field: {e}")
            return False

# Prediction model functions
class PredictionModel:
    @staticmethod
    def create_prediction(field_id, user_id, data_filename, health_score, ndvi_value, confidence, status, prediction_data=None):
        """Create a new prediction"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO predictions (field_id, user_id, data_filename, health_score, ndvi_value, confidence, status, prediction_data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING *
                    """, (field_id, user_id, data_filename, health_score, ndvi_value, confidence, status, prediction_data))
                    prediction = cur.fetchone()
                    conn.commit()
                    return dict(prediction) if prediction else None
        except Exception as e:
            logger.error(f"Error creating prediction: {e}")
            return None
    
    @staticmethod
    def get_predictions_by_field(field_id, user_id):
        """Get all predictions for a field"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT p.*, f.name as field_name
                        FROM predictions p
                        JOIN fields f ON p.field_id = f.id
                        WHERE p.field_id = %s AND p.user_id = %s
                        ORDER BY p.created_at DESC
                    """, (field_id, user_id))
                    predictions = cur.fetchall()
                    return [dict(prediction) for prediction in predictions]
        except Exception as e:
            logger.error(f"Error fetching predictions: {e}")
            return []

# Alert model functions
class AlertModel:
    @staticmethod
    def create_alert(field_id, user_id, alert_type, message, severity):
        """Create a new alert"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO alerts (field_id, user_id, alert_type, message, severity)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING *
                    """, (field_id, user_id, alert_type, message, severity))
                    alert = cur.fetchone()
                    conn.commit()
                    return dict(alert) if alert else None
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return None
    
    @staticmethod
    def get_alerts_by_user(user_id, unread_only=False):
        """Get alerts for a user"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    where_clause = "WHERE a.user_id = %s"
                    if unread_only:
                        where_clause += " AND a.is_read = FALSE"
                    
                    cur.execute(f"""
                        SELECT a.*, f.name as field_name
                        FROM alerts a
                        JOIN fields f ON a.field_id = f.id
                        {where_clause}
                        ORDER BY a.created_at DESC
                    """, (user_id,))
                    alerts = cur.fetchall()
                    return [dict(alert) for alert in alerts]
        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []
