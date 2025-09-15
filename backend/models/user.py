# Use SQLite for demo
try:
    from database.sqlite_db import UserModel as DbUserModel, verify_password
except ImportError:
    from database.db import UserModel as DbUserModel, verify_password
import logging

logger = logging.getLogger(__name__)

class User:
    def __init__(self, id=None, username=None, email=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.created_at = created_at
    
    @classmethod
    def create(cls, username, email, password):
        """Create a new user"""
        if not username or not email or not password:
            return None
        
        user_data = DbUserModel.create_user(username, email, password)
        if user_data:
            return cls(**user_data)
        return None
    
    @classmethod
    def authenticate(cls, email, password):
        """Authenticate user with email and password"""
        if not email or not password:
            return None
        
        user_data = DbUserModel.get_user_by_email(email)
        if user_data and verify_password(password, user_data['password_hash']):
            return cls(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                created_at=user_data['created_at']
            )
        return None
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID"""
        user_data = DbUserModel.get_user_by_id(user_id)
        if user_data:
            return cls(**user_data)
        return None
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        user_data = DbUserModel.get_user_by_email(email)
        if user_data:
            return cls(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                created_at=user_data['created_at']
            )
        return None
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': str(self.created_at) if self.created_at else None
        }
    
    def __repr__(self):
        return f"<User {self.username}>"
