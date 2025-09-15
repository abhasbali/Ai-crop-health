import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Upload, Play, MapPin } from 'lucide-react';
import { predictionsAPI } from '../services/api';
import toast from 'react-hot-toast';
import SpectralAnalysis from '../components/SpectralAnalysis';

const SpectralAnalysisPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [spectralData, setSpectralData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [coordinates, setCoordinates] = useState({
    latitude: location.state?.latitude || 40.7128,
    longitude: location.state?.longitude || -74.0060
  });

  const handleRunAnalysis = async () => {
    setLoading(true);
    toast.loading('Running spectral analysis...', { id: 'spectral' });
    
    try {
      // Generate sample spectral band data for demonstration
      const sampleSpectralData = {
        spectral_bands: {
          red: Array.from({length: 100}, () => Math.random() * 0.1 + 0.05),
          green: Array.from({length: 100}, () => Math.random() * 0.1 + 0.06),
          nir: Array.from({length: 100}, () => Math.random() * 0.4 + 0.4),
          swir: Array.from({length: 100}, () => Math.random() * 0.2 + 0.1)
        },
        location: {
          latitude: parseFloat(coordinates.latitude),
          longitude: parseFloat(coordinates.longitude)
        }
      };
      
      const response = await predictionsAPI.multiSpectralAnalysis(sampleSpectralData);
      
      setSpectralData(response.data);
      toast.success('Spectral analysis completed!', { id: 'spectral' });
      
    } catch (error) {
      console.error('Error running spectral analysis:', error);
      toast.error('Failed to run spectral analysis. Please try again.', { id: 'spectral' });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = () => {
    // Create a file input element
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv,.json,.npz';
    input.onchange = async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      
      setLoading(true);
      toast.loading('Uploading and analyzing file...', { id: 'upload' });
      
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('field_id', 'spectral-analysis-page');
        
        const response = await predictionsAPI.uploadData(formData);
        
        // Check if spectral analysis is included in the response
        if (response.data.spectral_analysis) {
          setSpectralData(response.data.spectral_analysis);
          toast.success('File analyzed successfully!', { id: 'upload' });
        } else {
          toast.success('File uploaded successfully!', { id: 'upload' });
        }
        
      } catch (error) {
        console.error('Error uploading file:', error);
        toast.error('Failed to upload file. Please try again.', { id: 'upload' });
      } finally {
        setLoading(false);
      }
    };
    input.click();
  };

  const handleCoordinateChange = (field, value) => {
    setCoordinates(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 sm:px-0">
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 mb-4"
          >
            <ArrowLeft size={16} className="mr-1" />
            Back to Dashboard
          </button>
          
          <div className="md:flex md:items-center md:justify-between">
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
                🛰️ Multi-Spectral Analysis
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Analyze vegetation health, water content, snow cover, and land use using satellite spectral indices
              </p>
            </div>
            <div className="mt-4 flex space-x-3 md:mt-0 md:ml-4">
              <button
                onClick={handleFileUpload}
                disabled={loading}
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                ) : (
                  <Upload size={16} className="mr-2" />
                )}
                Upload Spectral Data
              </button>
              <button
                onClick={handleRunAnalysis}
                disabled={loading}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : (
                  <Play size={16} className="mr-2" />
                )}
                {loading ? 'Analyzing...' : 'Run Analysis'}
              </button>
            </div>
          </div>
        </div>

        {/* Configuration Panel */}
        <div className="mt-8 px-4 sm:px-0">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
                Analysis Configuration
              </h3>
              
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <MapPin size={16} className="inline mr-1" />
                    Latitude
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    value={coordinates.latitude}
                    onChange={(e) => handleCoordinateChange('latitude', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="40.7128"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <MapPin size={16} className="inline mr-1" />
                    Longitude
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    value={coordinates.longitude}
                    onChange={(e) => handleCoordinateChange('longitude', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                    placeholder="-74.0060"
                  />
                </div>
              </div>
              
              <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h4 className="text-sm font-medium text-blue-800 dark:text-blue-300 mb-2">
                  Spectral Indices Calculated:
                </h4>
                <div className="grid grid-cols-2 gap-2 text-sm text-blue-700 dark:text-blue-300">
                  <div>• NDVI - Vegetation Index</div>
                  <div>• NDWI - Water Index</div>
                  <div>• MNDWI - Modified Water Index</div>
                  <div>• NDSI - Snow Index</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Spectral Analysis Results */}
        {spectralData ? (
          <div className="mt-8 px-4 sm:px-0">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
                  Analysis Results
                </h3>
                <SpectralAnalysis 
                  spectralData={spectralData} 
                  onAnalysisUpdate={(newData) => setSpectralData(newData)}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-8 px-4 sm:px-0">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-8 text-center">
              <div className="text-gray-500 dark:text-gray-400">
                <svg className="w-16 h-16 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 11-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4zm9 1a1 1 0 010-2h4a1 1 0 011 1v4a1 1 0 01-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13.586 5H12zm-9 7a1 1 0 012 0v1.586l2.293-2.293a1 1 0 111.414 1.414L6.414 15H8a1 1 0 010 2H4a1 1 0 01-1-1v-4zm13-1a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 010-2h1.586l-2.293-2.293a1 1 0 111.414-1.414L15 13.586V12a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Ready for Analysis
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Run spectral analysis or upload satellite data with multiple bands (Red, Green, NIR, SWIR) to get started.
                </p>
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={handleRunAnalysis}
                    disabled={loading}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Play size={16} className="mr-2" />
                    Run Sample Analysis
                  </button>
                  <button
                    onClick={handleFileUpload}
                    disabled={loading}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Upload size={16} className="mr-2" />
                    Upload Data
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SpectralAnalysisPage;
