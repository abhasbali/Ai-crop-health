import os
import numpy as np
import logging
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

# Import real satellite data and agricultural model
from .satellite_data import get_comprehensive_field_data
from .real_model import RealAgriculturalModel, create_and_train_real_model

logger = logging.getLogger(__name__)

# Global variables for model and scaler
loaded_model = None
scaler = None

def create_dummy_model():
    """Create a dummy model for demonstration purposes"""
    try:
        # Create a simple RandomForest model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        
        # Generate dummy training data (features: NDVI, temperature, humidity, soil_moisture, pH)
        X_dummy = np.random.rand(1000, 5)
        X_dummy[:, 0] = np.random.uniform(0.1, 0.9, 1000)  # NDVI
        X_dummy[:, 1] = np.random.uniform(15, 35, 1000)    # Temperature
        X_dummy[:, 2] = np.random.uniform(30, 90, 1000)    # Humidity
        X_dummy[:, 3] = np.random.uniform(20, 80, 1000)    # Soil moisture
        X_dummy[:, 4] = np.random.uniform(5.5, 8.5, 1000)  # pH
        
        # Create dummy labels based on simple rules
        y_dummy = []
        for i in range(1000):
            ndvi = X_dummy[i, 0]
            temp = X_dummy[i, 1]
            humidity = X_dummy[i, 2]
            soil_moisture = X_dummy[i, 3]
            ph = X_dummy[i, 4]
            
            # Simple rule-based classification
            if ndvi > 0.7 and temp < 30 and humidity > 50 and soil_moisture > 40 and 6 <= ph <= 7.5:
                y_dummy.append(2)  # Good
            elif ndvi > 0.4 and temp < 35 and humidity > 30 and soil_moisture > 20:
                y_dummy.append(1)  # Moderate
            else:
                y_dummy.append(0)  # Poor
        
        y_dummy = np.array(y_dummy)
        
        # Train the model
        model.fit(X_dummy, y_dummy)
        
        # Create scaler
        scaler = StandardScaler()
        scaler.fit(X_dummy)
        
        logger.info("Created dummy model successfully")
        return model, scaler
        
    except Exception as e:
        logger.error(f"Error creating dummy model: {e}")
        return None, None

def load_pytorch_model(model_path):
    """Load PyTorch model (.pt or .pth file)"""
    try:
        import torch
        import torch.nn as nn
        
        # Define a simple neural network for crop health prediction
        class CropHealthNet(nn.Module):
            def __init__(self, input_size=5, hidden_size=64, num_classes=3):
                super(CropHealthNet, self).__init__()
                self.fc1 = nn.Linear(input_size, hidden_size)
                self.relu1 = nn.ReLU()
                self.fc2 = nn.Linear(hidden_size, hidden_size)
                self.relu2 = nn.ReLU()
                self.fc3 = nn.Linear(hidden_size, num_classes)
                self.softmax = nn.Softmax(dim=1)
            
            def forward(self, x):
                x = self.relu1(self.fc1(x))
                x = self.relu2(self.fc2(x))
                x = self.fc3(x)
                return self.softmax(x)
        
        # Try to load existing model
        if os.path.exists(model_path):
            model = torch.load(model_path, map_location='cpu')
            logger.info(f"Loaded PyTorch model from {model_path}")
        else:
            # Create and save a new model with dummy weights
            model = CropHealthNet()
            torch.save(model, model_path)
            logger.info(f"Created new PyTorch model and saved to {model_path}")
        
        model.eval()  # Set to evaluation mode
        return model
        
    except ImportError:
        logger.warning("PyTorch not available, falling back to dummy model")
        return None
    except Exception as e:
        logger.error(f"Error loading PyTorch model: {e}")
        return None

def load_keras_model(model_path):
    """Load Keras/TensorFlow model (.h5 file)"""
    try:
        import tensorflow as tf
        from tensorflow import keras
        
        if os.path.exists(model_path):
            model = keras.models.load_model(model_path)
            logger.info(f"Loaded Keras model from {model_path}")
        else:
            # Create a simple model
            model = keras.Sequential([
                keras.layers.Dense(64, activation='relu', input_shape=(5,)),
                keras.layers.Dense(64, activation='relu'),
                keras.layers.Dense(3, activation='softmax')
            ])
            
            model.compile(
                optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Train with dummy data
            X_dummy = np.random.rand(1000, 5)
            y_dummy = np.random.randint(0, 3, 1000)
            model.fit(X_dummy, y_dummy, epochs=5, verbose=0)
            
            # Save the model
            model.save(model_path)
            logger.info(f"Created new Keras model and saved to {model_path}")
        
        return model
        
    except ImportError:
        logger.warning("TensorFlow/Keras not available, falling back to dummy model")
        return None
    except Exception as e:
        logger.error(f"Error loading Keras model: {e}")
        return None

def load_model(model_path=None):
    """Load the real agricultural crop health prediction model"""
    global loaded_model, scaler
    
    try:
        # Try to load real agricultural model first
        real_model_path = '/app/model/real_crop_model.joblib'
        
        # Check if real model exists
        if os.path.exists(real_model_path):
            logger.info("Loading real agricultural model")
            real_model = RealAgriculturalModel()
            if real_model.load_model(real_model_path):
                loaded_model = real_model
                scaler = real_model.scaler
                logger.info("Real agricultural model loaded successfully")
                return real_model
        
        # Create and train new real model if none exists
        logger.info("Creating and training new real agricultural model")
        real_model = create_and_train_real_model(real_model_path)
        if real_model:
            loaded_model = real_model
            scaler = real_model.scaler
            logger.info("New real agricultural model created and loaded")
            return real_model
        
        # Fallback to legacy model loading for backward compatibility
        if model_path and os.path.exists(model_path):
            _, ext = os.path.splitext(model_path)
            
            if ext in ['.pt', '.pth']:
                # PyTorch model
                model = load_pytorch_model(model_path)
                if model:
                    loaded_model = model
                    # Create a simple scaler
                    scaler = StandardScaler()
                    scaler.mean_ = np.array([0.5, 25, 60, 50, 7])  # Default means
                    scaler.scale_ = np.array([0.2, 8, 20, 20, 1])  # Default scales
                    return model
            
            elif ext == '.h5':
                # Keras model
                model = load_keras_model(model_path)
                if model:
                    loaded_model = model
                    scaler = StandardScaler()
                    scaler.mean_ = np.array([0.5, 25, 60, 50, 7])
                    scaler.scale_ = np.array([0.2, 8, 20, 20, 1])
                    return model
            
            elif ext in ['.pkl', '.joblib']:
                # Try to load as real model first
                try:
                    real_model = RealAgriculturalModel()
                    if real_model.load_model(model_path):
                        loaded_model = real_model
                        scaler = real_model.scaler
                        return real_model
                except:
                    # Fall back to simple joblib load
                    model = joblib.load(model_path)
                    loaded_model = model
                    logger.info(f"Loaded legacy model from {model_path}")
                    return model
        
        # Final fallback to dummy model
        logger.warning("Falling back to dummy model - real model creation failed")
        model, model_scaler = create_dummy_model()
        if model:
            loaded_model = model
            scaler = model_scaler
            return model
        else:
            logger.error("Failed to create any model")
            return None
            
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

def predict_crop_health(features=None, latitude=None, longitude=None, use_real_data=True):
    """Predict crop health using real satellite data and the loaded model"""
    global loaded_model, scaler
    
    try:
        if loaded_model is None:
            return None, "Model not loaded"
        
        # Use real satellite data if coordinates provided
        if use_real_data and latitude is not None and longitude is not None:
            logger.info(f"Using real satellite data for prediction at ({latitude}, {longitude})")
            
            # Try to fetch real satellite data first
            from .real_satellite_api import get_real_satellite_data
            real_sat_data = get_real_satellite_data(latitude, longitude)
            
            if real_sat_data.get('success') and 'ndvi' in real_sat_data:
                # Use real satellite NDVI
                ndvi = real_sat_data['ndvi']['value']
                logger.info(f"🛰️ Using real satellite NDVI: {ndvi:.3f}")
                
                # Get environmental data separately
                real_data = get_comprehensive_field_data(latitude, longitude)
            else:
                # Fallback to comprehensive field data
                real_data = get_comprehensive_field_data(latitude, longitude)
                if real_data.get('success'):
                    ndvi = real_data['ndvi']['value']
                else:
                    ndvi = 0.5  # Default
            
            if real_data.get('success'):
                # Extract features from real data (ndvi already set above)
                # Only update ndvi if we didn't get it from real satellite data
                if 'ndvi' not in locals():
                    ndvi = real_data['ndvi']['value']
                temperature = real_data['weather']['temperature']
                humidity = real_data['weather']['humidity']
                soil_moisture = real_data['soil']['moisture']
                soil_ph = real_data['soil']['ph']
                
                # Add additional features for the real model
                from datetime import datetime
                day_of_year = datetime.now().timetuple().tm_yday
                
                # Estimate additional parameters
                precipitation = 20.0  # Default weekly precipitation
                solar_radiation = 22.0  # Default solar radiation
                
                # Create feature array for real model (9 features)
                real_features = np.array([[
                    ndvi, temperature, humidity, soil_moisture, soil_ph,
                    precipitation, solar_radiation, day_of_year, latitude
                ]])
                
                # Check if this is our real agricultural model
                if isinstance(loaded_model, RealAgriculturalModel):
                    logger.info("Using real agricultural model with satellite data")
                    result = loaded_model.predict(real_features)
                    
                    # Add real data sources info
                    result.update({
                        'data_sources': {
                            'ndvi_source': real_data['ndvi']['source'],
                            'weather_source': real_data['weather']['source'],
                            'soil_source': real_data['soil']['source']
                        },
                        'real_data_quality': real_data['data_quality'],
                        'coordinates': {'latitude': latitude, 'longitude': longitude},
                        'timestamp': real_data['timestamp']
                    })
                    
                    logger.info(f"Real satellite prediction: Health={result['health_score']:.1f}, NDVI={result['ndvi_value']:.3f}")
                    return result, None
                else:
                    # Use first 5 features for legacy models
                    features = real_features[:, :5]
            else:
                logger.warning(f"Failed to fetch real data: {real_data.get('error')}")
                # Fall back to provided features or defaults
                if features is None:
                    features = np.array([[0.6, 25, 60, 45, 6.5]])  # Default values
        
        # Handle provided features or use defaults
        if features is None:
            logger.info("No features provided, using default agricultural values")
            features = np.array([[0.6, 25, 60, 45, 6.5]])  # Default good agricultural conditions
        
        # Ensure features is a 2D array
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        # Handle different model types
        if isinstance(loaded_model, RealAgriculturalModel):
            logger.info("Using real agricultural model with provided features")
            result = loaded_model.predict(features)
            return result, None
        
        # Legacy model handling
        # Handle different feature sizes for legacy models
        if features.shape[1] < 5:
            # Pad with average values
            padding = np.full((features.shape[0], 5 - features.shape[1]), 0.5)
            features = np.hstack([features, padding])
        elif features.shape[1] > 5:
            # Take first 5 features
            features = features[:, :5]
        
        # Scale features if scaler is available
        if scaler is not None:
            try:
                features_scaled = scaler.transform(features)
            except Exception:
                # If scaling fails, use original features
                features_scaled = features
        else:
            features_scaled = features
        
        # Make prediction with legacy model
        if hasattr(loaded_model, 'predict_proba'):
            # Scikit-learn model
            probabilities = loaded_model.predict_proba(features_scaled)
            predictions = loaded_model.predict(features_scaled)
        elif hasattr(loaded_model, '__call__'):
            # Check if it's a PyTorch model
            try:
                import torch
                if isinstance(loaded_model, torch.nn.Module):
                    # PyTorch model
                    with torch.no_grad():
                        features_tensor = torch.FloatTensor(features_scaled)
                        probabilities = loaded_model(features_tensor).numpy()
                        predictions = np.argmax(probabilities, axis=1)
                else:
                    raise Exception("Unknown model type")
            except ImportError:
                # Try Keras/TensorFlow
                try:
                    probabilities = loaded_model.predict(features_scaled)
                    predictions = np.argmax(probabilities, axis=1)
                except Exception:
                    return None, "Failed to make predictions"
        else:
            return None, "Model doesn't support prediction"
        
        # Calculate average health score and confidence for legacy models
        avg_probabilities = np.mean(probabilities, axis=0)
        health_score = float(np.sum(avg_probabilities * [0, 50, 100]))  # Poor=0, Moderate=50, Good=100
        confidence = float(np.max(avg_probabilities) * 100)
        
        # Determine status
        avg_prediction = np.mean(predictions)
        if avg_prediction >= 1.5:
            status = "Good"
        elif avg_prediction >= 0.5:
            status = "Moderate"
        else:
            status = "Poor"
        
        # Calculate NDVI (use first feature if available, otherwise estimate)
        if features.shape[1] > 0:
            avg_ndvi = float(np.mean(features[:, 0]))
        else:
            avg_ndvi = 0.5
        
        result = {
            'health_score': round(health_score, 2),
            'ndvi_value': round(avg_ndvi, 3),
            'confidence': round(confidence, 2),
            'status': status,
            'predictions': predictions.tolist(),
            'probabilities': probabilities.tolist(),
            'model_type': 'Legacy Model'
        }
        
        logger.info(f"Legacy prediction result: {result}")
        return result, None
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return None, str(e)

def get_model_info():
    """Get information about the loaded model"""
    global loaded_model
    
    if loaded_model is None:
        return {
            "status": "No model loaded",
            "available": False
        }
    
    # Check if this is our real agricultural model
    if isinstance(loaded_model, RealAgriculturalModel):
        return loaded_model.get_model_info()
    
    # Legacy model info
    model_type = type(loaded_model).__name__
    return {
        "status": "Legacy model loaded",
        "type": model_type,
        "available": True,
        "is_real_model": False,
        "data_sources": ["Synthetic data"]
    }
