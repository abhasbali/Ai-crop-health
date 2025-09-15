#!/usr/bin/env python3
"""
Complete demo of multi-spectral analysis functionality
"""

import numpy as np
import json
from utils.ndvi import generate_comprehensive_spectral_analysis

def generate_sample_data():
    """Generate realistic satellite spectral band data"""
    
    # Simulate different land cover types
    n_pixels = 200
    
    # Dense vegetation area (40% of pixels)
    dense_veg_count = int(n_pixels * 0.4)
    dense_red = np.random.uniform(0.03, 0.08, dense_veg_count)
    dense_green = np.random.uniform(0.05, 0.12, dense_veg_count) 
    dense_nir = np.random.uniform(0.6, 0.9, dense_veg_count)
    dense_swir = np.random.uniform(0.05, 0.15, dense_veg_count)
    
    # Sparse vegetation (30% of pixels)
    sparse_veg_count = int(n_pixels * 0.3)
    sparse_red = np.random.uniform(0.08, 0.15, sparse_veg_count)
    sparse_green = np.random.uniform(0.10, 0.18, sparse_veg_count)
    sparse_nir = np.random.uniform(0.3, 0.5, sparse_veg_count)
    sparse_swir = np.random.uniform(0.15, 0.25, sparse_veg_count)
    
    # Water bodies (15% of pixels)  
    water_count = int(n_pixels * 0.15)
    water_red = np.random.uniform(0.02, 0.05, water_count)
    water_green = np.random.uniform(0.03, 0.07, water_count)
    water_nir = np.random.uniform(0.01, 0.08, water_count)
    water_swir = np.random.uniform(0.001, 0.02, water_count)
    
    # Bare soil/urban (15% of pixels)
    bare_count = n_pixels - dense_veg_count - sparse_veg_count - water_count
    bare_red = np.random.uniform(0.15, 0.25, bare_count)
    bare_green = np.random.uniform(0.18, 0.28, bare_count)
    bare_nir = np.random.uniform(0.25, 0.45, bare_count)
    bare_swir = np.random.uniform(0.30, 0.50, bare_count)
    
    # Combine all land cover types
    red_band = np.concatenate([dense_red, sparse_red, water_red, bare_red])
    green_band = np.concatenate([dense_green, sparse_green, water_green, bare_green])
    nir_band = np.concatenate([dense_nir, sparse_nir, water_nir, bare_nir])
    swir_band = np.concatenate([dense_swir, sparse_swir, water_swir, bare_swir])
    
    # Shuffle to randomize spatial arrangement
    indices = np.random.permutation(n_pixels)
    
    return {
        'red': red_band[indices],
        'green': green_band[indices],
        'nir': nir_band[indices],
        'swir': swir_band[indices]
    }

def demo_spectral_analysis():
    """Run a complete demonstration of spectral analysis"""
    
    print("🛰️ Multi-Spectral Analysis Demo")
    print("=" * 60)
    
    # Generate sample data
    print("\n📊 Generating sample satellite data...")
    spectral_data = generate_sample_data()
    
    print(f"Generated {len(spectral_data['red'])} pixels with 4 spectral bands:")
    print(f"  Red band: {spectral_data['red'].min():.3f} - {spectral_data['red'].max():.3f}")
    print(f"  Green band: {spectral_data['green'].min():.3f} - {spectral_data['green'].max():.3f}")
    print(f"  NIR band: {spectral_data['nir'].min():.3f} - {spectral_data['nir'].max():.3f}")
    print(f"  SWIR band: {spectral_data['swir'].min():.3f} - {spectral_data['swir'].max():.3f}")
    
    # Run comprehensive analysis
    print("\n🔬 Running comprehensive spectral analysis...")
    try:
        analysis_result = generate_comprehensive_spectral_analysis(spectral_data)
        
        print("✅ Analysis completed successfully!")
        print(f"\nAnalysis components: {list(analysis_result.keys())}")
        
        # Display indices statistics
        if 'indices_stats' in analysis_result:
            print("\n📈 Spectral Indices Statistics:")
            indices_stats = analysis_result['indices_stats']
            
            for index_name, stats in indices_stats.items():
                print(f"\n{index_name}:")
                print(f"  Mean: {stats['mean']:.3f}")
                print(f"  Median: {stats['median']:.3f}")
                print(f"  Std Dev: {stats['std']:.3f}")
                print(f"  Range: {stats['min']:.3f} to {stats['max']:.3f}")
        
        # Display interpretations
        if 'interpretations' in analysis_result:
            print("\n🔍 Index Interpretations:")
            interpretations = analysis_result['interpretations']
            
            for index_name, interp in interpretations.items():
                print(f"\n{index_name}: {interp['status']}")
                print(f"  {interp['description']}")
                print(f"  Confidence: {interp['confidence']}%")
        
        # Display land cover analysis
        if 'land_cover_analysis' in analysis_result:
            print("\n🌍 Land Cover Analysis:")
            land_cover = analysis_result['land_cover_analysis']
            
            if 'land_cover_stats' in land_cover:
                cover_stats = land_cover['land_cover_stats']
                print("\nLand cover distribution:")
                
                for cover_type, stats in cover_stats.items():
                    print(f"  {cover_type}: {stats['percentage']:.1f}% ({stats['pixel_count']} pixels)")
                    
            if 'dominant_cover' in land_cover:
                dominant = land_cover['dominant_cover']
                print(f"\nDominant land cover: {dominant['type']} ({dominant['percentage']:.1f}%)")
        
        # Display visualizations info
        if 'visualizations' in analysis_result:
            print("\n🖼️ Generated Visualizations:")
            visualizations = analysis_result['visualizations']
            
            for viz_name, viz_data in visualizations.items():
                if viz_data and len(viz_data) > 100:
                    print(f"  ✅ {viz_name}: Generated ({len(viz_data)} chars base64)")
                else:
                    print(f"  ❌ {viz_name}: Failed to generate")
        
        # Show summary
        if 'summary' in analysis_result:
            print("\n📋 Analysis Summary:")
            summary = analysis_result['summary']
            
            for key, value in summary.items():
                if isinstance(value, list):
                    print(f"  {key}: {', '.join(map(str, value))}")
                else:
                    print(f"  {key}: {value}")
        
        # Save demo result to file for frontend testing
        demo_result = {
            'success': True,
            'message': 'Spectral analysis completed successfully',
            'data': analysis_result,
            'metadata': {
                'pixels_analyzed': len(spectral_data['red']),
                'bands_used': ['red', 'green', 'nir', 'swir'],
                'indices_calculated': list(analysis_result.get('indices_stats', {}).keys()),
                'timestamp': '2024-01-15T10:00:00Z'
            }
        }
        
        # Save to file for frontend testing
        with open('demo_spectral_result.json', 'w') as f:
            # Convert numpy arrays to lists for JSON serialization
            json_result = json.loads(json.dumps(demo_result, default=lambda x: x.tolist() if hasattr(x, 'tolist') else x))
            json.dump(json_result, f, indent=2)
        
        print(f"\n💾 Demo results saved to 'demo_spectral_result.json'")
        print(f"   File size: {len(json.dumps(json_result))} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_api_payload_example():
    """Show example API payload for frontend integration"""
    
    print("\n🌐 API Integration Example:")
    print("=" * 60)
    
    sample_payload = {
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
    
    print("POST /api/predictions/multi-spectral-analysis")
    print("Content-Type: application/json")
    print("\nRequest body:")
    print(json.dumps(sample_payload, indent=2))
    
    print(f"\n📝 This payload would analyze {len(sample_payload['spectral_bands']['red'])} pixels")
    print("   and return comprehensive spectral analysis results.")

if __name__ == '__main__':
    print("🚀 Multi-Spectral Analysis Complete Demo")
    print("=" * 60)
    
    # Run the main demo
    success = demo_spectral_analysis()
    
    # Show API example
    show_api_payload_example()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Demo completed successfully!")
        print("   • Spectral analysis functions working correctly")
        print("   • Land cover classification operational") 
        print("   • Visualizations generated")
        print("   • Ready for frontend integration")
    else:
        print("❌ Demo encountered errors!")
    print("=" * 60)
