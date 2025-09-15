import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, MapPin, Activity, Upload, Play, BarChart3, Satellite, School } from 'lucide-react';
import { fieldsAPI, predictionsAPI } from '../services/api';
import toast from 'react-hot-toast';
import SpectralAnalysis from './SpectralAnalysis';
import HyperspectralVisualization from './HyperspectralVisualization';
import SpectralIndexEducation from './SpectralIndexEducation';

const FieldDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [field, setField] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [predicting, setPredicting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [spectralData, setSpectralData] = useState(null);
  const [spectralLoading, setSpectralLoading] = useState(false);
  const [showHyperspectral, setShowHyperspectral] = useState(false);
  const [showEducation, setShowEducation] = useState(false);

  useEffect(() => {
    if (id) {
      fetchFieldData();
    }
  }, [id]);

  const fetchFieldData = async () => {
    setLoading(true);
    try {
      const [fieldResponse, predictionsResponse] = await Promise.all([
        fieldsAPI.getById(id),
        predictionsAPI.getHistory(id)
      ]);

      setField(fieldResponse.data.field);
      setPredictions(predictionsResponse.data.predictions || []);
    } catch (error) {
      console.error('Error fetching field data:', error);
      toast.error('Failed to load field data');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleRunPrediction = async () => {
    if (!field) return;
    
    setPredicting(true);
    toast.loading('🛰️ Running AI prediction with real satellite data...', { id: 'prediction' });
    
    try {
      // Use real satellite data - just pass field_id and let backend fetch real data
      const predictionData = {
        field_id: field.id,
        use_real_data: true,
        // Add some basic environmental data for the model
        temperature: 25.0,
        humidity: 65.0,
        soil_moisture: 40.0,
        ph: 6.8,
        precipitation: 10.0
      };
      
      const response = await predictionsAPI.predict(predictionData);
      
      // Show detailed success message based on prediction type
      if (response.data.prediction?.model_type === 'Real Agricultural Model') {
        toast.success('🛰️ Real satellite prediction completed!', { 
          id: 'prediction',
          duration: 4000
        });
      } else {
        toast.success('Prediction completed successfully!', { id: 'prediction' });
      }
      
      // Refresh the predictions list to show the new prediction
      await fetchFieldData();
      
    } catch (error) {
      console.error('Error running prediction:', error);
      toast.error('Failed to run prediction. Please try again.', { id: 'prediction' });
    } finally {
      setPredicting(false);
    }
  };

  const handleRunSpectralAnalysis = async () => {
    if (!field || !field.latitude || !field.longitude) {
      toast.error('Field coordinates are required for spectral analysis');
      return;
    }
    
    setSpectralLoading(true);
    toast.loading('🛰️ Running spectral analysis with real satellite data...', { id: 'spectral' });
    
    try {
      // Use real satellite data - let backend fetch real spectral bands
      const analysisData = {
        field_id: field.id,
        use_real_data: true
      };
      
      const response = await predictionsAPI.multiSpectralAnalysis(analysisData);
      
      setSpectralData(response.data);
      toast.success('Spectral analysis completed!', { id: 'spectral' });
      
    } catch (error) {
      console.error('Error running spectral analysis:', error);
      toast.error('Failed to run spectral analysis. Please try again.', { id: 'spectral' });
    } finally {
      setSpectralLoading(false);
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
      
      setUploading(true);
      toast.loading('Uploading file...', { id: 'upload' });
      
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('field_id', field.id);
        
        const response = await predictionsAPI.uploadData(formData);
        
        toast.success('File uploaded successfully!', { id: 'upload' });
        
        // Check if spectral analysis is included in the response
        if (response.data.spectral_analysis) {
          setSpectralData(response.data.spectral_analysis);
          toast.success('Spectral analysis completed from uploaded data!');
        }
        
        // After successful upload, automatically run prediction
        if (response.data.ready_for_prediction) {
          toast.success('Running prediction on uploaded data...');
          
          const predictionData = {
            field_id: field.id,
            file_id: response.data.file_id
          };
          
          await predictionsAPI.predict(predictionData);
          toast.success('Prediction completed!');
          
          // Refresh the predictions list
          await fetchFieldData();
        }
        
      } catch (error) {
        console.error('Error uploading file:', error);
        toast.error('Failed to upload file. Please try again.', { id: 'upload' });
      } finally {
        setUploading(false);
      }
    };
    input.click();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading field details...</p>
        </div>
      </div>
    );
  }

  if (!field) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 dark:text-gray-400">Field not found</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const getHealthStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'good':
        return 'text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900';
      case 'moderate':
        return 'text-yellow-600 dark:text-yellow-400 bg-yellow-100 dark:bg-yellow-900';
      case 'poor':
        return 'text-red-600 dark:text-red-400 bg-red-100 dark:bg-red-900';
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-900';
    }
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
                {field.name}
              </h1>
              {field.location && (
                <div className="mt-1 flex items-center text-sm text-gray-500 dark:text-gray-400">
                  <MapPin size={16} className="mr-1" />
                  {field.location}
                </div>
              )}
            </div>
            <div className="mt-4 flex space-x-3 md:mt-0 md:ml-4">
              <button
                onClick={handleFileUpload}
                disabled={uploading || predicting || spectralLoading}
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                ) : (
                  <Upload size={16} className="mr-2" />
                )}
                {uploading ? 'Uploading...' : 'Upload Data'}
              </button>
              <button
                onClick={handleRunSpectralAnalysis}
                disabled={uploading || predicting || spectralLoading}
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {spectralLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                ) : (
                  <BarChart3 size={16} className="mr-2" />
                )}
                {spectralLoading ? 'Analyzing...' : 'Spectral Analysis'}
              </button>
              <button
                onClick={() => setShowHyperspectral(true)}
                disabled={uploading || predicting || spectralLoading}
                className="inline-flex items-center px-4 py-2 border border-purple-500 rounded-md shadow-sm text-sm font-medium text-purple-700 dark:text-purple-300 bg-white dark:bg-gray-700 hover:bg-purple-50 dark:hover:bg-purple-900 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Satellite size={16} className="mr-2" />
                Hyperspectral Analysis
              </button>
              <button
                onClick={() => setShowEducation(true)}
                className="inline-flex items-center px-4 py-2 border border-indigo-500 rounded-md shadow-sm text-sm font-medium text-indigo-700 dark:text-indigo-300 bg-white dark:bg-gray-700 hover:bg-indigo-50 dark:hover:bg-indigo-900"
              >
                <School size={16} className="mr-2" />
                Learn Spectral Indices
              </button>
              <button
                onClick={handleRunPrediction}
                disabled={predicting || spectralLoading}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {predicting ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                ) : (
                  <Play size={16} className="mr-2" />
                )}
                {predicting ? 'Running...' : 'Run Prediction'}
              </button>
            </div>
          </div>
        </div>

        {/* Field Information */}
        <div className="mt-8 px-4 sm:px-0">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
                Field Information
              </h3>
              
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Crop Type</dt>
                  <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                    {field.crop_type || 'Not specified'}
                  </dd>
                </div>
                
                <div>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Area</dt>
                  <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                    {field.area_hectares ? `${field.area_hectares} ha` : 'Not specified'}
                  </dd>
                </div>
                
                {field.latitude && field.longitude && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Coordinates</dt>
                    <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                      {parseFloat(field.latitude).toFixed(4)}, {parseFloat(field.longitude).toFixed(4)}
                    </dd>
                  </div>
                )}
                
                <div>
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Created</dt>
                  <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                    {new Date(field.created_at).toLocaleDateString()}
                  </dd>
                </div>
                
                  {field.latitude && field.longitude && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">Real Data Sources</dt>
                    <dd className="mt-1 space-y-1">
                      <div className="text-xs text-green-600 dark:text-green-400 flex items-center">
                        <span className="mr-1">🛰️</span> NASA MODIS Satellite (Live NDVI)
                      </div>
                      <div className="text-xs text-blue-600 dark:text-blue-400 flex items-center">
                        <span className="mr-1">🌤️</span> OpenWeather API (Live Weather)
                      </div>
                      <div className="text-xs text-orange-600 dark:text-orange-400 flex items-center">
                        <span className="mr-1">🌍</span> Global Soil Database
                      </div>
                      <div className="text-xs text-purple-600 dark:text-purple-400 flex items-center">
                        <span className="mr-1">🤖</span> Agricultural ML Model
                      </div>
                    </dd>
                  </div>
                )}
              </div>
              
              {field.status && (
                <div className="mt-6">
                  <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Current Health Status</dt>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getHealthStatusColor(field.status)}`}>
                    {field.status}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Real-Time Data */}
        {predictions.length > 0 && predictions[0].satellite_data && (
          <div className="mt-8 px-4 sm:px-0">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
                  🛰️ Latest Satellite & Weather Data
                </h3>
                
                {(() => {
                  const latestPrediction = predictions[0];
                  const satelliteData = latestPrediction.satellite_data;
                  const weatherData = latestPrediction.weather_data;
                  
                  return (
                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                      {/* NDVI Data */}
                      <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                        <h4 className="text-md font-medium text-green-800 dark:text-green-300 mb-2">
                          🛰️ Vegetation Index (NDVI)
                        </h4>
                        <div className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm text-green-700 dark:text-green-400">Current Value:</span>
                            <span className="text-sm font-semibold text-green-900 dark:text-green-200">
                              {latestPrediction.ndvi_value ? Number(latestPrediction.ndvi_value).toFixed(3) : 'N/A'}
                            </span>
                          </div>
                          {satelliteData?.ndvi_stats && (
                            <>
                              <div className="flex justify-between">
                                <span className="text-xs text-green-600 dark:text-green-400">Mean:</span>
                                <span className="text-xs text-green-800 dark:text-green-300">
                                  {Number(satelliteData.ndvi_stats.mean).toFixed(3)}
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-xs text-green-600 dark:text-green-400">Std Dev:</span>
                                <span className="text-xs text-green-800 dark:text-green-300">
                                  {Number(satelliteData.ndvi_stats.std).toFixed(3)}
                                </span>
                              </div>
                            </>
                          )}
                          <div className="text-xs text-green-600 dark:text-green-400">
                            Source: {satelliteData?.source || 'NASA MODIS'}
                          </div>
                        </div>
                      </div>
                      
                      {/* Weather Data */}
                      {weatherData && (
                        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                          <h4 className="text-md font-medium text-blue-800 dark:text-blue-300 mb-2">
                            🌤️ Weather Conditions
                          </h4>
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-sm text-blue-700 dark:text-blue-400">Temperature:</span>
                              <span className="text-sm font-semibold text-blue-900 dark:text-blue-200">
                                {weatherData.temperature ? `${Math.round(weatherData.temperature)}°C` : 'N/A'}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-blue-700 dark:text-blue-400">Humidity:</span>
                              <span className="text-sm font-semibold text-blue-900 dark:text-blue-200">
                                {weatherData.humidity ? `${weatherData.humidity}%` : 'N/A'}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-blue-700 dark:text-blue-400">Precipitation:</span>
                              <span className="text-sm font-semibold text-blue-900 dark:text-blue-200">
                                {weatherData.precipitation ? `${weatherData.precipitation}mm` : '0mm'}
                              </span>
                            </div>
                            <div className="text-xs text-blue-600 dark:text-blue-400">
                              Source: {weatherData.source || 'OpenWeather API'}
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {/* Soil Data */}
                      {satelliteData?.soil_data && (
                        <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                          <h4 className="text-md font-medium text-orange-800 dark:text-orange-300 mb-2">
                            🌍 Soil Properties
                          </h4>
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-sm text-orange-700 dark:text-orange-400">pH Level:</span>
                              <span className="text-sm font-semibold text-orange-900 dark:text-orange-200">
                                {satelliteData.soil_data.ph ? Number(satelliteData.soil_data.ph).toFixed(1) : 'N/A'}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-orange-700 dark:text-orange-400">Moisture:</span>
                              <span className="text-sm font-semibold text-orange-900 dark:text-orange-200">
                                {satelliteData.soil_data.moisture ? `${Math.round(satelliteData.soil_data.moisture * 100)}%` : 'N/A'}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-sm text-orange-700 dark:text-orange-400">Organic Carbon:</span>
                              <span className="text-sm font-semibold text-orange-900 dark:text-orange-200">
                                {satelliteData.soil_data.organic_carbon ? `${Number(satelliteData.soil_data.organic_carbon).toFixed(2)}%` : 'N/A'}
                              </span>
                            </div>
                            <div className="text-xs text-orange-600 dark:text-orange-400">
                              Source: Global Soil Database
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })()}
              </div>
            </div>
          </div>
        )}

        {/* Spectral Analysis Section */}
        {spectralData && (
          <div className="mt-8 px-4 sm:px-0">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
                  🛰️ Multi-Spectral Analysis
                </h3>
                <SpectralAnalysis 
                  spectralData={spectralData} 
                  onAnalysisUpdate={(newData) => setSpectralData(newData)}
                />
              </div>
            </div>
          </div>
        )}

        {/* Prediction History */}
        <div className="mt-8 px-4 sm:px-0">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
                Prediction History
              </h3>
              
              {predictions.length === 0 ? (
                <div className="text-center py-8">
                  <Activity className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-gray-500 dark:text-gray-400 mb-4">
                    No predictions yet for this field
                  </p>
                  <button
                    onClick={handleRunPrediction}
                    disabled={predicting}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {predicting ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    ) : (
                      <Play size={16} className="mr-2" />
                    )}
                    {predicting ? 'Running...' : 'Run First Prediction'}
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {predictions.map((prediction) => (
                    <div key={prediction.id} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                      <div className="space-y-3">
                        {/* Header with status and model type */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getHealthStatusColor(prediction.status)}`}>
                              {prediction.status}
                            </span>
                            {prediction.model_type && (
                              <span className={`text-xs px-2 py-1 rounded ${
                                prediction.model_type === 'Real Agricultural Model' 
                                  ? 'text-green-700 dark:text-green-300 bg-green-100 dark:bg-green-900' 
                                  : 'text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900'
                              }`}>
                                {prediction.model_type === 'Real Agricultural Model' ? '🛰️ Real Satellite Data' : '🎭 Demo Mode'}
                              </span>
                            )}
                          </div>
                          <div className="text-right">
                            <span className="text-sm text-gray-500 dark:text-gray-400">
                              {new Date(prediction.created_at).toLocaleDateString()}
                            </span>
                            <div className="text-xs text-gray-400 mt-1">
                              {new Date(prediction.created_at).toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                        
                        {/* Prediction Metrics */}
                        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-gray-900 dark:text-white">
                              {prediction.health_score ? Number(prediction.health_score).toFixed(0) : '0'}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">Health Score</div>
                          </div>
                          
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                              {prediction.ndvi_value ? Number(prediction.ndvi_value).toFixed(3) : 'N/A'}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">NDVI Value</div>
                          </div>
                          
                          <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                              {prediction.confidence ? Number(prediction.confidence).toFixed(0) : '0'}%
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">Confidence</div>
                          </div>
                          
                          {prediction.recommendations && (
                            <div className="text-center">
                              <div className="text-2xl">
                                {prediction.recommendations.includes('irrigation') ? '💧' : 
                                 prediction.recommendations.includes('fertilizer') ? '🌱' : 
                                 prediction.recommendations.includes('pesticide') ? '🛡️' : '✅'}
                              </div>
                              <div className="text-xs text-gray-500 dark:text-gray-400">Action</div>
                            </div>
                          )}
                        </div>
                        
                        {/* Data Sources */}
                        {prediction.data_sources && (
                          <div className="border-t border-gray-200 dark:border-gray-600 pt-2">
                            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Data Sources:</div>
                            <div className="flex flex-wrap gap-2">
                              {prediction.data_sources.ndvi_source && (
                                <span className="text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded">
                                  NDVI: {prediction.data_sources.ndvi_source}
                                </span>
                              )}
                              {prediction.data_sources.weather_source && (
                                <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                                  Weather: {prediction.data_sources.weather_source}
                                </span>
                              )}
                              {prediction.data_sources.soil_source && (
                                <span className="text-xs bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 px-2 py-1 rounded">
                                  Soil: {prediction.data_sources.soil_source}
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                        
                        {/* Recommendations */}
                        {prediction.recommendations && (
                          <div className="border-t border-gray-200 dark:border-gray-600 pt-2">
                            <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">AI Recommendations:</div>
                            <div className="text-sm text-gray-700 dark:text-gray-300">
                              {Array.isArray(prediction.recommendations) 
                                ? prediction.recommendations.join(', ') 
                                : prediction.recommendations}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Hyperspectral Visualization Modal */}
        {showHyperspectral && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative min-h-screen flex items-center justify-center p-4">
              <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden">
                <HyperspectralVisualization
                  fieldId={field.id}
                  cropType={field.crop_type || 'general'}
                  onClose={() => setShowHyperspectral(false)}
                />
              </div>
            </div>
          </div>
        )}

        {/* Spectral Index Education Modal */}
        <SpectralIndexEducation
          open={showEducation}
          onClose={() => setShowEducation(false)}
        />
      </div>
    </div>
  );
};

export default FieldDetails;
