from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
import logging
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routes
from routes.auth import auth_bp
from routes.fields import fields_bp
from routes.predictions import predictions_bp

# Import database initialization (use SQLite for demo)
try:
    from database.sqlite_db import init_db
    logger = logging.getLogger(__name__)
    logger.info("Using SQLite database")
except ImportError:
    from database.db import init_db
    logger = logging.getLogger(__name__)
    logger.info("Using PostgreSQL database")
from utils.model_loader import load_model

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'supersecretjwt')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize extensions
CORS(app, 
     origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://frontend:3000"], 
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])
jwt = JWTManager(app)

# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    logger.warning("Expired token accessed")
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    logger.warning(f"Invalid token: {error_string}")
    return jsonify({'error': 'Invalid token'}), 422

@jwt.unauthorized_loader
def missing_token_callback(error_string):
    logger.warning(f"Missing token: {error_string}")
    return jsonify({'error': 'Authorization token required'}), 401

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request logging middleware
@app.before_request
def log_request_info():
    logger.info(f'{request.method} {request.url} - Headers: {dict(request.headers)}')

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(fields_bp, url_prefix='/api/fields')
app.register_blueprint(predictions_bp, url_prefix='/api/predictions')

# Global model instance
model = None

def startup():
    """Initialize database and load model on startup"""
    global model
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Load ML model
        model_path = os.getenv('MODEL_PATH', '/app/model/model.pt')
        model = load_model(model_path)
        if model:
            logger.info(f"Model loaded successfully from {model_path}")
        else:
            logger.warning("Model loading failed, using dummy predictions")
            
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")

# Call startup function
startup()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'timestamp': str(os.popen('date').read().strip())
    })

@app.route('/api/status', methods=['GET'])
@jwt_required()
def get_status():
    """Get application status"""
    current_user = int(get_jwt_identity())
    return jsonify({
        'user': current_user,
        'model_status': 'loaded' if model else 'not_loaded',
        'database_status': 'connected'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({'error': 'File too large'}), 413

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
