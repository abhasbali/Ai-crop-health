#!/usr/bin/env python3
"""
Google Earth Engine Integration Test Script
Tests the real satellite data integration for crop health monitoring

Service Account: abhasbali@uber-462705.iam.gserviceaccount.com
Project: uber-462705
"""

import sys
import os
import numpy as np
from datetime import datetime

# Add backend to path
sys.path.append('backend')

def test_gee_installation():
    """Test if Google Earth Engine is properly installed"""
    print("🔧 Testing Google Earth Engine Installation")
    print("-" * 50)
    
    try:
        import ee
        print("✅ earthengine-api package installed")
        print(f"   Version: {ee.__version__}")
        return True
    except ImportError as e:
        print(f"❌ earthengine-api not installed: {e}")
        print("   Install with: pip install earthengine-api")
        return False

def test_gee_authentication():
    """Test Google Earth Engine authentication"""
    print("\n🔐 Testing Google Earth Engine Authentication")
    print("-" * 50)
    
    try:
        import ee
        
        # Try to initialize with your service account
        project_id = "uber-462705"
        service_account = "abhasbali@uber-462705.iam.gserviceaccount.com"
        
        print(f"🏢 Project ID: {project_id}")
        print(f"👤 Service Account: {service_account}")
        
        # Try different authentication methods
        auth_methods = []
        
        # Method 1: Environment variable
        gac_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if gac_path:
            auth_methods.append(f"Environment variable: {gac_path}")
        
        # Method 2: Look for key files in common locations
        possible_key_locations = [
            f"gee-service-account-key.json",
            f"service-account-key.json",
            f"{service_account.split('@')[0]}-key.json"
        ]
        
        for key_file in possible_key_locations:
            if os.path.exists(key_file):
                auth_methods.append(f"Key file found: {key_file}")
        
        if auth_methods:
            print("🔑 Available authentication methods:")
            for method in auth_methods:
                print(f"   - {method}")
        else:
            print("⚠️ No authentication credentials found")
            print("   You'll need to:")
            print("   1. Download your service account key JSON file")
            print("   2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
            print("   3. Or place the key file in the project directory")
        
        # Try to initialize (this will help identify auth issues)
        try:
            ee.Initialize(project=project_id)
            print("✅ Google Earth Engine authentication successful!")
            return True
        except Exception as auth_error:
            print(f"❌ Authentication failed: {auth_error}")
            print("\n🔧 Authentication Setup Instructions:")
            print(f"   1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts?project={project_id}")
            print(f"   2. Find your service account: {service_account}")
            print("   3. Create and download a JSON key file")
            print("   4. Set environment variable: GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
            print("   5. Or run: gcloud auth application-default login")
            return False
            
    except Exception as e:
        print(f"❌ Error during authentication test: {e}")
        return False

def test_gee_satellite_module():
    """Test our custom GEE satellite module"""
    print("\n🛰️ Testing GEE Satellite Module")
    print("-" * 50)
    
    try:
        from utils.gee_satellite import GEESatelliteDataProvider, get_real_satellite_data
        print("✅ GEE satellite module imported successfully")
        
        # Create provider instance
        provider = GEESatelliteDataProvider()
        print(f"✅ Provider initialized")
        print(f"   Project: {provider.project_id}")
        print(f"   Service Account: {provider.service_account_email}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import GEE satellite module: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing satellite module: {e}")
        return False

def test_satellite_data_fetch():
    """Test fetching real satellite data"""
    print("\n📡 Testing Satellite Data Fetching")
    print("-" * 50)
    
    try:
        from utils.gee_satellite import get_real_satellite_data
        
        # Test coordinates (agricultural areas)
        test_locations = [
            ("Iowa Corn Belt", 42.0, -93.5),
            ("California Central Valley", 36.5, -120.0),
            ("Nebraska Farmland", 41.5, -99.5)
        ]
        
        for name, lat, lon in test_locations:
            print(f"\n🌍 Testing: {name} ({lat}, {lon})")
            
            try:
                result = get_real_satellite_data(lat, lon)
                
                if result.get('success'):
                    print(f"✅ Data retrieved: {result['source']}")
                    print(f"   Resolution: {result.get('resolution', 'Unknown')}")
                    print(f"   Pixels: {result.get('pixel_count', 0)}")
                    
                    if 'spectral_bands' in result:
                        bands = result['spectral_bands']
                        print(f"   Bands: {list(bands.keys())}")
                        for band, values in bands.items():
                            if isinstance(values, list) and len(values) > 0:
                                mean_val = np.mean(values)
                                print(f"     {band.upper()}: mean={mean_val:.3f}, count={len(values)}")
                    
                    if 'acquisition_date' in result:
                        print(f"   Date: {result['acquisition_date']}")
                    if 'cloud_cover' in result:
                        print(f"   Clouds: {result['cloud_cover']:.1f}%")
                        
                    return True  # Success with at least one location
                    
                else:
                    print(f"⚠️ No data: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"❌ Error for {name}: {e}")
        
        print("\n⚠️ No satellite data retrieved from any test location")
        return False
        
    except Exception as e:
        print(f"❌ Error during satellite data test: {e}")
        return False

def test_integration_with_weather_api():
    """Test integration with the existing weather API"""
    print("\n🌤️ Testing Integration with Weather API")
    print("-" * 50)
    
    try:
        from utils.satellite_data import get_comprehensive_field_data
        
        # Test agricultural coordinates
        test_lat, test_lon = 40.0, -95.0  # Nebraska
        
        print(f"🌍 Testing comprehensive data for {test_lat}, {test_lon}")
        
        result = get_comprehensive_field_data(test_lat, test_lon)
        
        if result.get('success'):
            print("✅ Comprehensive data retrieved successfully!")
            
            # Check weather data
            if 'weather' in result:
                weather = result['weather']
                print(f"🌡️ Weather: {weather['temperature']}°C, {weather['humidity']}% humidity")
                print(f"   Source: {weather['source']}")
            
            # Check satellite data
            if 'spectral_bands' in result:
                bands = result['spectral_bands']
                print(f"🛰️ Satellite bands: {list(bands.keys())}")
                
                if 'satellite_data_source' in result:
                    source = result['satellite_data_source']
                    print(f"   Source: {source}")
                    
                    if 'Google Earth Engine' in source:
                        print("✅ Using REAL satellite data from Google Earth Engine!")
                        if 'satellite_metadata' in result:
                            meta = result['satellite_metadata']
                            print(f"   Metadata: {meta}")
                    else:
                        print("⚠️ Using synthetic satellite data (fallback)")
            
            # Check soil data
            if 'soil' in result:
                soil = result['soil']
                print(f"🌍 Soil: pH {soil['ph']}, {soil['moisture']}% moisture")
                print(f"   Source: {soil['source']}")
            
            return True
            
        else:
            print(f"❌ Comprehensive data failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during integration test: {e}")
        return False

def main():
    """Run the complete Google Earth Engine integration test"""
    print("🛰️ Google Earth Engine Integration Test Suite")
    print("=" * 60)
    print("Service Account: abhasbali@uber-462705.iam.gserviceaccount.com")
    print("Project: uber-462705")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("GEE Installation", test_gee_installation),
        ("GEE Authentication", test_gee_authentication),
        ("GEE Satellite Module", test_gee_satellite_module),
        ("Satellite Data Fetching", test_satellite_data_fetch),
        ("Weather API Integration", test_integration_with_weather_api)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
        print("Your Google Earth Engine integration is working correctly.")
        print("\n💡 Your application now uses REAL satellite data:")
        print("   🛰️ Landsat 8/9 (30m resolution)")
        print("   🛰️ Sentinel-2 (10-20m resolution)")  
        print("   🛰️ MODIS NDVI (250m resolution)")
        print("   🌤️ WeatherAPI.com (real weather)")
        print("   🌍 SoilGrids (real soil data)")
        
    elif passed >= 3:
        print("\n⚠️ MOSTLY WORKING - Some issues detected")
        print("Your system will work with fallback to synthetic data where needed.")
        
    else:
        print("\n❌ SIGNIFICANT ISSUES - Setup required")
        print("\n🔧 Next Steps:")
        print("   1. Install: pip install earthengine-api")
        print("   2. Set up authentication with your service account")
        print("   3. Download service account key JSON file") 
        print("   4. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("   5. Run this test again")
    
    print(f"\n📞 For help with authentication:")
    print("   https://developers.google.com/earth-engine/guides/service_account")

if __name__ == "__main__":
    main()
