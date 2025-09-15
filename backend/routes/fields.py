from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
# Use SQLite for demo
try:
    from database.sqlite_db import FieldModel
except ImportError:
    from database.db import FieldModel
import logging

fields_bp = Blueprint('fields', __name__)
logger = logging.getLogger(__name__)

@fields_bp.route('/debug', methods=['POST'])
def debug_create_field():
    """Debug endpoint to test field creation without auth"""
    try:
        data = request.get_json()
        logger.info(f"Debug - Received data: {data}")
        return jsonify({'message': 'Debug endpoint working', 'data': data}), 200
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@fields_bp.route('', methods=['GET'])
@jwt_required()
def list_fields():
    try:
        user_id = int(get_jwt_identity())
        fields = FieldModel.get_fields_by_user(user_id)
        return jsonify({'fields': fields}), 200
    except Exception as e:
        logger.error(f"List fields error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@fields_bp.route('', methods=['POST'])
@jwt_required()
def create_field():
    try:
        user_id = int(get_jwt_identity())
        logger.info(f"Creating field for user: {user_id}")
        
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        if not data:
            logger.warning("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name')
        location = data.get('location')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        area_hectares = data.get('area_hectares')
        crop_type = data.get('crop_type')
        
        logger.info(f"Field data - Name: {name}, Location: {location}, Lat: {latitude}, Lng: {longitude}, Area: {area_hectares}, Crop: {crop_type}")
        
        if not name:
            logger.warning("Field name is missing")
            return jsonify({'error': 'Field name is required'}), 400
        
        field = FieldModel.create_field(user_id, name, location, latitude, longitude, area_hectares, crop_type)
        if not field:
            logger.error("Failed to create field in database")
            return jsonify({'error': 'Failed to create field'}), 500
        
        logger.info(f"Field created successfully: {field}")
        return jsonify({'field': field}), 201
    except Exception as e:
        logger.error(f"Create field error: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Internal server error'}), 500

@fields_bp.route('/<int:field_id>', methods=['GET'])
@jwt_required()
def get_field(field_id):
    try:
        user_id = int(get_jwt_identity())
        field = FieldModel.get_field_by_id(field_id, user_id)
        if not field:
            return jsonify({'error': 'Field not found'}), 404
        return jsonify({'field': field}), 200
    except Exception as e:
        logger.error(f"Get field error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@fields_bp.route('/<int:field_id>', methods=['PUT'])
@jwt_required()
def update_field(field_id):
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        field = FieldModel.update_field(field_id, user_id, 
                                        name=data.get('name'),
                                        location=data.get('location'),
                                        latitude=data.get('latitude'),
                                        longitude=data.get('longitude'),
                                        area_hectares=data.get('area_hectares'),
                                        crop_type=data.get('crop_type'))
        
        if not field:
            return jsonify({'error': 'Field not found or no changes made'}), 404
        return jsonify({'field': field}), 200
    except Exception as e:
        logger.error(f"Update field error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@fields_bp.route('/<int:field_id>', methods=['DELETE'])
@jwt_required()
def delete_field(field_id):
    try:
        user_id = int(get_jwt_identity())
        deleted = FieldModel.delete_field(field_id, user_id)
        if not deleted:
            return jsonify({'error': 'Field not found'}), 404
        return jsonify({'message': 'Field deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Delete field error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

