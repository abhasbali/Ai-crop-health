"""
Google Earth Engine Satellite Data Integration
Real multi-spectral satellite imagery for crop health monitoring

This module fetches real satellite data from:
- Landsat 8/9 (30m resolution, 16-day revisit)
- Sentinel-2 (10m resolution, 5-day revisit) 
- MODIS (250m resolution, daily)

Service Account: abhasbali@uber-462705.iam.gserviceaccount.com
"""

import ee
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import os
import json
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

class GEESatelliteDataProvider:
    """Google Earth Engine satellite data provider for real multi-spectral imagery"""
    
    def __init__(self):
        self.initialized = False
        self.service_account_email = os.getenv('GOOGLE_EARTH_ENGINE_SERVICE_ACCOUNT', "abhasbali@uber-462705.iam.gserviceaccount.com")
        self.project_id = os.getenv('GOOGLE_EARTH_ENGINE_PROJECT', "uber-462705")
        
    def initialize_gee(self, service_account_key_path: str = None) -> bool:
        """
        Initialize Google Earth Engine with service account authentication
        
        Args:
            service_account_key_path: Path to service account JSON key file
            
        Returns:
            bool: Success status
        """
        try:
            if self.initialized:
                return True
            
            # Get service account key path from environment or parameter
            if not service_account_key_path:
                service_account_key_path = os.getenv('GOOGLE_EARTH_ENGINE_PRIVATE_KEY_PATH', './gee-service-account-key.json')
            
            # Quick check for credentials availability before attempting
            if not (service_account_key_path or os.getenv('GOOGLE_APPLICATION_CREDENTIALS')):
                logger.info("No Google Earth Engine credentials available, skipping initialization")
                return False
            
            # Try different authentication methods
            if service_account_key_path and os.path.exists(service_account_key_path):
                # Method 1: Service account key file
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_key_path,
                    scopes=['https://www.googleapis.com/auth/earthengine']
                )
                ee.Initialize(credentials=credentials, project=self.project_id)
                logger.info(f"✅ GEE initialized with service account key file: {service_account_key_path}")
                
            elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                # Method 2: Environment variable
                ee.Initialize(project=self.project_id)
                logger.info(f"✅ GEE initialized with environment credentials")
                
            else:
                # Method 3: Try default authentication
                ee.Initialize(project=self.project_id)
                logger.info(f"✅ GEE initialized with default credentials")
            
            self.initialized = True
            
            # Test connection
            test_image = ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_044034_20210101')
            test_info = test_image.getInfo()
            logger.info(f"✅ GEE connection test successful")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Earth Engine: {e}")
            return False
    
    def get_landsat8_data(self, latitude: float, longitude: float, 
                         start_date: str = None, end_date: str = None) -> Dict:
        """
        Fetch Landsat 8/9 satellite data for given coordinates and date range
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate  
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with spectral band data
        """
        try:
            if not self.initialized:
                if not self.initialize_gee():
                    return {'error': 'GEE initialization failed'}
            
            # Set default date range (last 30 days)
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Create point geometry
            point = ee.Geometry.Point([longitude, latitude])
            
            # Load Landsat 8/9 Collection 2 Surface Reflectance
            landsat = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                      .filterDate(start_date, end_date)
                      .filterBounds(point)
                      .filter(ee.Filter.lt('CLOUD_COVER', 30))  # < 30% clouds
                      .sort('CLOUD_COVER'))
            
            # Check if any images available
            image_count = landsat.size().getInfo()
            if image_count == 0:
                logger.warning(f"No Landsat images found for {latitude}, {longitude} between {start_date} and {end_date}")
                return self._get_fallback_data(latitude, longitude)
            
            # Get the least cloudy image
            image = landsat.first()
            
            # Landsat 8/9 bands mapping:
            # SR_B2 = Blue, SR_B3 = Green, SR_B4 = Red, SR_B5 = NIR, SR_B6 = SWIR1, SR_B7 = SWIR2
            bands = ['SR_B3', 'SR_B4', 'SR_B5', 'SR_B6']  # Green, Red, NIR, SWIR1
            
            # Create a region around the point (1km buffer)
            region = point.buffer(500)  # 500m radius = 1km diameter
            
            # Sample the image
            sample = image.select(bands).sample(
                region=region,
                scale=30,  # 30m resolution
                numPixels=50,  # Sample up to 50 pixels
                dropNulls=True
            )
            
            # Get the sampled data
            features = sample.getInfo()['features']
            
            if not features:
                logger.warning(f"No valid pixels found for {latitude}, {longitude}")
                return self._get_fallback_data(latitude, longitude)
            
            # Extract spectral values
            spectral_data = {
                'green': [],
                'red': [],
                'nir': [],
                'swir': []
            }
            
            for feature in features:
                props = feature['properties']
                # Landsat values are scaled by 0.0000275 with offset -0.2
                spectral_data['green'].append(max(0, props['SR_B3'] * 0.0000275 - 0.2))
                spectral_data['red'].append(max(0, props['SR_B4'] * 0.0000275 - 0.2))
                spectral_data['nir'].append(max(0, props['SR_B5'] * 0.0000275 - 0.2))
                spectral_data['swir'].append(max(0, props['SR_B6'] * 0.0000275 - 0.2))
            
            # Get image metadata
            image_info = image.getInfo()
            
            result = {
                'success': True,
                'source': 'Landsat 8/9 (Google Earth Engine)',
                'spectral_bands': spectral_data,
                'acquisition_date': image_info['properties']['DATE_ACQUIRED'],
                'cloud_cover': image_info['properties']['CLOUD_COVER'],
                'satellite': image_info['properties']['SPACECRAFT_ID'],
                'pixel_count': len(features),
                'coordinates': {'lat': latitude, 'lon': longitude},
                'resolution': '30m',
                'data_type': 'Surface Reflectance'
            }
            
            logger.info(f"✅ Retrieved Landsat data: {len(features)} pixels, {result['cloud_cover']:.1f}% clouds")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching Landsat data: {e}")
            return self._get_fallback_data(latitude, longitude)
    
    def get_sentinel2_data(self, latitude: float, longitude: float,
                          start_date: str = None, end_date: str = None) -> Dict:
        """
        Fetch Sentinel-2 satellite data for given coordinates and date range
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            start_date: Start date (YYYY-MM-DD) 
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with spectral band data
        """
        try:
            if not self.initialized:
                if not self.initialize_gee():
                    return {'error': 'GEE initialization failed'}
            
            # Set default date range (last 30 days)
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Create point geometry
            point = ee.Geometry.Point([longitude, latitude])
            
            # Load Sentinel-2 Surface Reflectance collection
            sentinel = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                       .filterDate(start_date, end_date)
                       .filterBounds(point)
                       .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
                       .sort('CLOUDY_PIXEL_PERCENTAGE'))
            
            # Check if any images available
            image_count = sentinel.size().getInfo()
            if image_count == 0:
                logger.warning(f"No Sentinel-2 images found for {latitude}, {longitude}")
                return self.get_landsat8_data(latitude, longitude, start_date, end_date)
            
            # Get the least cloudy image
            image = sentinel.first()
            
            # Sentinel-2 bands: B3=Green, B4=Red, B8=NIR, B11=SWIR1
            bands = ['B3', 'B4', 'B8', 'B11']
            
            # Create sampling region
            region = point.buffer(500)  # 500m radius
            
            # Sample the image
            sample = image.select(bands).sample(
                region=region,
                scale=20,  # 20m resolution (compromise between 10m and 20m bands)
                numPixels=100,  # More pixels due to higher resolution
                dropNulls=True
            )
            
            # Get sampled data
            features = sample.getInfo()['features']
            
            if not features:
                logger.warning(f"No valid Sentinel-2 pixels found")
                return self.get_landsat8_data(latitude, longitude, start_date, end_date)
            
            # Extract spectral values
            spectral_data = {
                'green': [],
                'red': [],  
                'nir': [],
                'swir': []
            }
            
            for feature in features:
                props = feature['properties']
                # Sentinel-2 values are already in reflectance (0-10000 scale)
                spectral_data['green'].append(max(0, min(1, props['B3'] / 10000)))
                spectral_data['red'].append(max(0, min(1, props['B4'] / 10000)))
                spectral_data['nir'].append(max(0, min(1, props['B8'] / 10000)))
                spectral_data['swir'].append(max(0, min(1, props['B11'] / 10000)))
            
            # Get image metadata
            image_info = image.getInfo()
            
            result = {
                'success': True,
                'source': 'Sentinel-2 (Google Earth Engine)',
                'spectral_bands': spectral_data,
                'acquisition_date': image_info['properties']['PRODUCT_ID'][:8],  # Extract date
                'cloud_cover': image_info['properties']['CLOUDY_PIXEL_PERCENTAGE'],
                'satellite': 'Sentinel-2',
                'pixel_count': len(features),
                'coordinates': {'lat': latitude, 'lon': longitude},
                'resolution': '10-20m',
                'data_type': 'Surface Reflectance'
            }
            
            logger.info(f"✅ Retrieved Sentinel-2 data: {len(features)} pixels, {result['cloud_cover']:.1f}% clouds")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching Sentinel-2 data: {e}")
            return self.get_landsat8_data(latitude, longitude, start_date, end_date)
    
    def get_modis_ndvi(self, latitude: float, longitude: float,
                       start_date: str = None, end_date: str = None) -> Dict:
        """
        Fetch MODIS NDVI data for vegetation analysis
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with NDVI data
        """
        try:
            if not self.initialized:
                if not self.initialize_gee():
                    return {'error': 'GEE initialization failed'}
            
            # Set default date range
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
            
            # Create point geometry
            point = ee.Geometry.Point([longitude, latitude])
            
            # Load MODIS NDVI collection (16-day composite)
            modis = (ee.ImageCollection('MODIS/061/MOD13Q1')
                    .filterDate(start_date, end_date)
                    .filterBounds(point)
                    .select('NDVI'))
            
            # Get the most recent image
            image_count = modis.size().getInfo()
            if image_count == 0:
                return {'error': 'No MODIS data available for this location/time'}
            
            image = modis.sort('system:time_start', False).first()
            
            # Sample NDVI at the point
            sample = image.sample(
                region=point.buffer(250),  # 250m buffer (MODIS pixel size)
                scale=250,
                numPixels=5
            )
            
            features = sample.getInfo()['features']
            
            if not features:
                return {'error': 'No MODIS NDVI data at this location'}
            
            # Extract NDVI values (MODIS NDVI is scaled by 10000)
            ndvi_values = []
            for feature in features:
                ndvi_raw = feature['properties']['NDVI']
                ndvi_values.append(ndvi_raw / 10000.0)  # Convert to -1 to 1 range
            
            avg_ndvi = np.mean(ndvi_values)
            
            result = {
                'success': True,
                'source': 'MODIS NDVI (Google Earth Engine)',
                'ndvi_values': ndvi_values,
                'avg_ndvi': round(float(avg_ndvi), 3),
                'pixel_count': len(features),
                'coordinates': {'lat': latitude, 'lon': longitude},
                'resolution': '250m',
                'data_type': '16-day NDVI composite'
            }
            
            logger.info(f"✅ Retrieved MODIS NDVI: {avg_ndvi:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching MODIS NDVI: {e}")
            return {'error': str(e)}
    
    def get_best_available_data(self, latitude: float, longitude: float,
                               start_date: str = None, end_date: str = None) -> Dict:
        """
        Get the best available satellite data, trying multiple sources
        
        Priority order:
        1. Sentinel-2 (highest resolution, frequent revisit)
        2. Landsat 8/9 (good resolution, reliable)
        3. MODIS (lower resolution but always available)
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with best available satellite data
        """
        logger.info(f"🛰️ Fetching best satellite data for {latitude}, {longitude}")
        
        # Try Sentinel-2 first (best resolution)
        result = self.get_sentinel2_data(latitude, longitude, start_date, end_date)
        if result.get('success') and result.get('pixel_count', 0) > 5:
            logger.info(f"✅ Using Sentinel-2 data ({result['pixel_count']} pixels)")
            return result
        
        # Fall back to Landsat
        result = self.get_landsat8_data(latitude, longitude, start_date, end_date)
        if result.get('success') and result.get('pixel_count', 0) > 3:
            logger.info(f"✅ Using Landsat data ({result['pixel_count']} pixels)")
            return result
        
        # Final fallback to synthetic data with MODIS NDVI if available
        modis_result = self.get_modis_ndvi(latitude, longitude, start_date, end_date)
        fallback_data = self._get_fallback_data(latitude, longitude)
        
        if modis_result.get('success'):
            fallback_data['modis_ndvi'] = modis_result['avg_ndvi']
            fallback_data['real_ndvi_source'] = 'MODIS'
            logger.info(f"✅ Using synthetic data with real MODIS NDVI: {modis_result['avg_ndvi']:.3f}")
        else:
            logger.warning("⚠️ No satellite data available, using synthetic data")
        
        return fallback_data
    
    def _get_fallback_data(self, latitude: float, longitude: float) -> Dict:
        """Generate realistic synthetic data when satellite data unavailable"""
        
        # Generate location-specific synthetic spectral data
        n_pixels = 25
        
        # Use location as seed for consistent but different results per field
        seed = int(abs(latitude * 1000 + longitude * 1000) % 2147483647)
        np.random.seed(seed)
        
        # Location-based adjustments
        abs_lat = abs(latitude)
        climate_factor = 1.0
        if abs_lat < 23.5:  # Tropical
            climate_factor = 1.3
        elif abs_lat < 35:  # Subtropical  
            climate_factor = 1.1
        elif abs_lat > 50:  # Cold regions
            climate_factor = 0.8
        
        # Base reflectance values typical for agricultural areas
        base_values = {
            'green': 0.08 * climate_factor,
            'red': 0.05 * climate_factor, 
            'nir': 0.45 * climate_factor,
            'swir': 0.25 * climate_factor
        }
        
        # Add realistic location-specific variation
        spectral_data = {}
        for band, base_val in base_values.items():
            # Use beta distribution for more realistic spectral curves
            if band == 'nir':  # Higher values for vegetation
                values = np.random.beta(4, 2, n_pixels) * base_val * 1.5 + base_val * 0.3
            else:
                values = np.random.beta(2, 4, n_pixels) * base_val * 2
            
            values = np.clip(values, 0.001, 0.95)  # Keep in realistic range
            spectral_data[band] = values.tolist()
        
        # Reset random seed
        np.random.seed(None)
        
        return {
            'success': True,
            'source': 'Synthetic (Satellite data unavailable)',
            'spectral_bands': spectral_data,
            'pixel_count': n_pixels,
            'coordinates': {'lat': latitude, 'lon': longitude},
            'resolution': 'simulated',
            'data_type': 'fallback_synthetic'
        }

# Global instance
gee_provider = GEESatelliteDataProvider()

def get_real_satellite_data(latitude: float, longitude: float, 
                           start_date: str = None, end_date: str = None) -> Dict:
    """
    Main function to get real satellite data from Google Earth Engine
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate  
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        Dictionary with satellite data or fallback synthetic data
    """
    try:
        import concurrent.futures
        import signal
        
        def fetch_with_timeout():
            return gee_provider.get_best_available_data(latitude, longitude, start_date, end_date)
        
        # Use a ThreadPoolExecutor with timeout to prevent hanging
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(fetch_with_timeout)
            try:
                # Wait maximum 3 seconds for GEE data
                result = future.result(timeout=3)
                return result
            except concurrent.futures.TimeoutError:
                logger.warning("⚠️ Google Earth Engine data fetch timed out, using fallback")
                return gee_provider._get_fallback_data(latitude, longitude)
                
    except Exception as e:
        logger.error(f"Error in satellite data retrieval: {e}")
        return gee_provider._get_fallback_data(latitude, longitude)

def initialize_gee(key_file_path: str = None) -> bool:
    """
    Initialize Google Earth Engine with authentication
    
    Args:
        key_file_path: Optional path to service account key file
        
    Returns:
        bool: Success status
    """
    return gee_provider.initialize_gee(key_file_path)

# Test function
if __name__ == "__main__":
    # Test coordinates (agricultural area in Iowa, USA)
    test_lat, test_lon = 42.0, -93.5
    
    print("🧪 Testing Google Earth Engine Integration")
    print(f"Service Account: abhasbali@uber-462705.iam.gserviceaccount.com")
    print(f"Testing coordinates: {test_lat}, {test_lon}")
    
    # Test the integration
    result = get_real_satellite_data(test_lat, test_lon)
    
    if result.get('success'):
        print(f"✅ Success! Source: {result['source']}")
        print(f"📊 Pixel count: {result['pixel_count']}")
        if 'spectral_bands' in result:
            bands = result['spectral_bands']
            for band, values in bands.items():
                print(f"   {band.upper()}: mean={np.mean(values):.3f}, count={len(values)}")
    else:
        print(f"❌ Failed: {result}")
