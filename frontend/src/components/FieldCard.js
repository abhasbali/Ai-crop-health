import React from 'react';
import { Link } from 'react-router-dom';
import { 
  MapPin, 
  Calendar, 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  MoreVertical,
  Edit,
  Trash2
} from 'lucide-react';

const FieldCard = ({ field, onEdit, onDelete }) => {
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

  const getTrendIcon = (trend) => {
    if (trend > 0) return <TrendingUp size={16} className="text-green-500" />;
    if (trend < 0) return <TrendingDown size={16} className="text-red-500" />;
    return <Minus size={16} className="text-gray-500" />;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No data';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Invalid date';
    }
  };

  const healthScore = field.health_score || 0;
  const lastPrediction = field.last_prediction;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 border border-gray-200 dark:border-gray-700">
      {/* Card Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
              {field.name}
            </h3>
            {field.location && (
              <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                <MapPin size={14} className="mr-1" />
                {field.location}
              </div>
            )}
          </div>
          
          {/* Health Status Badge */}
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${getHealthStatusColor(field.status)}`}>
            {field.status || 'Unknown'}
          </div>
        </div>
      </div>

      {/* Card Body */}
      <div className="p-4">
        {/* Field Details */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <div className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              Crop Type
            </div>
            <div className="text-sm font-medium text-gray-900 dark:text-white">
              {field.crop_type || 'Not specified'}
            </div>
          </div>
          
          <div>
            <div className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">
              Area (Ha)
            </div>
            <div className="text-sm font-medium text-gray-900 dark:text-white">
              {field.area_hectares ? `${field.area_hectares} ha` : 'Not specified'}
            </div>
          </div>
        </div>

        {/* Health Score */}
        {healthScore > 0 && (
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                Health Score
              </span>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                {healthScore}/100
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  healthScore >= 70 
                    ? 'bg-green-500' 
                    : healthScore >= 40 
                    ? 'bg-yellow-500' 
                    : 'bg-red-500'
                }`}
                style={{ width: `${healthScore}%` }}
              />
            </div>
          </div>
        )}

        {/* Coordinates */}
        {(field.latitude && field.longitude) && (
          <div className="mb-4">
            <div className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
              Coordinates
            </div>
            <div className="text-sm text-gray-700 dark:text-gray-300">
              {parseFloat(field.latitude).toFixed(4)}, {parseFloat(field.longitude).toFixed(4)}
            </div>
          </div>
        )}

        {/* Last Prediction */}
        {lastPrediction && (
          <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
              <div className="flex items-center">
                <Activity size={12} className="mr-1" />
                Last updated: {formatDate(lastPrediction)}
              </div>
              <div className="flex items-center space-x-1">
                {field.latest_prediction?.model_type === 'Real Agricultural Model' && (
                  <span className="text-green-600 dark:text-green-400" title="Using real satellite data">
                    🛰️
                  </span>
                )}
                {getTrendIcon(0)}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Card Footer */}
      <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-700 rounded-b-lg">
        <div className="flex justify-between items-center">
          <Link
            to={`/field/${field.id}`}
            className="text-primary-600 dark:text-primary-400 text-sm font-medium hover:text-primary-700 dark:hover:text-primary-300 transition-colors duration-200"
          >
            View Details
          </Link>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => onEdit && onEdit(field)}
              className="p-1 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors duration-200"
              title="Edit field"
            >
              <Edit size={16} />
            </button>
            
            <button
              onClick={() => onDelete && onDelete(field)}
              className="p-1 text-gray-500 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors duration-200"
              title="Delete field"
            >
              <Trash2 size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FieldCard;
