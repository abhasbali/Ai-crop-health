from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
import logging
import re

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not username or not email or not password:
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, password_error = validate_password(password)
        if not is_valid:
            return jsonify({'error': password_error}), 400
        
        # Check if user already exists
        existing_user = User.get_by_email(email)
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Create new user
        user = User.create(username, email, password)
        if not user:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Generate access token
        access_token = create_access_token(identity=str(user.id))
        
        logger.info(f"New user registered: {email}")
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
    
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Authenticate user
        user = User.authenticate(email, password)
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate access token
        access_token = create_access_token(identity=str(user.id))
        
        logger.info(f"User logged in: {email}")
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.get_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    """Refresh access token"""
    try:
        current_user_id = int(get_jwt_identity())
        user = User.get_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Generate new access token
        new_token = create_access_token(identity=str(current_user_id))
        
        return jsonify({
            'access_token': new_token,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
