import React, { useState, useEffect } from 'react';
import { Line, Bar, Pie, Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const SpectralAnalysis = ({ spectralData, onAnalysisUpdate }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(false);

  // Check if we have spectral analysis data
  const hasSpectralData = spectralData && 
    spectralData.indices_stats && 
    Object.keys(spectralData.indices_stats).length > 0;

  // Index information for display
  const indexInfo = {
    NDVI: {
      name: 'Normalized Difference Vegetation Index',
      description: 'Measures vegetation health and density',
      color: '#228B22',
      range: 'Dense vegetation: >0.6, Moderate: 0.2-0.6, Sparse/Bare: <0.2'
    },
    NDWI: {
      name: 'Normalized Difference Water Index',
      description: 'Detects water content and moisture',
      color: '#0077BE',
      range: 'High water: >0.3, Moderate: 0.1-0.3, Low water: <0.1'
    },
    MNDWI: {
      name: 'Modified NDWI',
      description: 'Enhanced water body detection',
      color: '#4A9FDB',
      range: 'Water bodies: >0.3, Mixed: 0.0-0.3, Vegetation: <0.0'
    },
    NDSI: {
      name: 'Normalized Difference Snow Index',
      description: 'Identifies snow and ice cover',
      color: '#FF00FF',
      range: 'Snow/Ice: >0.4, Possible: 0.1-0.4, No snow: <0.1'
    }
  };

  // Create chart data for indices comparison
  const createIndicesBarChart = () => {
    if (!hasSpectralData) return null;

    const indices = Object.keys(spectralData.indices_stats);
    const means = indices.map(index => spectralData.indices_stats[index].mean);
    const colors = indices.map(index => indexInfo[index]?.color || '#666666');

    return {
      labels: indices,
      datasets: [
        {
          label: 'Mean Index Value',
          data: means,
          backgroundColor: colors.map(color => color + '80'), // Add transparency
          borderColor: colors,
          borderWidth: 2,
        },
      ],
    };
  };

  // Create chart data for land cover
  const createLandCoverChart = () => {
    if (!spectralData?.land_cover_analysis?.land_cover_stats) return null;

    const landCoverStats = spectralData.land_cover_analysis.land_cover_stats;
    const labels = Object.keys(landCoverStats);
    const data = labels.map(label => landCoverStats[label].percentage);
    const colors = labels.map(label => landCoverStats[label].color);

    return {
      labels,
      datasets: [
        {
          label: 'Land Cover Distribution (%)',
          data,
          backgroundColor: colors.map(color => color + '80'),
          borderColor: colors,
          borderWidth: 2,
        },
      ],
    };
  };

  // Chart options
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Spectral Indices Analysis',
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        min: -1,
        max: 1,
        title: {
          display: true,
          text: 'Index Value',
        },
      },
    },
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right',
      },
      title: {
        display: true,
        text: 'Land Cover Distribution',
      },
    },
  };

  // Render index card
  const renderIndexCard = (indexName, stats, interpretation) => {
    const info = indexInfo[indexName];
    if (!info || !stats) return null;

    return (
      <div key={indexName} className="bg-white rounded-lg shadow-md p-6 border-l-4" style={{ borderColor: info.color }}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">{indexName}</h3>
          <span className="px-3 py-1 rounded-full text-sm font-medium text-white" style={{ backgroundColor: info.color }}>
            {stats.mean.toFixed(3)}
          </span>
        </div>
        
        <p className="text-sm text-gray-600 mb-3">{info.description}</p>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-xs text-gray-500">Range</p>
            <p className="text-sm font-medium">{stats.min.toFixed(3)} to {stats.max.toFixed(3)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Std Dev</p>
            <p className="text-sm font-medium">{stats.std.toFixed(3)}</p>
          </div>
        </div>

        {interpretation && (
          <div className="bg-gray-50 rounded-lg p-3 mt-4">
            <p className="text-sm font-medium text-gray-800 mb-1">{interpretation.status}</p>
            <p className="text-xs text-gray-600">{interpretation.description}</p>
            <div className="flex items-center mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="h-2 rounded-full" 
                  style={{ 
                    width: `${interpretation.confidence}%`,
                    backgroundColor: info.color 
                  }}
                ></div>
              </div>
              <span className="ml-2 text-xs text-gray-500">{interpretation.confidence}%</span>
            </div>
          </div>
        )}

        <div className="mt-3">
          <p className="text-xs text-gray-500">Interpretation Guide:</p>
          <p className="text-xs text-gray-600">{info.range}</p>
        </div>
      </div>
    );
  };

  // Render overview tab
  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* Summary Stats */}
      {spectralData?.summary && (
        <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Analysis Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{spectralData.summary.total_pixels_analyzed}</p>
              <p className="text-sm text-gray-600">Pixels Analyzed</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{spectralData.summary.indices_calculated?.length || 0}</p>
              <p className="text-sm text-gray-600">Indices Calculated</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{spectralData.summary.dominant_land_cover}</p>
              <p className="text-sm text-gray-600">Dominant Cover</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">
                {spectralData.land_cover_analysis?.land_cover_stats ? Object.keys(spectralData.land_cover_analysis.land_cover_stats).length : 0}
              </p>
              <p className="text-sm text-gray-600">Cover Types</p>
            </div>
          </div>
        </div>
      )}

      {/* Index Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {hasSpectralData && Object.entries(spectralData.indices_stats).map(([indexName, stats]) =>
          renderIndexCard(indexName, stats, spectralData.interpretations?.[indexName])
        )}
      </div>
    </div>
  );

  // Render charts tab
  const renderChartsTab = () => {
    const barChartData = createIndicesBarChart();
    const pieChartData = createLandCoverChart();

    return (
      <div className="space-y-8">
        {/* Indices Comparison Chart */}
        {barChartData && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Spectral Indices Comparison</h3>
            <div className="h-96">
              <Bar data={barChartData} options={chartOptions} />
            </div>
          </div>
        )}

        {/* Land Cover Chart */}
        {pieChartData && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Land Cover Analysis</h3>
            <div className="h-96">
              <Pie data={pieChartData} options={pieOptions} />
            </div>
          </div>
        )}

        {/* Visualization Images */}
        {spectralData?.visualizations && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {spectralData.visualizations.spectral_indices_plot && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Statistical Distribution</h3>
                <img 
                  src={`data:image/png;base64,${spectralData.visualizations.spectral_indices_plot}`}
                  alt="Spectral Indices Distribution"
                  className="w-full h-auto rounded-lg"
                />
              </div>
            )}
            
            {spectralData.visualizations.correlation_plot && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Index Correlations</h3>
                <img 
                  src={`data:image/png;base64,${spectralData.visualizations.correlation_plot}`}
                  alt="Index Correlation Analysis"
                  className="w-full h-auto rounded-lg"
                />
              </div>
            )}
            
            {spectralData.visualizations.land_cover_plot && (
              <div className="bg-white rounded-lg shadow-md p-6 lg:col-span-2">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Land Cover Classification</h3>
                <img 
                  src={`data:image/png;base64,${spectralData.visualizations.land_cover_plot}`}
                  alt="Land Cover Classification"
                  className="w-full h-auto rounded-lg"
                />
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  // Render technical details tab
  const renderTechnicalTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Technical Specifications</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(indexInfo).map(([indexKey, info]) => (
            <div key={indexKey} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center mb-3">
                <div 
                  className="w-4 h-4 rounded-full mr-3" 
                  style={{ backgroundColor: info.color }}
                ></div>
                <h4 className="font-semibold text-gray-800">{indexKey}</h4>
              </div>
              
              <h5 className="font-medium text-gray-700 mb-2">{info.name}</h5>
              <p className="text-sm text-gray-600 mb-3">{info.description}</p>
              
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs font-medium text-gray-700 mb-1">Formula:</p>
                {indexKey === 'NDVI' && <p className="text-xs text-gray-600 font-mono">NDVI = (NIR - RED) / (NIR + RED)</p>}
                {indexKey === 'NDWI' && <p className="text-xs text-gray-600 font-mono">NDWI = (NIR - SWIR) / (NIR + SWIR)</p>}
                {indexKey === 'MNDWI' && <p className="text-xs text-gray-600 font-mono">MNDWI = (GREEN - SWIR) / (GREEN + SWIR)</p>}
                {indexKey === 'NDSI' && <p className="text-xs text-gray-600 font-mono">NDSI = (GREEN - SWIR) / (GREEN + SWIR)</p>}
              </div>
              
              <div className="mt-3">
                <p className="text-xs font-medium text-gray-700 mb-1">Interpretation:</p>
                <p className="text-xs text-gray-600">{info.range}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Raw Data Table */}
      {hasSpectralData && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Statistical Summary</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Index</th>
                  <th className="text-right py-2">Mean</th>
                  <th className="text-right py-2">Median</th>
                  <th className="text-right py-2">Std Dev</th>
                  <th className="text-right py-2">Min</th>
                  <th className="text-right py-2">Max</th>
                  <th className="text-right py-2">Count</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(spectralData.indices_stats).map(([indexName, stats]) => (
                  <tr key={indexName} className="border-b hover:bg-gray-50">
                    <td className="py-2 font-medium">{indexName}</td>
                    <td className="py-2 text-right">{stats.mean.toFixed(3)}</td>
                    <td className="py-2 text-right">{stats.median.toFixed(3)}</td>
                    <td className="py-2 text-right">{stats.std.toFixed(3)}</td>
                    <td className="py-2 text-right">{stats.min.toFixed(3)}</td>
                    <td className="py-2 text-right">{stats.max.toFixed(3)}</td>
                    <td className="py-2 text-right">{stats.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );

  if (!spectralData) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <div className="text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 11-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4zm9 1a1 1 0 010-2h4a1 1 0 011 1v4a1 1 0 01-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13.586 5H12zm-9 7a1 1 0 012 0v1.586l2.293-2.293a1 1 0 111.414 1.414L6.414 15H8a1 1 0 010 2H4a1 1 0 01-1-1v-4zm13-1a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 010-2h1.586l-2.293-2.293a1 1 0 111.414-1.414L15 13.586V12a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Spectral Data Available</h3>
          <p className="text-gray-600">Upload satellite data with multiple bands to see comprehensive spectral analysis.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
        {[
          { key: 'overview', label: 'Overview', icon: '📊' },
          { key: 'charts', label: 'Charts', icon: '📈' },
          { key: 'technical', label: 'Technical', icon: '🔬' }
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 flex items-center justify-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'charts' && renderChartsTab()}
        {activeTab === 'technical' && renderTechnicalTab()}
      </div>
    </div>
  );
};

export default SpectralAnalysis;
