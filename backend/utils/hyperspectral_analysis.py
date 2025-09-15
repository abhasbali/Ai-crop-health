"""
Hyperspectral Analysis and Visualization for Agricultural Monitoring
Implements comprehensive crop health, soil health, and pest risk assessment
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging
from typing import Dict, List, Tuple, Optional
import base64
from io import BytesIO
import json

# Custom JSON encoder to handle numpy types and other serialization issues
def convert_for_json(obj):
    """Convert numpy types and other non-serializable objects for JSON"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_for_json(item) for item in obj]
    return obj

logger = logging.getLogger(__name__)

class HyperspectralAnalyzer:
    """
    Advanced hyperspectral analysis for agricultural monitoring
    Includes pest detection, crop health, and soil assessment
    """
    
    def __init__(self):
        # Indian agriculture-specific thresholds based on ICAR guidelines
        self.thresholds = {
            'crop_health': {
                'excellent': {'ndvi': 0.7, 'ndwi': 0.4},
                'good': {'ndvi': 0.5, 'ndwi': 0.25},
                'moderate': {'ndvi': 0.3, 'ndwi': 0.15},
                'poor': {'ndvi': 0.2, 'ndwi': 0.1}
            },
            'soil_health': {
                'healthy': {'ndvi': 0.3, 'ndsi': 0.2},
                'moderate': {'ndvi': 0.2, 'ndsi': 0.4},
                'degraded': {'ndvi': 0.15, 'ndsi': 0.6}
            },
            'pest_risk': {
                'high': {'ndvi_drop': 0.15, 'texture_var': 0.08},
                'medium': {'ndvi_drop': 0.10, 'texture_var': 0.05},
                'low': {'ndvi_drop': 0.05, 'texture_var': 0.03}
            }
        }
        
        # Crop-specific adjustments for India
        self.crop_thresholds = {
            'rice': {'healthy_ndvi': 0.8, 'stress_threshold': 0.15},
            'wheat': {'healthy_ndvi': 0.7, 'stress_threshold': 0.12},
            'cotton': {'healthy_ndvi': 0.75, 'stress_threshold': 0.18},
            'sugarcane': {'healthy_ndvi': 0.85, 'stress_threshold': 0.20},
            'maize': {'healthy_ndvi': 0.7, 'stress_threshold': 0.15}
        }
    
    def generate_field_visualization(self, spectral_data: Dict, weather_data: Dict, 
                                   field_coords: Tuple[float, float], 
                                   crop_type: str = 'general', 
                                   real_ndvi: float = None) -> Dict:
        """
        Generate comprehensive field visualization including health zones and pest risk
        
        Args:
            spectral_data: Multi-spectral band data
            weather_data: Environmental conditions
            field_coords: (latitude, longitude)
            crop_type: Type of crop for specific thresholds
            real_ndvi: Real NDVI value from satellite data (overrides calculated NDVI)
            
        Returns:
            Dictionary containing all visualization data and analysis
        """
        try:
            logger.info(f"Generating hyperspectral visualization for {crop_type} crop at {field_coords}")
            
            # Calculate spectral indices (use real NDVI if available)
            indices = self.calculate_spectral_indices(spectral_data, real_ndvi=real_ndvi)
            
            # Generate field grid (simulated satellite pixels)
            field_grid = self.generate_field_grid(spectral_data, grid_size=(20, 20))
            
            # Analyze health zones
            health_zones = self.analyze_health_zones(indices, field_grid, crop_type)
            
            # Assess pest risk
            pest_assessment = self.assess_pest_risk(indices, weather_data, field_coords, crop_type)
            
            # Create visualizations
            visualizations = self.create_visualizations(field_grid, health_zones, pest_assessment)
            
            # Generate recommendations
            recommendations = self.generate_recommendations(health_zones, pest_assessment, crop_type)
            
            result = {
                'success': True,
                'field_coordinates': field_coords,
                'crop_type': crop_type,
                'timestamp': datetime.now().isoformat(),
                'spectral_indices': indices,
                'health_zones': health_zones,
                'pest_assessment': pest_assessment,
                'visualizations': visualizations,
                'recommendations': recommendations,
                'thresholds_used': self.crop_thresholds.get(crop_type, self.crop_thresholds['general'] if 'general' in self.crop_thresholds else {})
            }
            
            # Convert all numpy types and other non-serializable objects
            return convert_for_json(result)
            
        except Exception as e:
            logger.error(f"Error in hyperspectral visualization: {e}")
            return {
                'success': False,
                'error': str(e),
                'field_coordinates': field_coords
            }
    
    def calculate_spectral_indices(self, spectral_data: Dict, real_ndvi: float = None) -> Dict:
        """Calculate key spectral indices from multi-spectral bands
        
        Args:
            spectral_data: Multi-spectral band data
            real_ndvi: Real NDVI value from satellite data (overrides calculated NDVI)
        """
        try:
            # Extract bands
            red = np.array(spectral_data.get('red', []))
            green = np.array(spectral_data.get('green', []))
            nir = np.array(spectral_data.get('nir', []))
            swir = np.array(spectral_data.get('swir', []))
            
            # Ensure we have enough data
            if len(red) == 0 or len(nir) == 0:
                raise ValueError("Insufficient spectral data")
            
            # NDVI = (NIR - Red) / (NIR + Red) - use real NDVI if provided
            if real_ndvi is not None:
                # Use real NDVI value, replicated across the array size
                array_size = len(red) if len(red) > 0 else len(nir) if len(nir) > 0 else 100
                ndvi = np.full(array_size, real_ndvi)
                logger.info(f"Using real NDVI value: {real_ndvi:.3f} for hyperspectral analysis")
            else:
                # Calculate NDVI from bands
                ndvi = np.where((nir + red) != 0, (nir - red) / (nir + red), 0)
            
            # NDWI = (NIR - SWIR) / (NIR + SWIR) 
            ndwi = np.where((nir + swir) != 0, (nir - swir) / (nir + swir), 0)
            
            # MNDWI (Modified NDWI) = (Green - SWIR) / (Green + SWIR)
            mndwi = np.where((green + swir) != 0, (green - swir) / (green + swir), 0)
            
            # NDSI = (SWIR - Green) / (SWIR + Green)
            ndsi = np.where((swir + green) != 0, (swir - green) / (swir + green), 0)
            
            # Red Edge NDVI (approximation using available bands)
            # RE-NDVI ≈ (NIR - Red_edge) / (NIR + Red_edge)
            # Since we don't have red-edge, approximate with weighted NIR-Red
            red_edge_ndvi = np.where((nir * 1.1 + red * 0.9) != 0, 
                                   (nir * 1.1 - red * 0.9) / (nir * 1.1 + red * 0.9), 0)
            
            # Calculate statistics for each index
            def get_stats(values):
                return {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'median': float(np.median(values)),
                    'values': values.tolist()
                }
            
            return {
                'ndvi': get_stats(ndvi),
                'ndwi': get_stats(ndwi),
                'mndwi': get_stats(mndwi),
                'ndsi': get_stats(ndsi),
                'red_edge_ndvi': get_stats(red_edge_ndvi)
            }
            
        except Exception as e:
            logger.error(f"Error calculating spectral indices: {e}")
            return {}
    
    def generate_field_grid(self, spectral_data: Dict, grid_size: Tuple[int, int] = (20, 20)) -> Dict:
        """Generate a spatial grid representation of the field"""
        try:
            rows, cols = grid_size
            
            # Create spatial grids for each spectral index
            def create_spatial_grid(values, noise_factor=0.1):
                # Reshape values to grid and add spatial correlation
                base_grid = np.random.choice(values, size=grid_size)
                
                # Add spatial smoothing to simulate realistic field patterns
                from scipy.ndimage import gaussian_filter
                smoothed = gaussian_filter(base_grid, sigma=1.0)
                
                # Add some random variation to simulate field heterogeneity
                noise = np.random.normal(0, noise_factor * np.std(smoothed), grid_size)
                final_grid = smoothed + noise
                
                return final_grid
            
            # Get spectral data
            red = spectral_data.get('red', [0.1] * 100)
            green = spectral_data.get('green', [0.15] * 100) 
            nir = spectral_data.get('nir', [0.6] * 100)
            swir = spectral_data.get('swir', [0.3] * 100)
            
            # Create grids for each band
            red_grid = create_spatial_grid(red)
            green_grid = create_spatial_grid(green)
            nir_grid = create_spatial_grid(nir)
            swir_grid = create_spatial_grid(swir)
            
            # Calculate index grids
            ndvi_grid = np.where((nir_grid + red_grid) != 0, 
                               (nir_grid - red_grid) / (nir_grid + red_grid), 0)
            
            ndwi_grid = np.where((nir_grid + swir_grid) != 0,
                               (nir_grid - swir_grid) / (nir_grid + swir_grid), 0)
            
            ndsi_grid = np.where((swir_grid + green_grid) != 0,
                               (swir_grid - green_grid) / (swir_grid + green_grid), 0)
            
            return {
                'dimensions': grid_size,
                'bands': {
                    'red': red_grid.tolist(),
                    'green': green_grid.tolist(), 
                    'nir': nir_grid.tolist(),
                    'swir': swir_grid.tolist()
                },
                'indices': {
                    'ndvi': ndvi_grid.tolist(),
                    'ndwi': ndwi_grid.tolist(),
                    'ndsi': ndsi_grid.tolist()
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating field grid: {e}")
            return {'dimensions': grid_size, 'bands': {}, 'indices': {}}
    
    def analyze_health_zones(self, indices: Dict, field_grid: Dict, crop_type: str) -> Dict:
        """Analyze field health zones based on spectral indices"""
        try:
            # Get crop-specific thresholds
            crop_thresh = self.crop_thresholds.get(crop_type, {
                'healthy_ndvi': 0.7,
                'stress_threshold': 0.15
            })
            
            ndvi_values = np.array(indices.get('ndvi', {}).get('values', []))
            ndwi_values = np.array(indices.get('ndwi', {}).get('values', []))
            ndsi_values = np.array(indices.get('ndsi', {}).get('values', []))
            
            # Classify crop health
            def classify_crop_health(ndvi, ndwi):
                if ndvi > crop_thresh['healthy_ndvi'] and ndwi > 0.3:
                    return 'excellent'
                elif ndvi > 0.5 and ndwi > 0.2:
                    return 'good'
                elif ndvi > 0.3 and ndwi > 0.1:
                    return 'moderate'
                else:
                    return 'poor'
            
            # Classify soil health
            def classify_soil_health(ndvi, ndsi):
                if ndsi > 0.4 and ndvi < 0.3:
                    return 'degraded'
                elif 0.2 < ndsi < 0.4 and 0.3 < ndvi < 0.6:
                    return 'moderate'
                else:
                    return 'healthy'
            
            # Create health maps
            crop_health = []
            soil_health = []
            
            for i in range(len(ndvi_values)):
                crop_health.append(classify_crop_health(ndvi_values[i], ndwi_values[i]))
                soil_health.append(classify_soil_health(ndvi_values[i], ndsi_values[i]))
            
            # Calculate zone statistics
            from collections import Counter
            crop_stats = Counter(crop_health)
            soil_stats = Counter(soil_health)
            
            return {
                'crop_health': {
                    'classifications': crop_health,
                    'statistics': dict(crop_stats),
                    'overall_score': self._calculate_health_score(crop_stats),
                    'dominant_zone': crop_stats.most_common(1)[0][0] if crop_stats else 'unknown'
                },
                'soil_health': {
                    'classifications': soil_health,
                    'statistics': dict(soil_stats),
                    'overall_score': self._calculate_soil_score(soil_stats),
                    'dominant_zone': soil_stats.most_common(1)[0][0] if soil_stats else 'unknown'
                },
                'field_uniformity': {
                    'crop_variability': len(crop_stats) / len(crop_health) if crop_health else 0,
                    'soil_variability': len(soil_stats) / len(soil_health) if soil_health else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing health zones: {e}")
            return {}
    
    def assess_pest_risk(self, indices: Dict, weather_data: Dict, 
                        field_coords: Tuple[float, float], crop_type: str) -> Dict:
        """Assess pest and disease risk based on spectral patterns and environmental conditions"""
        try:
            latitude, longitude = field_coords
            
            # Extract environmental conditions
            temperature = weather_data.get('temperature', 25)
            humidity = weather_data.get('humidity', 60)
            pressure = weather_data.get('pressure', 1013)
            
            # Calculate spectral stress indicators
            ndvi_mean = indices.get('ndvi', {}).get('mean', 0.5)
            ndvi_std = indices.get('ndvi', {}).get('std', 0.1)
            ndwi_mean = indices.get('ndwi', {}).get('mean', 0.3)
            
            # Pest risk factors
            risk_factors = {
                'environmental': self._assess_environmental_pest_risk(
                    temperature, humidity, crop_type, latitude
                ),
                'spectral_stress': self._assess_spectral_stress(
                    ndvi_mean, ndvi_std, ndwi_mean
                ),
                'seasonal': self._assess_seasonal_pest_risk(latitude, crop_type)
            }
            
            # Common pests for Indian agriculture
            pest_risks = self._calculate_specific_pest_risks(
                risk_factors, crop_type, temperature, humidity
            )
            
            # Overall risk assessment
            overall_risk = self._calculate_overall_pest_risk(risk_factors)
            
            return {
                'overall_risk': overall_risk,
                'risk_level': self._categorize_risk_level(overall_risk),
                'risk_factors': risk_factors,
                'specific_pests': pest_risks,
                'environmental_conditions': {
                    'temperature': temperature,
                    'humidity': humidity,
                    'favorable_for_pests': humidity > 70 and 20 < temperature < 35
                },
                'recommendations': self._generate_pest_recommendations(overall_risk, pest_risks, crop_type)
            }
            
        except Exception as e:
            logger.error(f"Error assessing pest risk: {e}")
            return {'overall_risk': 0.3, 'risk_level': 'medium', 'error': str(e)}
    
    def _assess_environmental_pest_risk(self, temp: float, humidity: float, 
                                      crop_type: str, latitude: float) -> float:
        """Assess pest risk based on environmental conditions"""
        risk = 0.0
        
        # Temperature-based risk
        if 22 <= temp <= 32:  # Optimal for many pests
            risk += 0.3
        elif temp > 35 or temp < 15:  # Too extreme
            risk += 0.1
        else:
            risk += 0.2
        
        # Humidity-based risk  
        if humidity > 75:  # High humidity favors fungal pests
            risk += 0.4
        elif humidity < 40:  # Dry conditions favor mites
            risk += 0.3
        else:
            risk += 0.2
            
        # Tropical/subtropical regions have higher pest pressure
        if abs(latitude) < 35:
            risk += 0.2
            
        return min(risk, 1.0)
    
    def _assess_spectral_stress(self, ndvi_mean: float, ndvi_std: float, ndwi_mean: float) -> float:
        """Assess stress indicators from spectral data"""
        stress_score = 0.0
        
        # Low NDVI indicates plant stress (susceptible to pests)
        if ndvi_mean < 0.4:
            stress_score += 0.4
        elif ndvi_mean < 0.6:
            stress_score += 0.2
            
        # High variability indicates uneven growth (pest hotspots)
        if ndvi_std > 0.15:
            stress_score += 0.3
        elif ndvi_std > 0.10:
            stress_score += 0.2
            
        # Water stress makes plants vulnerable
        if ndwi_mean < 0.2:
            stress_score += 0.3
        
        return min(stress_score, 1.0)
    
    def _assess_seasonal_pest_risk(self, latitude: float, crop_type: str) -> float:
        """Assess seasonal pest risk patterns"""
        month = datetime.now().month
        
        # Northern hemisphere seasonal patterns
        if latitude > 0:
            if crop_type in ['rice', 'cotton'] and month in [6, 7, 8]:  # Monsoon season
                return 0.8
            elif crop_type == 'wheat' and month in [3, 4, 5]:  # Pre-harvest
                return 0.6
        else:  # Southern hemisphere
            if month in [12, 1, 2]:  # Summer growing season
                return 0.7
                
        return 0.4  # Base seasonal risk
    
    def _calculate_specific_pest_risks(self, risk_factors: Dict, crop_type: str, 
                                     temp: float, humidity: float) -> Dict:
        """Calculate risk for specific pests common in Indian agriculture"""
        base_risk = np.mean(list(risk_factors.values()))
        
        pest_risks = {}
        
        # Common pests by crop type in India
        if crop_type == 'rice':
            pest_risks.update({
                'brown_planthopper': base_risk * 0.9 if humidity > 80 else base_risk * 0.6,
                'rice_blast': base_risk * 0.8 if humidity > 75 and temp > 25 else base_risk * 0.4,
                'stem_borer': base_risk * 0.7,
                'leaf_folder': base_risk * 0.6 if temp > 28 else base_risk * 0.4
            })
        elif crop_type == 'cotton':
            pest_risks.update({
                'bollworm': base_risk * 0.8 if 25 < temp < 35 else base_risk * 0.5,
                'aphids': base_risk * 0.7 if humidity < 60 else base_risk * 0.4,
                'whitefly': base_risk * 0.9 if temp > 30 else base_risk * 0.6,
                'thrips': base_risk * 0.6
            })
        elif crop_type == 'wheat':
            pest_risks.update({
                'rust': base_risk * 0.8 if humidity > 70 else base_risk * 0.3,
                'aphids': base_risk * 0.7,
                'termites': base_risk * 0.5 if humidity < 50 else base_risk * 0.3,
                'army_worm': base_risk * 0.6 if temp > 25 else base_risk * 0.4
            })
        else:  # General crops
            pest_risks.update({
                'aphids': base_risk * 0.6,
                'spider_mites': base_risk * 0.5 if humidity < 50 else base_risk * 0.3,
                'thrips': base_risk * 0.5,
                'fungal_diseases': base_risk * 0.7 if humidity > 75 else base_risk * 0.4
            })
        
        return pest_risks
    
    def _calculate_overall_pest_risk(self, risk_factors: Dict) -> float:
        """Calculate weighted overall pest risk"""
        weights = {
            'environmental': 0.4,
            'spectral_stress': 0.35,
            'seasonal': 0.25
        }
        
        weighted_risk = sum(risk_factors.get(factor, 0) * weight 
                          for factor, weight in weights.items())
        
        return min(weighted_risk, 1.0)
    
    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize risk level based on score"""
        if risk_score >= 0.7:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_health_score(self, crop_stats: Dict) -> float:
        """Calculate overall crop health score"""
        weights = {'excellent': 1.0, 'good': 0.75, 'moderate': 0.5, 'poor': 0.25}
        total_pixels = sum(crop_stats.values())
        
        if total_pixels == 0:
            return 0.5
            
        weighted_sum = sum(crop_stats.get(status, 0) * weight 
                          for status, weight in weights.items())
        
        return weighted_sum / total_pixels
    
    def _calculate_soil_score(self, soil_stats: Dict) -> float:
        """Calculate overall soil health score"""
        weights = {'healthy': 1.0, 'moderate': 0.6, 'degraded': 0.2}
        total_pixels = sum(soil_stats.values())
        
        if total_pixels == 0:
            return 0.5
            
        weighted_sum = sum(soil_stats.get(status, 0) * weight 
                          for status, weight in weights.items())
        
        return weighted_sum / total_pixels
    
    def create_visualizations(self, field_grid: Dict, health_zones: Dict, pest_assessment: Dict) -> Dict:
        """Create visualization images for the field analysis"""
        try:
            visualizations = {}
            
            # Create NDVI heatmap
            visualizations['ndvi_map'] = self._create_ndvi_heatmap(field_grid)
            
            # Create health zones map
            visualizations['health_zones'] = self._create_health_zones_map(field_grid, health_zones)
            
            # Create pest risk map
            visualizations['pest_risk'] = self._create_pest_risk_visualization(pest_assessment)
            
            # Create combined dashboard
            visualizations['dashboard'] = self._create_combined_dashboard(field_grid, health_zones, pest_assessment)
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
            return {}
    
    def _create_ndvi_heatmap(self, field_grid: Dict) -> str:
        """Create NDVI heatmap visualization"""
        try:
            ndvi_grid = np.array(field_grid.get('indices', {}).get('ndvi', []))
            
            plt.figure(figsize=(10, 8))
            plt.imshow(ndvi_grid, cmap='RdYlGn', vmin=0, vmax=1)
            plt.colorbar(label='NDVI Value')
            plt.title('NDVI (Normalized Difference Vegetation Index)\nGreen = Healthy Vegetation, Red = Stressed/Bare')
            plt.xlabel('Field Width (relative)')
            plt.ylabel('Field Length (relative)')
            
            # Convert to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Error creating NDVI heatmap: {e}")
            return ""
    
    def _create_health_zones_map(self, field_grid: Dict, health_zones: Dict) -> str:
        """Create field health zones visualization"""
        try:
            # Create a simple visualization representation
            # In a real implementation, you'd create actual image maps
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            
        except Exception as e:
            logger.error(f"Error creating health zones map: {e}")
            return ""
    
    def _create_pest_risk_visualization(self, pest_assessment: Dict) -> Dict:
        """Create pest risk visualization data"""
        try:
            return {
                'risk_level': pest_assessment.get('risk_level', 'medium'),
                'overall_risk': pest_assessment.get('overall_risk', 0.5),
                'specific_risks': pest_assessment.get('specific_pests', {}),
                'risk_factors': pest_assessment.get('risk_factors', {})
            }
            
        except Exception as e:
            logger.error(f"Error creating pest risk visualization: {e}")
            return {}
    
    def _create_combined_dashboard(self, field_grid: Dict, health_zones: Dict, pest_assessment: Dict) -> Dict:
        """Create combined dashboard data"""
        try:
            return {
                'field_overview': {
                    'total_area': '1 hectare (simulated)',
                    'analysis_resolution': f"{field_grid.get('dimensions', [20, 20])[0]}x{field_grid.get('dimensions', [20, 20])[1]} pixels",
                    'analysis_date': datetime.now().isoformat()
                },
                'summary_stats': {
                    'crop_health_score': health_zones.get('crop_health', {}).get('overall_score', 0.5),
                    'soil_health_score': health_zones.get('soil_health', {}).get('overall_score', 0.5),
                    'pest_risk_level': pest_assessment.get('risk_level', 'medium')
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating combined dashboard: {e}")
            return {}
    
    def generate_recommendations(self, health_zones: Dict, pest_assessment: Dict, crop_type: str) -> List[Dict]:
        """Generate actionable recommendations based on analysis"""
        try:
            recommendations = []
            
            # Crop health recommendations
            crop_score = health_zones.get('crop_health', {}).get('overall_score', 0.5)
            if crop_score < 0.4:
                recommendations.append({
                    'type': 'crop_health',
                    'priority': 'high',
                    'title': 'Crop Health Critical',
                    'description': 'Crop health is below optimal levels. Consider soil testing and nutrient management.',
                    'actions': ['Soil nutrient analysis', 'Fertilizer application', 'Irrigation assessment']
                })
            elif crop_score < 0.6:
                recommendations.append({
                    'type': 'crop_health', 
                    'priority': 'medium',
                    'title': 'Improve Crop Health',
                    'description': 'Moderate crop stress detected. Monitor and optimize growing conditions.',
                    'actions': ['Monitor water stress', 'Adjust fertilization', 'Check for early pest signs']
                })
            
            # Pest risk recommendations
            risk_level = pest_assessment.get('risk_level', 'medium')
            if risk_level == 'high':
                recommendations.append({
                    'type': 'pest_control',
                    'priority': 'high',
                    'title': 'High Pest Risk Detected',
                    'description': 'Environmental conditions favor pest development. Implement preventive measures.',
                    'actions': ['Scout fields regularly', 'Consider preventive treatments', 'Monitor weather conditions']
                })
            
            # Specific pest recommendations
            specific_pests = pest_assessment.get('specific_pests', {})
            high_risk_pests = [pest for pest, risk in specific_pests.items() if risk > 0.7]
            
            if high_risk_pests:
                recommendations.append({
                    'type': 'specific_pests',
                    'priority': 'high',
                    'title': f'High Risk: {", ".join(high_risk_pests[:3])}',
                    'description': f'Specific pest risks identified for {crop_type}.',
                    'actions': [f'Monitor for {pest}' for pest in high_risk_pests[:3]]
                })
            
            # Soil health recommendations
            soil_score = health_zones.get('soil_health', {}).get('overall_score', 0.5)
            if soil_score < 0.4:
                recommendations.append({
                    'type': 'soil_health',
                    'priority': 'medium',
                    'title': 'Soil Health Improvement Needed',
                    'description': 'Soil conditions show signs of degradation or poor coverage.',
                    'actions': ['Soil organic matter enhancement', 'Cover crop consideration', 'Erosion control measures']
                })
            
            return recommendations[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    def _generate_pest_recommendations(self, overall_risk: float, pest_risks: Dict, crop_type: str) -> List[str]:
        """Generate specific pest management recommendations"""
        recommendations = []
        
        if overall_risk > 0.7:
            recommendations.extend([
                "Implement intensive field monitoring (2-3 times per week)",
                "Consider preventive pest control measures",
                "Monitor weather conditions for pest-favorable periods"
            ])
        elif overall_risk > 0.4:
            recommendations.extend([
                "Regular field scouting (weekly)",
                "Maintain field hygiene and remove crop residues",
                "Monitor threshold levels for economic pests"
            ])
        
        # Add crop-specific recommendations
        if crop_type == 'rice' and pest_risks.get('brown_planthopper', 0) > 0.6:
            recommendations.append("Monitor for brown planthopper, especially in humid conditions")
        
        if crop_type == 'cotton' and pest_risks.get('bollworm', 0) > 0.6:
            recommendations.append("Check for bollworm eggs and larvae on cotton bolls")
            
        return recommendations
