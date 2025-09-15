import requests
import json

# Test the multi-spectral analysis API
url = 'http://localhost:5000/api/predictions/multi-spectral-analysis'
headers = {'Content-Type': 'application/json'}

# Sample data that the frontend would send
data = {
    "spectral_bands": {
        "red": [0.05, 0.06, 0.04, 0.07, 0.05],
        "green": [0.07, 0.08, 0.06, 0.09, 0.07],
        "nir": [0.6, 0.7, 0.5, 0.8, 0.65],
        "swir": [0.1, 0.12, 0.08, 0.15, 0.11]
    },
    "location": {
        "latitude": 40.7128,
        "longitude": -74.0060
    }
}

print("🧪 Testing Multi-Spectral Analysis API...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, headers=headers, timeout=30)
    print(f"\n📡 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCESS! Multi-spectral analysis working!")
        print(f"\n📊 Results:")
        if 'indices_stats' in result:
            print(f"   Indices: {list(result['indices_stats'].keys())}")
            for idx, stats in result['indices_stats'].items():
                print(f"   {idx}: mean={stats.get('mean', 0):.3f}")
        
        if 'land_cover_analysis' in result:
            land_cover = result['land_cover_analysis'].get('land_cover_stats', {})
            print(f"   Land cover types: {len(land_cover)}")
            
        if 'visualizations' in result:
            viz_count = len([v for v in result['visualizations'].values() if v])
            print(f"   Visualizations: {viz_count} generated")
    else:
        print(f"❌ ERROR: {response.text}")

except requests.exceptions.ConnectionError:
    print("❌ Connection failed - is the backend running on port 5000?")
    print("   Start with: cd backend && python app.py")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n🎯 If successful, try the frontend at http://localhost:3000")
print("   Login: demo@crophealth.com / demo123")
print("   Navigate to 'Spectral Analysis' and click 'Run Analysis'")
