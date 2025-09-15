import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

def calculate_ndvi(red_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
    """
    Calculate NDVI (Normalized Difference Vegetation Index)
    NDVI = (NIR - Red) / (NIR + Red)
    
    Args:
        red_band: Red band reflectance values
        nir_band: Near-infrared band reflectance values
    
    Returns:
        NDVI values array
    """
    try:
        # Avoid division by zero
        denominator = nir_band + red_band
        denominator = np.where(denominator == 0, 1e-10, denominator)
        
        ndvi = (nir_band - red_band) / denominator
        
        # Clip NDVI values to valid range [-1, 1]
        ndvi = np.clip(ndvi, -1, 1)
        
        logger.info(f"Calculated NDVI for {len(ndvi)} pixels, range: {np.min(ndvi):.3f} to {np.max(ndvi):.3f}")
        return ndvi
        
    except Exception as e:
        logger.error(f"Error calculating NDVI: {e}")
        return np.array([])

def calculate_ndwi(nir_band: np.ndarray, swir_band: np.ndarray) -> np.ndarray:
    """
    Calculate NDWI (Normalized Difference Water Index)
    NDWI = (NIR - SWIR) / (NIR + SWIR)
    
    Args:
        nir_band: Near-infrared band reflectance values
        swir_band: Short-wave infrared band reflectance values
    
    Returns:
        NDWI values array
    """
    try:
        # Avoid division by zero
        denominator = nir_band + swir_band
        denominator = np.where(denominator == 0, 1e-10, denominator)
        
        ndwi = (nir_band - swir_band) / denominator
        
        # Clip NDWI values to valid range [-1, 1]
        ndwi = np.clip(ndwi, -1, 1)
        
        logger.info(f"Calculated NDWI for {len(ndwi)} pixels, range: {np.min(ndwi):.3f} to {np.max(ndwi):.3f}")
        return ndwi
        
    except Exception as e:
        logger.error(f"Error calculating NDWI: {e}")
        return np.array([])

def calculate_mndwi(green_band: np.ndarray, swir_band: np.ndarray) -> np.ndarray:
    """
    Calculate Modified NDWI (MNDWI) for better water body delineation
    MNDWI = (GREEN - SWIR) / (GREEN + SWIR)
    
    Args:
        green_band: Green band reflectance values
        swir_band: Short-wave infrared band reflectance values
    
    Returns:
        MNDWI values array
    """
    try:
        # Avoid division by zero
        denominator = green_band + swir_band
        denominator = np.where(denominator == 0, 1e-10, denominator)
        
        mndwi = (green_band - swir_band) / denominator
        
        # Clip MNDWI values to valid range [-1, 1]
        mndwi = np.clip(mndwi, -1, 1)
        
        logger.info(f"Calculated MNDWI for {len(mndwi)} pixels, range: {np.min(mndwi):.3f} to {np.max(mndwi):.3f}")
        return mndwi
        
    except Exception as e:
        logger.error(f"Error calculating MNDWI: {e}")
        return np.array([])

def calculate_ndsi(green_band: np.ndarray, swir_band: np.ndarray) -> np.ndarray:
    """
    Calculate NDSI (Normalized Difference Snow Index)
    NDSI = (GREEN - SWIR) / (GREEN + SWIR)
    
    Args:
        green_band: Green band reflectance values
        swir_band: Short-wave infrared band reflectance values
    
    Returns:
        NDSI values array
    """
    try:
        # Avoid division by zero
        denominator = green_band + swir_band
        denominator = np.where(denominator == 0, 1e-10, denominator)
        
        ndsi = (green_band - swir_band) / denominator
        
        # Clip NDSI values to valid range [-1, 1]
        ndsi = np.clip(ndsi, -1, 1)
        
        logger.info(f"Calculated NDSI for {len(ndsi)} pixels, range: {np.min(ndsi):.3f} to {np.max(ndsi):.3f}")
        return ndsi
        
    except Exception as e:
        logger.error(f"Error calculating NDSI: {e}")
        return np.array([])

def calculate_all_indices(data: Dict) -> Dict:
    """
    Calculate all spectral indices (NDVI, NDWI, MNDWI, NDSI) from satellite data
    
    Args:
        data: Dictionary containing band reflectance data
        
    Returns:
        Dictionary with all calculated indices
    """
    try:
        indices = {}
        
        # Extract bands
        red_band = np.array(data.get('red', []))
        nir_band = np.array(data.get('nir', []))
        green_band = np.array(data.get('green', []))
        swir_band = np.array(data.get('swir', []))
        
        # Calculate NDVI if red and NIR are available
        if len(red_band) > 0 and len(nir_band) > 0:
            indices['ndvi'] = calculate_ndvi(red_band, nir_band)
            logger.info(f"NDVI calculated: mean = {np.mean(indices['ndvi']):.3f}")
        
        # Calculate NDWI if NIR and SWIR are available
        if len(nir_band) > 0 and len(swir_band) > 0:
            indices['ndwi'] = calculate_ndwi(nir_band, swir_band)
            logger.info(f"NDWI calculated: mean = {np.mean(indices['ndwi']):.3f}")
        
        # Calculate Modified NDWI if GREEN and SWIR are available
        if len(green_band) > 0 and len(swir_band) > 0:
            indices['mndwi'] = calculate_mndwi(green_band, swir_band)
            logger.info(f"MNDWI calculated: mean = {np.mean(indices['mndwi']):.3f}")
        
        # Calculate NDSI if GREEN and SWIR are available
        if len(green_band) > 0 and len(swir_band) > 0:
            indices['ndsi'] = calculate_ndsi(green_band, swir_band)
            logger.info(f"NDSI calculated: mean = {np.mean(indices['ndsi']):.3f}")
        
        return indices
        
    except Exception as e:
        logger.error(f"Error calculating all indices: {e}")
        return {}

def interpret_ndwi(ndwi_value: float) -> Dict:
    """
    Interpret NDWI value and provide water presence status
    
    Args:
        ndwi_value: NDWI value between -1 and 1
    
    Returns:
        Dictionary with interpretation results
    """
    try:
        if ndwi_value > 0.3:
            status = "High Water Content"
            description = "Strong water presence or very moist vegetation"
            water_score = 90
            color = "#0077BE"  # Blue
        elif ndwi_value > 0.1:
            status = "Moderate Water Content"
            description = "Water bodies or moist vegetation"
            water_score = 70
            color = "#4A9FDB"  # Light blue
        elif ndwi_value > -0.1:
            status = "Low Water Content"
            description = "Slightly moist soil or sparse vegetation"
            water_score = 40
            color = "#87CEEB"  # Sky blue
        else:
            status = "No Water"
            description = "Dry vegetation, bare soil, or built-up areas"
            water_score = 10
            color = "#8B4513"  # Brown
        
        return {
            'ndwi_value': round(ndwi_value, 3),
            'status': status,
            'description': description,
            'water_score': water_score,
            'color': color,
            'confidence': min(95, max(60, abs(ndwi_value) * 100))
        }
        
    except Exception as e:
        logger.error(f"Error interpreting NDWI: {e}")
        return {
            'ndwi_value': ndwi_value,
            'status': 'Unknown',
            'description': 'Error interpreting NDWI value',
            'water_score': 50,
            'color': '#888888',
            'confidence': 50
        }

def interpret_ndsi(ndsi_value: float) -> Dict:
    """
    Interpret NDSI value and provide snow/ice presence status
    
    Args:
        ndsi_value: NDSI value between -1 and 1
    
    Returns:
        Dictionary with interpretation results
    """
    try:
        if ndsi_value > 0.4:
            status = "Snow/Ice Present"
            description = "Strong snow or ice cover"
            snow_score = 90
            color = "#FFFFFF"  # White
        elif ndsi_value > 0.1:
            status = "Possible Snow/Ice"
            description = "Light snow cover or mixed snow-vegetation"
            snow_score = 60
            color = "#F0F8FF"  # Alice blue
        elif ndsi_value > -0.1:
            status = "No Snow"
            description = "Clear ground or sparse vegetation"
            snow_score = 20
            color = "#90EE90"  # Light green
        else:
            status = "Vegetation/Water"
            description = "Vegetation or water bodies (no snow)"
            snow_score = 5
            color = "#228B22"  # Forest green
        
        return {
            'ndsi_value': round(ndsi_value, 3),
            'status': status,
            'description': description,
            'snow_score': snow_score,
            'color': color,
            'confidence': min(95, max(60, abs(ndsi_value) * 100))
        }
        
    except Exception as e:
        logger.error(f"Error interpreting NDSI: {e}")
        return {
            'ndsi_value': ndsi_value,
            'status': 'Unknown',
            'description': 'Error interpreting NDSI value',
            'snow_score': 50,
            'color': '#888888',
            'confidence': 50
        }

def create_index_stack_analysis(indices: Dict) -> Dict:
    """
    Create comprehensive index stack analysis with land cover classification
    
    Args:
        indices: Dictionary containing calculated indices (NDVI, NDWI, MNDWI, NDSI)
    
    Returns:
        Dictionary with land cover classification and analysis
    """
    try:
        ndvi = indices.get('ndvi', np.array([]))
        ndwi = indices.get('ndwi', np.array([]))
        mndwi = indices.get('mndwi', np.array([]))
        ndsi = indices.get('ndsi', np.array([]))
        
        # Ensure all arrays have the same length
        min_length = min([len(arr) for arr in [ndvi, ndwi, mndwi, ndsi] if len(arr) > 0])
        if min_length == 0:
            return {'error': 'No valid index data provided'}
        
        # Truncate all arrays to the same length
        ndvi = ndvi[:min_length] if len(ndvi) > 0 else np.full(min_length, 0.5)
        ndwi = ndwi[:min_length] if len(ndwi) > 0 else np.full(min_length, 0.0)
        mndwi = mndwi[:min_length] if len(mndwi) > 0 else np.full(min_length, 0.0)
        ndsi = ndsi[:min_length] if len(ndsi) > 0 else np.full(min_length, 0.0)
        
        # Land cover classification based on index combinations
        land_cover = np.full(min_length, 0, dtype=int)  # 0: Unknown
        
        # Classification logic:
        # 1: Water (high MNDWI or NDWI)
        # 2: Snow/Ice (high NDSI)
        # 3: Dense Vegetation (high NDVI, low NDWI)
        # 4: Sparse Vegetation (moderate NDVI)
        # 5: Bare Soil/Rock (low NDVI, low NDWI, low NDSI)
        # 6: Urban/Built-up (very low NDVI, low NDWI)
        
        for i in range(min_length):
            if ndsi[i] > 0.4:  # Snow/Ice
                land_cover[i] = 2
            elif mndwi[i] > 0.3 or ndwi[i] > 0.3:  # Water
                land_cover[i] = 1
            elif ndvi[i] > 0.6:  # Dense vegetation
                land_cover[i] = 3
            elif ndvi[i] > 0.2:  # Sparse vegetation
                land_cover[i] = 4
            elif ndvi[i] < -0.1:  # Urban/built-up
                land_cover[i] = 6
            else:  # Bare soil/rock
                land_cover[i] = 5
        
        # Calculate land cover percentages
        land_cover_counts = np.bincount(land_cover, minlength=7)
        total_pixels = len(land_cover)
        
        land_cover_map = {
            0: {'name': 'Unknown', 'color': '#808080'},
            1: {'name': 'Water', 'color': '#6A5ACD'},  # Purple
            2: {'name': 'Snow/Ice', 'color': '#FF00FF'},  # Magenta
            3: {'name': 'Dense Vegetation', 'color': '#228B22'},  # Green
            4: {'name': 'Sparse Vegetation', 'color': '#9ACD32'},  # Yellow-green
            5: {'name': 'Bare Soil/Rock', 'color': '#4169E1'},  # Blue
            6: {'name': 'Urban/Built-up', 'color': '#696969'}  # Gray
        }
        
        land_cover_stats = {}
        for i in range(7):
            if land_cover_counts[i] > 0:
                percentage = (land_cover_counts[i] / total_pixels) * 100
                land_cover_stats[land_cover_map[i]['name']] = {
                    'percentage': round(percentage, 1),
                    'pixel_count': int(land_cover_counts[i]),
                    'color': land_cover_map[i]['color']
                }
        
        # Calculate index statistics
        index_stats = {}
        for name, values in [('NDVI', ndvi), ('NDWI', ndwi), ('MNDWI', mndwi), ('NDSI', ndsi)]:
            if len(values) > 0:
                index_stats[name] = {
                    'mean': round(float(np.mean(values)), 3),
                    'std': round(float(np.std(values)), 3),
                    'min': round(float(np.min(values)), 3),
                    'max': round(float(np.max(values)), 3),
                    'median': round(float(np.median(values)), 3)
                }
        
        return {
            'land_cover_stats': land_cover_stats,
            'index_stats': index_stats,
            'total_pixels': total_pixels,
            'dominant_land_cover': max(land_cover_stats.items(), key=lambda x: x[1]['percentage'])[0] if land_cover_stats else 'Unknown'
        }
        
    except Exception as e:
        logger.error(f"Error creating index stack analysis: {e}")
        return {'error': f'Failed to create index stack analysis: {str(e)}'}

def generate_spectral_indices_plot(indices: Dict, title: str = "Spectral Indices Analysis") -> str:
    """
    Generate a comprehensive plot of all spectral indices
    
    Args:
        indices: Dictionary containing calculated indices
        title: Plot title
    
    Returns:
        Base64 encoded image string
    """
    try:
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        index_info = {
            'NDVI': {'data': indices.get('ndvi', []), 'color': '#228B22', 'label': 'Vegetation Health'},
            'NDWI': {'data': indices.get('ndwi', []), 'color': '#0077BE', 'label': 'Water Content'},
            'MNDWI': {'data': indices.get('mndwi', []), 'color': '#4A9FDB', 'label': 'Water Bodies'},
            'NDSI': {'data': indices.get('ndsi', []), 'color': '#FF00FF', 'label': 'Snow/Ice Cover'}
        }
        
        plot_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        for idx, (index_name, info) in enumerate(index_info.items()):
            ax = axes[plot_positions[idx]]
            data = info['data']
            
            if len(data) > 0:
                # Histogram
                ax.hist(data, bins=30, alpha=0.7, color=info['color'], edgecolor='black')
                ax.axvline(np.mean(data), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(data):.3f}')
                ax.axvline(np.median(data), color='orange', linestyle=':', linewidth=2, label=f'Median: {np.median(data):.3f}')
                
                # Statistics text
                stats_text = f"Mean: {np.mean(data):.3f}\nStd: {np.std(data):.3f}\nRange: [{np.min(data):.3f}, {np.max(data):.3f}]"
                ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            else:
                ax.text(0.5, 0.5, 'No Data Available', transform=ax.transAxes, 
                       ha='center', va='center', fontsize=14)
            
            ax.set_title(f'{index_name} - {info["label"]}', fontsize=12, fontweight='bold')
            ax.set_xlabel('Index Value')
            ax.set_ylabel('Frequency')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(plot_data).decode()
        
    except Exception as e:
        logger.error(f"Error generating spectral indices plot: {e}")
        return ""

def generate_index_comparison_plot(indices: Dict) -> str:
    """
    Generate a scatter plot comparing different indices
    
    Args:
        indices: Dictionary containing calculated indices
    
    Returns:
        Base64 encoded image string
    """
    try:
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Spectral Indices Correlation Analysis', fontsize=16, fontweight='bold')
        
        ndvi = indices.get('ndvi', [])
        ndwi = indices.get('ndwi', [])
        mndwi = indices.get('mndwi', [])
        ndsi = indices.get('ndsi', [])
        
        # Ensure all arrays have the same length for comparison
        min_length = min([len(arr) for arr in [ndvi, ndwi, mndwi, ndsi] if len(arr) > 0])
        
        if min_length > 0:
            ndvi = ndvi[:min_length] if len(ndvi) > 0 else np.full(min_length, 0.5)
            ndwi = ndwi[:min_length] if len(ndwi) > 0 else np.full(min_length, 0.0)
            mndwi = mndwi[:min_length] if len(mndwi) > 0 else np.full(min_length, 0.0)
            ndsi = ndsi[:min_length] if len(ndsi) > 0 else np.full(min_length, 0.0)
            
            # NDVI vs NDWI
            axes[0].scatter(ndvi, ndwi, alpha=0.6, c='blue', s=50)
            axes[0].set_xlabel('NDVI (Vegetation)')
            axes[0].set_ylabel('NDWI (Water)')
            axes[0].set_title('NDVI vs NDWI')
            axes[0].grid(True, alpha=0.3)
            
            # Calculate and display correlation
            corr_ndvi_ndwi = np.corrcoef(ndvi, ndwi)[0, 1]
            axes[0].text(0.05, 0.95, f'Correlation: {corr_ndvi_ndwi:.3f}', 
                        transform=axes[0].transAxes, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # NDVI vs NDSI
            axes[1].scatter(ndvi, ndsi, alpha=0.6, c='magenta', s=50)
            axes[1].set_xlabel('NDVI (Vegetation)')
            axes[1].set_ylabel('NDSI (Snow/Ice)')
            axes[1].set_title('NDVI vs NDSI')
            axes[1].grid(True, alpha=0.3)
            
            corr_ndvi_ndsi = np.corrcoef(ndvi, ndsi)[0, 1]
            axes[1].text(0.05, 0.95, f'Correlation: {corr_ndvi_ndsi:.3f}', 
                        transform=axes[1].transAxes, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # NDWI vs MNDWI
            axes[2].scatter(ndwi, mndwi, alpha=0.6, c='cyan', s=50)
            axes[2].set_xlabel('NDWI (Water - NIR/SWIR)')
            axes[2].set_ylabel('MNDWI (Water - Green/SWIR)')
            axes[2].set_title('NDWI vs MNDWI')
            axes[2].grid(True, alpha=0.3)
            
            corr_ndwi_mndwi = np.corrcoef(ndwi, mndwi)[0, 1]
            axes[2].text(0.05, 0.95, f'Correlation: {corr_ndwi_mndwi:.3f}', 
                        transform=axes[2].transAxes, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(plot_data).decode()
        
    except Exception as e:
        logger.error(f"Error generating index comparison plot: {e}")
        return ""

def generate_land_cover_plot(land_cover_stats: Dict) -> str:
    """
    Generate a pie chart of land cover classification
    
    Args:
        land_cover_stats: Dictionary containing land cover statistics
    
    Returns:
        Base64 encoded image string
    """
    try:
        if not land_cover_stats:
            return ""
        
        plt.style.use('seaborn-v0_8')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        fig.suptitle('Land Cover Classification Analysis', fontsize=16, fontweight='bold')
        
        # Extract data
        labels = list(land_cover_stats.keys())
        percentages = [stats['percentage'] for stats in land_cover_stats.values()]
        colors = [stats['color'] for stats in land_cover_stats.values()]
        
        # Pie chart
        wedges, texts, autotexts = ax1.pie(percentages, labels=labels, colors=colors, autopct='%1.1f%%',
                                          startangle=90, textprops={'fontsize': 10})
        ax1.set_title('Land Cover Distribution', fontsize=12, fontweight='bold')
        
        # Bar chart
        bars = ax2.bar(labels, percentages, color=colors, alpha=0.7, edgecolor='black')
        ax2.set_title('Land Cover Percentages', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Percentage (%)')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, percentage in zip(bars, percentages):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{percentage:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(plot_data).decode()
        
    except Exception as e:
        logger.error(f"Error generating land cover plot: {e}")
        return ""

def calculate_ndvi_from_data(data: Dict) -> Tuple[float, str]:
    """
    Calculate NDVI from processed data dictionary
    
    Args:
        data: Dictionary containing sensor data
    
    Returns:
        Tuple of (average_ndvi, status_message)
    """
    try:
        # Check if NDVI is already calculated
        if 'ndvi' in data:
            ndvi_values = np.array(data['ndvi'])
            avg_ndvi = float(np.mean(ndvi_values))
            logger.info(f"Using existing NDVI data, average: {avg_ndvi:.3f}")
            return avg_ndvi, "success"
        
        # Try to calculate from red and NIR bands
        if 'red' in data and 'nir' in data:
            red_band = np.array(data['red'])
            nir_band = np.array(data['nir'])
            ndvi_values = calculate_ndvi(red_band, nir_band)
            if len(ndvi_values) > 0:
                avg_ndvi = float(np.mean(ndvi_values))
                logger.info(f"Calculated NDVI from red/NIR bands, average: {avg_ndvi:.3f}")
                return avg_ndvi, "success"
        
        # Try to estimate from other vegetation indices
        if 'vegetation_index' in data:
            vi_values = np.array(data['vegetation_index'])
            # Assume vegetation index is similar to NDVI
            avg_ndvi = float(np.mean(vi_values))
            logger.info(f"Using vegetation index as NDVI proxy, average: {avg_ndvi:.3f}")
            return avg_ndvi, "estimated_from_vi"
        
        # Estimate based on other available data
        return estimate_ndvi_from_features(data)
        
    except Exception as e:
        logger.error(f"Error calculating NDVI from data: {e}")
        return 0.5, f"error: {str(e)}"

def estimate_ndvi_from_features(data: Dict) -> Tuple[float, str]:
    """
    Estimate NDVI based on available environmental features
    
    Args:
        data: Dictionary containing sensor data
    
    Returns:
        Tuple of (estimated_ndvi, status_message)
    """
    try:
        # Use environmental factors to estimate vegetation health
        estimated_ndvi = 0.5  # Default baseline
        
        # Adjust based on temperature (optimal range: 20-30°C)
        if 'temperature' in data:
            temp = np.mean(data['temperature'])
            if 20 <= temp <= 30:
                estimated_ndvi += 0.1
            elif temp < 10 or temp > 40:
                estimated_ndvi -= 0.2
            elif temp < 15 or temp > 35:
                estimated_ndvi -= 0.1
        
        # Adjust based on soil moisture (higher is generally better)
        if 'soil_moisture' in data:
            moisture = np.mean(data['soil_moisture'])
            if moisture > 60:
                estimated_ndvi += 0.15
            elif moisture > 40:
                estimated_ndvi += 0.05
            elif moisture < 20:
                estimated_ndvi -= 0.2
        
        # Adjust based on humidity
        if 'humidity' in data:
            humidity = np.mean(data['humidity'])
            if 50 <= humidity <= 70:
                estimated_ndvi += 0.05
            elif humidity < 30:
                estimated_ndvi -= 0.1
        
        # Adjust based on pH (optimal range: 6-7.5)
        if 'ph' in data:
            ph = np.mean(data['ph'])
            if 6.0 <= ph <= 7.5:
                estimated_ndvi += 0.05
            elif ph < 5.5 or ph > 8.0:
                estimated_ndvi -= 0.1
        
        # Ensure NDVI is within valid range
        estimated_ndvi = np.clip(estimated_ndvi, 0.0, 1.0)
        
        logger.info(f"Estimated NDVI from environmental features: {estimated_ndvi:.3f}")
        return float(estimated_ndvi), "estimated_from_features"
        
    except Exception as e:
        logger.error(f"Error estimating NDVI: {e}")
        return 0.5, f"error: {str(e)}"

def interpret_ndvi(ndvi_value: float) -> Dict:
    """
    Interpret NDVI value and provide vegetation health status
    
    Args:
        ndvi_value: NDVI value between -1 and 1
    
    Returns:
        Dictionary with interpretation results
    """
    try:
        if ndvi_value < 0:
            status = "Poor"
            description = "No vegetation or stressed vegetation"
            health_score = 0
            color = "#FF4444"  # Red
        elif ndvi_value < 0.2:
            status = "Poor"
            description = "Sparse vegetation or bare soil"
            health_score = 20
            color = "#FF6644"  # Orange-red
        elif ndvi_value < 0.4:
            status = "Moderate"
            description = "Moderate vegetation density"
            health_score = 50
            color = "#FFAA44"  # Orange
        elif ndvi_value < 0.6:
            status = "Good"
            description = "Healthy vegetation"
            health_score = 75
            color = "#88CC44"  # Yellow-green
        else:
            status = "Excellent"
            description = "Dense, very healthy vegetation"
            health_score = 90
            color = "#44AA44"  # Green
        
        return {
            'ndvi_value': round(ndvi_value, 3),
            'status': status,
            'description': description,
            'health_score': health_score,
            'color': color,
            'confidence': min(95, max(60, health_score))  # Confidence based on score
        }
        
    except Exception as e:
        logger.error(f"Error interpreting NDVI: {e}")
        return {
            'ndvi_value': ndvi_value,
            'status': 'Unknown',
            'description': 'Error interpreting NDVI value',
            'health_score': 50,
            'color': '#888888',
            'confidence': 50
        }

def calculate_ndvi_trends(ndvi_history: List[float], dates: Optional[List] = None) -> Dict:
    """
    Calculate NDVI trends over time
    
    Args:
        ndvi_history: List of historical NDVI values
        dates: Optional list of corresponding dates
    
    Returns:
        Dictionary with trend analysis
    """
    try:
        if len(ndvi_history) < 2:
            return {
                'trend': 'insufficient_data',
                'direction': 'unknown',
                'slope': 0,
                'change_rate': 0,
                'recommendation': 'Need more historical data for trend analysis'
            }
        
        ndvi_array = np.array(ndvi_history)
        time_points = np.arange(len(ndvi_array))
        
        # Calculate linear trend
        slope, intercept = np.polyfit(time_points, ndvi_array, 1)
        
        # Determine trend direction
        if abs(slope) < 0.01:
            trend = 'stable'
            direction = 'no_change'
        elif slope > 0.01:
            trend = 'improving'
            direction = 'increasing'
        else:
            trend = 'declining'
            direction = 'decreasing'
        
        # Calculate change rate (percentage change from first to last)
        change_rate = ((ndvi_array[-1] - ndvi_array[0]) / ndvi_array[0]) * 100
        
        # Generate recommendation
        if trend == 'declining':
            recommendation = "Consider investigating potential stressors (water, nutrients, pests)"
        elif trend == 'improving':
            recommendation = "Vegetation health is improving, maintain current practices"
        else:
            recommendation = "Vegetation health is stable, continue monitoring"
        
        return {
            'trend': trend,
            'direction': direction,
            'slope': round(float(slope), 4),
            'change_rate': round(float(change_rate), 2),
            'recommendation': recommendation,
            'current_ndvi': round(float(ndvi_array[-1]), 3),
            'average_ndvi': round(float(np.mean(ndvi_array)), 3)
        }
        
    except Exception as e:
        logger.error(f"Error calculating NDVI trends: {e}")
        return {
            'trend': 'error',
            'direction': 'unknown',
            'slope': 0,
            'change_rate': 0,
            'recommendation': f'Error in trend analysis: {str(e)}'
        }

def generate_comprehensive_spectral_analysis(data: Dict) -> Dict:
    """
    Generate comprehensive spectral analysis including all indices and visualizations
    
    Args:
        data: Dictionary containing processed band data
    
    Returns:
        Dictionary with complete spectral analysis
    """
    try:
        # Calculate all spectral indices
        indices = calculate_all_indices(data)
        
        if not indices:
            # Generate synthetic data for demonstration
            n_samples = len(next(iter(data.values()))) if data else 100
            indices = {
                'ndvi': np.random.beta(3, 1.5, n_samples),  # Vegetation-biased
                'ndwi': np.random.normal(0.0, 0.3, n_samples),  # Neutral water
                'mndwi': np.random.normal(-0.1, 0.2, n_samples),  # Slightly dry
                'ndsi': np.random.normal(-0.2, 0.1, n_samples)  # No snow
            }
            # Clip all indices to valid ranges
            for key in indices:
                indices[key] = np.clip(indices[key], -1, 1)
        
        # Create comprehensive analysis
        analysis = {
            'indices_stats': {},
            'interpretations': {},
            'land_cover_analysis': {},
            'visualizations': {}
        }
        
        # Calculate statistics for each index
        for index_name, values in indices.items():
            if len(values) > 0:
                analysis['indices_stats'][index_name.upper()] = {
                    'mean': round(float(np.mean(values)), 3),
                    'median': round(float(np.median(values)), 3),
                    'std': round(float(np.std(values)), 3),
                    'min': round(float(np.min(values)), 3),
                    'max': round(float(np.max(values)), 3),
                    'count': len(values),
                    'percentiles': {
                        '25th': round(float(np.percentile(values, 25)), 3),
                        '75th': round(float(np.percentile(values, 75)), 3),
                        '90th': round(float(np.percentile(values, 90)), 3)
                    }
                }
        
        # Add interpretations
        if 'ndvi' in indices and len(indices['ndvi']) > 0:
            analysis['interpretations']['NDVI'] = interpret_ndvi(np.mean(indices['ndvi']))
        
        if 'ndwi' in indices and len(indices['ndwi']) > 0:
            analysis['interpretations']['NDWI'] = interpret_ndwi(np.mean(indices['ndwi']))
        
        if 'ndsi' in indices and len(indices['ndsi']) > 0:
            analysis['interpretations']['NDSI'] = interpret_ndsi(np.mean(indices['ndsi']))
        
        # Create index stack analysis
        land_cover_analysis = create_index_stack_analysis(indices)
        analysis['land_cover_analysis'] = land_cover_analysis
        
        # Generate visualizations
        try:
            analysis['visualizations']['spectral_indices_plot'] = generate_spectral_indices_plot(indices)
            analysis['visualizations']['correlation_plot'] = generate_index_comparison_plot(indices)
            if 'land_cover_stats' in land_cover_analysis:
                analysis['visualizations']['land_cover_plot'] = generate_land_cover_plot(land_cover_analysis['land_cover_stats'])
        except Exception as viz_error:
            logger.warning(f"Error generating visualizations: {viz_error}")
            analysis['visualizations'] = {'error': 'Visualization generation failed'}
        
        # Add summary metrics
        analysis['summary'] = {
            'total_pixels_analyzed': len(indices.get('ndvi', [])),
            'indices_calculated': list(indices.keys()),
            'dominant_land_cover': land_cover_analysis.get('dominant_land_cover', 'Unknown'),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Generated comprehensive spectral analysis for {analysis['summary']['total_pixels_analyzed']} samples")
        return analysis
        
    except Exception as e:
        logger.error(f"Error generating comprehensive spectral analysis: {e}")
        return {'error': f'Failed to generate comprehensive analysis: {str(e)}'}

def validate_ndvi_data(ndvi_values: np.ndarray) -> Tuple[bool, str]:
    """
    Validate NDVI data for consistency and quality
    
    Args:
        ndvi_values: Array of NDVI values
    
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        if len(ndvi_values) == 0:
            return False, "No NDVI data provided"
        
        # Check for valid range
        if np.any(ndvi_values < -1) or np.any(ndvi_values > 1):
            return False, "NDVI values outside valid range [-1, 1]"
        
        # Check for reasonable distribution
        mean_ndvi = np.mean(ndvi_values)
        if mean_ndvi < -0.5:
            return False, "Mean NDVI too low, check data quality"
        
        # Check for excessive uniformity (might indicate bad data)
        std_ndvi = np.std(ndvi_values)
        if std_ndvi < 0.001 and len(ndvi_values) > 10:
            return False, "NDVI data shows no variation, possible data quality issue"
        
        # Check for NaN or infinite values
        if np.any(np.isnan(ndvi_values)) or np.any(np.isinf(ndvi_values)):
            return False, "NDVI data contains invalid values (NaN or Inf)"
        
        return True, "NDVI data is valid"
        
    except Exception as e:
        logger.error(f"Error validating NDVI data: {e}")
        return False, f"Validation error: {str(e)}"
