from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
# Use SQLite for demo
try:
    from database.sqlite_db import PredictionModel, FieldModel
    # AlertModel not implemented in SQLite demo, using dummy
    class AlertModel:
        @staticmethod
        def get_alerts_by_user(user_id, unread_only=False):
            return []
        
        @staticmethod
        def create_alert(field_id, user_id, alert_type, message, severity):
            return None
except ImportError:
    from database.db import PredictionModel, FieldModel, AlertModel
from utils.data_processing import save_uploaded_file, process_uploaded_data, validate_processed_data, cleanup_file
from utils.model_loader import predict_crop_health, get_model_info
from utils.ndvi import (
    calculate_ndvi_from_data, generate_comprehensive_spectral_analysis, 
    interpret_ndvi, interpret_ndwi, interpret_ndsi, 
    calculate_all_indices, create_index_stack_analysis
)
from utils.hyperspectral_analysis import HyperspectralAnalyzer
import logging
import json
import os
from datetime import datetime

predictions_bp = Blueprint('predictions', __name__)
logger = logging.getLogger(__name__)

@predictions_bp.route('/upload-data', methods=['POST'])
@jwt_required()
def upload_data():
    """Upload and process crop data file (CSV, NPZ, or JSON)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        field_id = request.form.get('field_id')
        
        # Validate field_id if provided
        if field_id:
            try:
                field_id = int(field_id)
                field = FieldModel.get_field_by_id(field_id, user_id)
                if not field:
                    return jsonify({'error': 'Field not found'}), 404
            except ValueError:
                return jsonify({'error': 'Invalid field_id'}), 400
        
        # Save the uploaded file
        filepath, error = save_uploaded_file(file)
        if error:
            return jsonify({'error': error}), 400
        
        try:
            # Process the uploaded data
            processed_data, process_error = process_uploaded_data(filepath)
            if process_error:
                cleanup_file(filepath)
                return jsonify({'error': f'Processing error: {process_error}'}), 400
            
            # Validate processed data
            is_valid, validation_message = validate_processed_data(processed_data)
            if not is_valid:
                cleanup_file(filepath)
                return jsonify({'error': f'Validation error: {validation_message}'}), 400
            
            # Calculate comprehensive spectral analysis
            spectral_analysis = generate_comprehensive_spectral_analysis(processed_data.get('data', {}))
            
            response_data = {
                'message': 'File processed successfully',
                'filename': os.path.basename(filepath),
                'data_shape': processed_data.get('shape', [0, 0]),
                'columns': processed_data.get('columns', []),
                'spectral_analysis': spectral_analysis,
                'field_id': field_id,
                'ready_for_prediction': True,
                'multi_spectral_enabled': True
            }
            
            # Store file path in session or temporary storage for prediction
            # In a production system, you might use Redis or database storage
            response_data['file_id'] = os.path.basename(filepath)
            
            logger.info(f"Data uploaded successfully for user {user_id}, shape: {processed_data.get('shape')}")
            return jsonify(response_data), 200
            
        except Exception as e:
            cleanup_file(filepath)
            raise e
    
    except Exception as e:
        logger.error(f"Upload data error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@predictions_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    """Run AI model prediction on uploaded data"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        field_id = data.get('field_id')
        file_id = data.get('file_id')
        
        # Validate field_id
        if not field_id:
            return jsonify({'error': 'field_id is required'}), 400
        
        try:
            field_id = int(field_id)
            field = FieldModel.get_field_by_id(field_id, user_id)
            if not field:
                return jsonify({'error': 'Field not found'}), 404
        except ValueError:
            return jsonify({'error': 'Invalid field_id'}), 400
        
        # Get model info
        model_info = get_model_info()
        if not model_info.get('available'):
            return jsonify({'error': 'AI model not available'}), 503
        
        # Process data based on input
        processed_data = None
        filename = 'direct_input'
        
        if file_id:
            # Use previously uploaded file
            filepath = os.path.join('/app/uploads', file_id)
            if os.path.exists(filepath):
                processed_data, process_error = process_uploaded_data(filepath)
                if process_error:
                    return jsonify({'error': f'Processing error: {process_error}'}), 400
                filename = file_id
            else:
                return jsonify({'error': 'Uploaded file not found'}), 404
        
        elif 'data' in data or any(key in data for key in ['temperature', 'humidity', 'soil_moisture', 'ph', 'precipitation']):
            # Use directly provided data (either in 'data' dict or as direct parameters)
            if 'data' in data:
                input_data = data['data']
            else:
                # Extract direct parameters into data format
                input_data = {
                    'temperature': [data.get('temperature', 25.0)],
                    'humidity': [data.get('humidity', 65.0)],
                    'soil_moisture': [data.get('soil_moisture', 40.0)],
                    'ph': [data.get('ph', 6.8)],
                    'precipitation': [data.get('precipitation', 10.0)]
                }
            
            # Convert input data to processed format
            processed_data = {
                'data': input_data,
                'features': None,
                'shape': (0, 0),
                'columns': list(input_data.keys()) if isinstance(input_data, dict) else []
            }
            
            # Create feature matrix from input data
            import numpy as np
            if isinstance(input_data, dict):
                features = []
                for key in ['ndvi', 'temperature', 'humidity', 'soil_moisture', 'ph']:
                    if key in input_data:
                        values = input_data[key]
                        if not isinstance(values, list):
                            values = [values]
                        features.append(values)
                
                if features:
                    # Ensure all feature arrays have the same length
                    max_len = max(len(f) for f in features)
                    padded_features = []
                    for f in features:
                        if len(f) < max_len:
                            f.extend([f[-1]] * (max_len - len(f)))
                        padded_features.append(f)
                    
                    processed_data['features'] = np.array(padded_features).T
                    processed_data['shape'] = processed_data['features'].shape
        else:
            return jsonify({'error': 'Either file_id or data must be provided'}), 400
        
        # Validate processed data
        is_valid, validation_message = validate_processed_data(processed_data)
        if not is_valid:
            return jsonify({'error': f'Validation error: {validation_message}'}), 400
        
        # Get field coordinates for real satellite data
        field_coords = FieldModel.get_field_by_id(field_id, user_id)
        latitude = field_coords.get('latitude') if field_coords else None
        longitude = field_coords.get('longitude') if field_coords else None
        
        # Run prediction with real satellite data if coordinates available
        if latitude is not None and longitude is not None:
            logger.info(f"Using real satellite data for field {field_id} at ({latitude}, {longitude})")
            prediction_result, pred_error = predict_crop_health(
                features=processed_data['features'],
                latitude=float(latitude),
                longitude=float(longitude),
                use_real_data=True
            )
        else:
            # Fall back to features-only prediction
            logger.info("Using features-only prediction (no coordinates available)")
            features = processed_data['features']
            prediction_result, pred_error = predict_crop_health(features)
        
        if pred_error:
            return jsonify({'error': f'Prediction error: {pred_error}'}), 500
        
        # Determine NDVI source and avoid overwriting real NDVI
        # Check if we used real satellite data by looking for coordinates usage and data sources
        used_real_satellite_data = (
            latitude is not None and longitude is not None and
            prediction_result and (
                prediction_result.get('data_sources') is not None or  # Has real data sources
                prediction_result.get('coordinates') is not None or    # Has coordinates info
                'Geographic estimation' in str(prediction_result.get('data_sources', {}))  # Used geographic estimation
            )
        )
        
        if used_real_satellite_data and prediction_result.get('ndvi_value') is not None:
            avg_ndvi = float(prediction_result['ndvi_value'])
            ndvi_status = "success"
            logger.info(f"Keeping NDVI from real satellite data: {avg_ndvi:.3f}")
        else:
            # Fall back to calculating NDVI from provided data (bands or existing ndvi in payload)
            avg_ndvi, ndvi_status = calculate_ndvi_from_data(processed_data.get('data', {}))
            prediction_result['ndvi_value'] = avg_ndvi
            logger.info(f"Using calculated NDVI from input data: {avg_ndvi:.3f}")
        
        # Interpret NDVI
        ndvi_interpretation = interpret_ndvi(avg_ndvi)
        
        # Save prediction to database
        prediction_data = {
            'model_info': model_info,
            'ndvi_interpretation': ndvi_interpretation,
            'feature_shape': processed_data.get('shape', [0, 0]),
            'columns': processed_data.get('columns', [])
        }
        
        saved_prediction = PredictionModel.create_prediction(
            field_id=field_id,
            user_id=user_id,
            data_filename=filename,
            health_score=prediction_result['health_score'],
            ndvi_value=prediction_result['ndvi_value'],
            confidence=prediction_result['confidence'],
            status=prediction_result['status'],
            prediction_data=json.dumps(prediction_data)
        )
        
        if not saved_prediction:
            logger.warning("Failed to save prediction to database")
        
        # Create alert if crop health is poor
        if prediction_result['status'] == 'Poor' or prediction_result['health_score'] < 30:
            alert_message = f"Field '{field['name']}' shows poor crop health (Score: {prediction_result['health_score']}, NDVI: {avg_ndvi:.3f}). Immediate attention required."
            AlertModel.create_alert(
                field_id=field_id,
                user_id=user_id,
                alert_type='poor_health',
                message=alert_message,
                severity='high'
            )
            logger.info(f"Created poor health alert for field {field_id}")
        
        # Clean up temporary file if it was uploaded for this prediction
        if file_id and os.path.exists(os.path.join('/app/uploads', file_id)):
            cleanup_file(os.path.join('/app/uploads', file_id))
        
        # Prepare response
        response_data = {
            'prediction': prediction_result,
            'ndvi_interpretation': ndvi_interpretation,
            'field': {
                'id': field['id'],
                'name': field['name'],
                'location': field['location']
            },
            'model_info': model_info,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Prediction completed for user {user_id}, field {field_id}: {prediction_result['status']}")
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@predictions_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get alerts for poor crop health fields"""
    try:
        user_id = int(get_jwt_identity())
        
        # Get query parameters
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        # Fetch alerts
        alerts = AlertModel.get_alerts_by_user(user_id, unread_only=unread_only)
        
        # Add additional information to alerts
        for alert in alerts:
            # Add relative time information
            created_at = alert.get('created_at')
            if created_at:
                try:
                    alert_time = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
                    time_diff = datetime.utcnow() - alert_time.replace(tzinfo=None)
                    
                    if time_diff.days > 0:
                        alert['relative_time'] = f"{time_diff.days} days ago"
                    elif time_diff.seconds > 3600:
                        alert['relative_time'] = f"{time_diff.seconds // 3600} hours ago"
                    else:
                        alert['relative_time'] = f"{time_diff.seconds // 60} minutes ago"
                except Exception:
                    alert['relative_time'] = 'Recently'
        
        response_data = {
            'alerts': alerts,
            'total_count': len(alerts),
            'unread_count': len([a for a in alerts if not a.get('is_read', True)])
        }
        
        logger.info(f"Retrieved {len(alerts)} alerts for user {user_id}")
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@predictions_bp.route('/history/<int:field_id>', methods=['GET'])
@jwt_required()
def get_prediction_history(field_id):
    """Get prediction history for a specific field"""
    try:
        user_id = int(get_jwt_identity())
        
        # Verify field ownership
        field = FieldModel.get_field_by_id(field_id, user_id)
        if not field:
            return jsonify({'error': 'Field not found'}), 404
        
        # Get predictions for the field
        predictions = PredictionModel.get_predictions_by_field(field_id, user_id)
        
        # Process predictions for response
        for prediction in predictions:
            # Parse prediction_data if it exists
            if prediction.get('prediction_data'):
                try:
                    # Check if it's already a dict or needs to be parsed
                    if isinstance(prediction['prediction_data'], str):
                        prediction['prediction_data'] = json.loads(prediction['prediction_data'])
                    elif isinstance(prediction['prediction_data'], dict):
                        # Already a dict, no need to parse
                        pass
                    else:
                        # If it's neither string nor dict, set to None
                        prediction['prediction_data'] = None
                except (json.JSONDecodeError, TypeError):
                    prediction['prediction_data'] = None
            
            # Format timestamps
            created_at = prediction.get('created_at')
            if created_at:
                try:
                    prediction['created_at'] = datetime.fromisoformat(str(created_at)).isoformat()
                except Exception:
                    pass
        
        response_data = {
            'field': field,
            'predictions': predictions,
            'total_count': len(predictions)
        }
        
        logger.info(f"Retrieved {len(predictions)} predictions for field {field_id}")
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Get prediction history error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@predictions_bp.route('/model-info', methods=['GET'])
@jwt_required()
def model_info():
    """Get information about the loaded AI model"""
    try:
        info = get_model_info()
        return jsonify(info), 200
    except Exception as e:
        logger.error(f"Model info error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@predictions_bp.route('/multi-spectral-analysis', methods=['POST'])
@jwt_required(optional=True)
def multi_spectral_analysis():
    """Perform comprehensive multi-spectral analysis (NDVI, NDWI, MNDWI, NDSI)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if field_id is provided for real satellite data
        field_id = data.get('field_id')
        input_data = None
        real_ndvi = None
        
        if field_id:
            # Try to use real satellite data
            try:
                # Get authenticated user if available
                user_id = get_jwt_identity()
                if user_id:
                    user_id = int(user_id)
                
                if user_id:
                    field = FieldModel.get_field_by_id(int(field_id), user_id)
                    if field:
                        latitude = field.get('latitude')
                        longitude = field.get('longitude')
                        
                        if latitude and longitude:
                            # Get real satellite data
                            from utils.real_satellite_api import get_real_satellite_data
                            field_data = get_real_satellite_data(latitude, longitude)
                            
                            if field_data.get('success'):
                                input_data = field_data.get('spectral_bands', {})
                                # Get NDVI from real satellite data
                                if 'ndvi' in field_data and 'value' in field_data['ndvi']:
                                    real_ndvi = field_data['ndvi']['value']
                                elif 'calculated_indices' in field_data and 'ndvi' in field_data['calculated_indices']:
                                    real_ndvi = field_data['calculated_indices']['ndvi']['mean']
                                else:
                                    real_ndvi = None
                                    
                                if real_ndvi:
                                    logger.info(f"🛰️ Using real satellite NDVI for multi-spectral analysis: {real_ndvi:.3f}")
            except Exception as e:
                logger.warning(f"Could not fetch real satellite data for field {field_id}: {e}")
        
        # Fallback to provided data if real satellite data not available
        if not input_data:
            if 'spectral_bands' in data:
                input_data = data['spectral_bands']
            elif 'data' in data:
                input_data = data['data']
            else:
                return jsonify({'error': 'No spectral_bands or data provided'}), 400
        
        logger.info(f"Processing multi-spectral analysis with bands: {list(input_data.keys())}")
        
        # Generate comprehensive spectral analysis with real NDVI if available
        if real_ndvi is not None:
            # Use real NDVI value in the input data
            if 'ndvi' not in input_data:
                input_data['ndvi'] = [real_ndvi] * 100  # Create array with real NDVI
            logger.info(f"Using real NDVI in multi-spectral analysis: {real_ndvi:.3f}")
        
        spectral_analysis = generate_comprehensive_spectral_analysis(input_data)
        
        # Extract key metrics for backward compatibility
        avg_ndvi = 0.5  # Default
        if 'indices_stats' in spectral_analysis and 'NDVI' in spectral_analysis['indices_stats']:
            avg_ndvi = spectral_analysis['indices_stats']['NDVI']['mean']
        
        # Return the spectral analysis directly (frontend expects this structure)
        response_data = spectral_analysis.copy()
        response_data.update({
            'success': True,
            'average_ndvi': avg_ndvi,  # For backward compatibility
            'timestamp': datetime.utcnow().isoformat(),
            'analysis_type': 'comprehensive_multi_spectral'
        })
        
        logger.info(f"Multi-spectral analysis completed")
        logger.info(f"Indices calculated: {spectral_analysis.get('summary', {}).get('indices_calculated', [])}")
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Multi-spectral analysis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@predictions_bp.route('/ndvi-analysis', methods=['POST'])
@jwt_required()
def ndvi_analysis():
    """Perform NDVI analysis on provided data (legacy endpoint)"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Process NDVI data
        input_data = data['data']
        avg_ndvi, ndvi_status = calculate_ndvi_from_data(input_data)
        
        # Generate comprehensive analysis but return NDVI-focused response
        spectral_analysis = generate_comprehensive_spectral_analysis(input_data)
        
        # Extract NDVI-specific data
        ndvi_interpretation = spectral_analysis.get('interpretations', {}).get('NDVI', interpret_ndvi(avg_ndvi))
        ndvi_stats = spectral_analysis.get('indices_stats', {}).get('NDVI', {})
        
        response_data = {
            'average_ndvi': avg_ndvi,
            'status': ndvi_status,
            'interpretation': ndvi_interpretation,
            'statistics': ndvi_stats,
            'timestamp': datetime.utcnow().isoformat(),
            'full_spectral_analysis_available': True  # Hint to frontend
        }
        
        logger.info(f"NDVI analysis completed for user {user_id}, average NDVI: {avg_ndvi:.3f}")
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"NDVI analysis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@predictions_bp.route('/hyperspectral-visualization', methods=['POST'])
@jwt_required()
def hyperspectral_visualization():
    """Generate hyperspectral field visualization with pest risk assessment"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        field_id = data.get('field_id')
        crop_type = data.get('crop_type', 'general')
        
        # Validate field_id
        if not field_id:
            return jsonify({'error': 'field_id is required'}), 400
        
        try:
            field_id = int(field_id)
            field = FieldModel.get_field_by_id(field_id, user_id)
            if not field:
                return jsonify({'error': 'Field not found'}), 404
        except ValueError:
            return jsonify({'error': 'Invalid field_id'}), 400
        
        # Get field coordinates
        latitude = field.get('latitude')
        longitude = field.get('longitude')
        
        if latitude is None or longitude is None:
            return jsonify({'error': 'Field coordinates not available'}), 400
        
        # Get spectral data - either from uploaded data or use real satellite data
        spectral_data = data.get('spectral_data')
        field_data = None
        
        if not spectral_data:
            # Use real satellite data for consistent analysis
            from utils.real_satellite_api import get_real_satellite_data
            field_data = get_real_satellite_data(latitude, longitude)
            
            if field_data.get('success'):
                spectral_data = field_data.get('spectral_bands', {})
                # Use real NDVI if available from satellite data
                if 'ndvi' in field_data and 'value' in field_data['ndvi']:
                    real_ndvi = field_data['ndvi']['value']
                    logger.info(f"🛰️ Using real satellite NDVI for hyperspectral analysis: {real_ndvi:.3f}")
                elif 'calculated_indices' in field_data and 'ndvi' in field_data['calculated_indices']:
                    real_ndvi = field_data['calculated_indices']['ndvi']['mean']
                    logger.info(f"📊 Using calculated NDVI from real bands: {real_ndvi:.3f}")
                else:
                    real_ndvi = None
                    logger.warning("No NDVI found in real satellite data")
            else:
                # Fallback to comprehensive field data
                from utils.satellite_data import get_comprehensive_field_data
                field_data = get_comprehensive_field_data(latitude, longitude)
                spectral_data = field_data.get('spectral_bands', {})
                real_ndvi = field_data.get('ndvi', {}).get('value') if field_data else None
                logger.info(f"⚠️ Using fallback satellite data: NDVI={real_ndvi if real_ndvi else 'N/A'}")
        
        # Get weather data
        weather_data = data.get('weather_data')
        if not weather_data:
            from utils.satellite_data import SatelliteDataProvider
            provider = SatelliteDataProvider()
            weather_result = provider.get_weather_data(latitude, longitude)
            weather_data = {
                'temperature': weather_result.get('avg_temperature', 25),
                'humidity': weather_result.get('avg_humidity', 60),
                'pressure': weather_result.get('pressure', 1013)
            }
        
        # Initialize hyperspectral analyzer
        analyzer = HyperspectralAnalyzer()
        
        # If we have real field data, pass the real NDVI to maintain consistency
        real_ndvi = None
        if field_data and 'ndvi' in field_data:
            real_ndvi = field_data['ndvi'].get('value')
            logger.info(f"Passing real NDVI to hyperspectral analyzer: {real_ndvi:.3f}")
        
        # Generate comprehensive visualization
        visualization_result = analyzer.generate_field_visualization(
            spectral_data=spectral_data,
            weather_data=weather_data,
            field_coords=(latitude, longitude),
            crop_type=crop_type,
            real_ndvi=real_ndvi  # Pass real NDVI to preserve consistency
        )
        
        if not visualization_result.get('success'):
            return jsonify({
                'error': 'Failed to generate visualization', 
                'details': visualization_result.get('error', 'Unknown error')
            }), 500
        
        # Add field information
        visualization_result['field_info'] = {
            'id': field['id'],
            'name': field['name'],
            'location': field['location'],
            'coordinates': {'latitude': latitude, 'longitude': longitude},
            'crop_type': crop_type
        }
        
        # Add spectral indices explanations
        visualization_result['spectral_explanations'] = {
            'ndvi': {
                'name': 'Normalized Difference Vegetation Index',
                'formula': '(NIR - Red) / (NIR + Red)',
                'interpretation': {
                    'high': '0.6-0.9: Healthy vegetation',
                    'medium': '0.3-0.5: Moderate growth/stress',
                    'low': '<0.2: Poor vegetation/bare soil'
                },
                'significance': 'Primary indicator of plant health and biomass'
            },
            'ndwi': {
                'name': 'Normalized Difference Water Index',
                'formula': '(NIR - SWIR) / (NIR + SWIR)',
                'interpretation': {
                    'high': '>0.5: Good water availability',
                    'medium': '0.2-0.5: Moderate water content',
                    'low': '<0.2: Water stress/drought'
                },
                'significance': 'Indicates water content in soil and plants'
            },
            'ndsi': {
                'name': 'Normalized Difference Soil Index',
                'formula': '(SWIR - Green) / (SWIR + Green)',
                'interpretation': {
                    'high': '>0.4: Bare soil/degraded land',
                    'medium': '0.2-0.4: Partially vegetated',
                    'low': '<0.2: Well-covered vegetation'
                },
                'significance': 'Detects soil exposure and land degradation'
            },
            'mndwi': {
                'name': 'Modified Normalized Difference Water Index',
                'formula': '(Green - SWIR) / (Green + SWIR)',
                'interpretation': {
                    'positive': '>0: Water bodies/very wet areas',
                    'near_zero': '~0: Mixed water-vegetation',
                    'negative': '<0: Dry land/vegetation'
                },
                'significance': 'Enhanced water body detection and moisture mapping'
            },
            'red_edge_ndvi': {
                'name': 'Red Edge NDVI',
                'formula': '(NIR - Red Edge) / (NIR + Red Edge)',
                'interpretation': {
                    'high': '>0.6: Excellent vegetation health',
                    'medium': '0.3-0.6: Good vegetation condition',
                    'low': '<0.3: Stressed or sparse vegetation'
                },
                'significance': 'More sensitive to chlorophyll content and early stress detection'
            }
        }
        
        logger.info(f"Hyperspectral visualization completed for user {user_id}, field {field_id}")
        return jsonify(visualization_result), 200
    
    except Exception as e:
        logger.error(f"Hyperspectral visualization error: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@predictions_bp.route('/field-health-assessment/<int:field_id>', methods=['GET'])
@jwt_required()
def field_health_assessment(field_id):
    """Get comprehensive field health assessment including pest risks"""
    try:
        user_id = int(get_jwt_identity())
        
        # Verify field ownership
        field = FieldModel.get_field_by_id(field_id, user_id)
        if not field:
            return jsonify({'error': 'Field not found'}), 404
        
        # Get query parameters
        crop_type = request.args.get('crop_type', 'general')
        include_recommendations = request.args.get('include_recommendations', 'true').lower() == 'true'
        
        latitude = field.get('latitude')
        longitude = field.get('longitude')
        
        if latitude is None or longitude is None:
            return jsonify({'error': 'Field coordinates not available'}), 400
        
        # Get comprehensive field data
        from utils.satellite_data import get_comprehensive_field_data, SatelliteDataProvider
        
        field_data = get_comprehensive_field_data(latitude, longitude)
        
        # Prepare data for analysis
        spectral_data = field_data.get('spectral_bands', {})
        weather_data = {
            'temperature': field_data.get('weather', {}).get('temperature', 25),
            'humidity': field_data.get('weather', {}).get('humidity', 60),
            'pressure': field_data.get('weather', {}).get('pressure', 1013)
        }
        
        # Initialize analyzer
        analyzer = HyperspectralAnalyzer()
        
        # Calculate spectral indices
        indices = analyzer.calculate_spectral_indices(spectral_data)
        
        # Generate field grid for spatial analysis
        field_grid = analyzer.generate_field_grid(spectral_data)
        
        # Analyze health zones
        health_zones = analyzer.analyze_health_zones(indices, field_grid, crop_type)
        
        # Assess pest risk
        pest_assessment = analyzer.assess_pest_risk(indices, weather_data, (latitude, longitude), crop_type)
        
        # Generate recommendations if requested
        recommendations = []
        if include_recommendations:
            recommendations = analyzer.generate_recommendations(health_zones, pest_assessment, crop_type)
        
        response_data = {
            'field_info': {
                'id': field['id'],
                'name': field['name'],
                'location': field['location'],
                'coordinates': {'latitude': latitude, 'longitude': longitude},
                'crop_type': crop_type
            },
            'assessment_timestamp': datetime.utcnow().isoformat(),
            'spectral_indices': indices,
            'health_zones': health_zones,
            'pest_assessment': pest_assessment,
            'environmental_conditions': {
                'temperature': weather_data['temperature'],
                'humidity': weather_data['humidity'],
                'weather_source': field_data.get('weather', {}).get('source', 'Unknown')
            },
            'recommendations': recommendations,
            'data_quality': field_data.get('data_quality', {})
        }
        
        logger.info(f"Field health assessment completed for user {user_id}, field {field_id}")
        return jsonify(response_data), 200
    
    except Exception as e:
        logger.error(f"Field health assessment error: {e}")
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
