import React, { useState, useEffect } from 'react';
import {
  ChevronDown,
  ChevronUp,
  Info,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Bug,
  Sprout,
  Satellite,
  X
} from 'lucide-react';
import { predictionsAPI } from '../services/api';
import toast from 'react-hot-toast';

const HyperspectralVisualization = ({ fieldId, cropType = 'general', onClose }) => {
  const [loading, setLoading] = useState(false);
  const [visualization, setVisualization] = useState(null);
  const [error, setError] = useState(null);
  const [expandedSections, setExpandedSections] = useState({});

  useEffect(() => {
    if (fieldId) {
      generateVisualization();
    }
  }, [fieldId, cropType]);

  const generateVisualization = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await predictionsAPI.hyperspectralVisualization({
        field_id: fieldId,
        crop_type: cropType,
        use_real_data: true
      });

      setVisualization(response.data);
    } catch (err) {
      console.error('Hyperspectral visualization error:', err);
      const errorMessage = err.response?.data?.details || 
                          err.response?.data?.error || 
                          err.message || 
                          'Failed to generate hyperspectral visualization';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getRiskLevelColor = (level) => {
    const colors = {
      'low': 'text-green-600 bg-green-100',
      'medium': 'text-yellow-600 bg-yellow-100', 
      'high': 'text-red-600 bg-red-100'
    };
    return colors[level] || 'text-gray-600 bg-gray-100';
  };

  const getHealthScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-green-500';
    if (score >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const SpectralIndexCard = ({ index, data, explanation }) => {
    // Safety check for explanation object
    if (!explanation || !data) {
      return (
        <div className="bg-gray-100 dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 mb-4">
          <div className="p-4">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
              {index?.toUpperCase() || 'Loading...'}
            </h4>
            <p className="text-gray-600 dark:text-gray-400">Loading spectral data...</p>
          </div>
        </div>
      );
    }

    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 mb-4">
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
              {explanation.name || index?.toUpperCase() || 'Unknown Index'}
            </h4>
            <button 
              className="text-blue-500 hover:text-blue-700"
              title={explanation.significance || 'Spectral index information'}
            >
              <Info size={16} />
            </button>
          </div>
        
        <div className="mb-3">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            <strong>Formula:</strong> {explanation.formula || 'Formula not available'}
          </p>
        </div>
        
        <div className="grid grid-cols-2 gap-4 mb-3">
          <div>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              <strong>Mean:</strong> {data.mean?.toFixed(3) || 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              <strong>Range:</strong> {data.min?.toFixed(3) || 'N/A'} - {data.max?.toFixed(3) || 'N/A'}
            </p>
          </div>
        </div>

        <div className="mb-3">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full" 
              style={{ width: `${Math.min(Math.abs(data.mean || 0) * 100, 100)}%` }}
            ></div>
          </div>
        </div>

        <div className="border-t border-gray-200 dark:border-gray-600 pt-3">
          <button
            onClick={() => toggleSection(`interpretation-${index}`)}
            className="flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
          >
            <span>Interpretation</span>
            {expandedSections[`interpretation-${index}`] ? <ChevronUp size={16} className="ml-1" /> : <ChevronDown size={16} className="ml-1" />}
          </button>
          {expandedSections[`interpretation-${index}`] && explanation.interpretation && (
            <div className="mt-2 space-y-2">
              {Object.entries(explanation.interpretation).map(([level, desc]) => (
                <p key={level} className="text-sm text-gray-700 dark:text-gray-300">
                  <strong>{level.charAt(0).toUpperCase() + level.slice(1)}:</strong> {desc}
                </p>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <Satellite size={48} className="text-blue-600 mb-4 animate-pulse" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Analyzing Hyperspectral Data...
        </h3>
        <div className="w-full max-w-sm bg-gray-200 rounded-full h-2 mb-2">
          <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
        </div>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Processing satellite imagery and environmental data
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <XCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Analysis Failed</h3>
              <p className="mt-2 text-sm text-red-700">{error}</p>
              <button
                onClick={generateVisualization}
                className="mt-3 bg-red-100 hover:bg-red-200 text-red-800 font-bold py-1 px-3 rounded text-sm"
              >
                Retry Analysis
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!visualization) {
    return (
      <div className="flex flex-col items-center justify-center p-8">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Generate Hyperspectral Analysis
        </h3>
        <button
          onClick={generateVisualization}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700"
        >
          <Satellite size={16} className="mr-2" />
          Start Analysis
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 max-h-screen overflow-y-auto">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4 mb-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Hyperspectral Field Analysis
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {visualization.field_info?.name || 'Field Analysis'} • {cropType} crop
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
              Location: {visualization.field_coordinates?.[0]?.toFixed(4) || '0.0000'}, {visualization.field_coordinates?.[1]?.toFixed(4) || '0.0000'}
            </p>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              <X size={16} className="mr-1" />
              Close
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Spectral Indices */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Spectral Indices
          </h2>
          
          {visualization.spectral_indices && 
            Object.entries(visualization.spectral_indices).map(([index, data]) => {
              // Get explanation with fallback
              const explanation = visualization.spectral_explanations?.[index] || {
                name: index.toUpperCase(),
                formula: 'Formula not available',
                significance: 'Spectral index for agricultural analysis',
                interpretation: {}
              };
              
              return (
                <SpectralIndexCard
                  key={index}
                  index={index}
                  data={data}
                  explanation={explanation}
                />
              );
            })}
        </div>

        {/* Health Assessment */}
        <div>
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Health Assessment
          </h2>

          {/* Simple Health Summary */}
          {visualization.health_zones && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 mb-4">
              <div className="p-4">
                <div className="flex items-center mb-3">
                  <Sprout className="text-green-600 mr-2" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Field Health Summary
                  </h3>
                </div>
                
                {visualization.health_zones.crop_health && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Crop Health</span>
                      <span className={`text-2xl font-bold ${getHealthScoreColor(visualization.health_zones.crop_health.overall_score)}`}>
                        {Math.round(visualization.health_zones.crop_health.overall_score * 100)}%
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Dominant Zone: {visualization.health_zones.crop_health.dominant_zone}
                    </div>
                  </div>
                )}

                {visualization.pest_assessment && (
                  <div className="border-t border-gray-200 dark:border-gray-600 pt-3">
                    <div className="flex items-center mb-2">
                      <Bug className="mr-2" style={{ color: visualization.pest_assessment.risk_level === 'high' ? '#ef4444' : visualization.pest_assessment.risk_level === 'medium' ? '#f59e0b' : '#10b981' }} />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Pest Risk</span>
                    </div>
                    <div className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(visualization.pest_assessment.risk_level)}`}>
                      {visualization.pest_assessment.risk_level.toUpperCase()}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      Risk Score: {Math.round(visualization.pest_assessment.overall_risk * 100)}%
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recommendations */}
      {visualization.recommendations && visualization.recommendations.length > 0 && (
        <div className="mt-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Management Recommendations
          </h2>
          <div className="space-y-3">
            {visualization.recommendations.map((rec, index) => {
              const priorityColors = {
                high: 'bg-red-50 border-red-200 text-red-800',
                medium: 'bg-yellow-50 border-yellow-200 text-yellow-800',
                low: 'bg-blue-50 border-blue-200 text-blue-800'
              };
              return (
                <div key={index} className={`border rounded-lg p-4 ${priorityColors[rec.priority] || priorityColors.low}`}>
                  <h4 className="font-semibold mb-2">{rec.title}</h4>
                  <p className="text-sm mb-2">{rec.description}</p>
                  <ul className="text-sm space-y-1 pl-4">
                    {rec.actions.map((action, actionIndex) => (
                      <li key={actionIndex} className="list-disc">{action}</li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Technical Details */}
      <div className="mt-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
          <button
            onClick={() => toggleSection('technical')}
            className="w-full px-4 py-3 text-left flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 rounded-t-lg"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Technical Details</h3>
            {expandedSections.technical ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          {expandedSections.technical && (
            <div className="px-4 pb-4 border-t border-gray-200 dark:border-gray-600">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Analysis Parameters</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Crop Type: {visualization.crop_type}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Analysis Date: {visualization.timestamp ? new Date(visualization.timestamp).toLocaleString() : 'N/A'}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Field Resolution: 20x20 pixels (simulated)</p>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Data Sources</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Spectral: Synthetic satellite data</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Weather: Real-time API data</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Thresholds: ICAR guidelines (India)</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HyperspectralVisualization;
