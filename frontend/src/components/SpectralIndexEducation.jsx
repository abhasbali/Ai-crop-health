import React, { useState } from 'react';
import { X, ChevronDown, ChevronUp, GraduationCap, Leaf, Droplet, Mountain, Info } from 'lucide-react';

const SpectralIndexEducation = ({ open, onClose, selectedIndex = null }) => {
  const [expandedSection, setExpandedSection] = useState(null);

  const spectralIndices = {
    ndvi: {
      name: 'NDVI (Normalized Difference Vegetation Index)',
      icon: <Leaf className="text-green-600" />,
      formula: '(NIR - Red) / (NIR + Red)',
      description: 'The most widely used vegetation index that measures photosynthetic activity and biomass.',
      ranges: [
        { range: '< 0.1', meaning: 'Bare soil, water, snow', color: '#8B4513' },
        { range: '0.1 - 0.2', meaning: 'Sparse vegetation', color: '#DEB887' },
        { range: '0.2 - 0.4', meaning: 'Moderate vegetation', color: '#9ACD32' },
        { range: '0.4 - 0.7', meaning: 'Dense vegetation', color: '#32CD32' },
        { range: '> 0.7', meaning: 'Very dense vegetation', color: '#006400' }
      ]
    },
    ndwi: {
      name: 'NDWI (Normalized Difference Water Index)',
      icon: <Droplet className="text-blue-600" />,
      formula: '(Green - NIR) / (Green + NIR)',
      description: 'Measures water content in vegetation and identifies water bodies.',
      ranges: [
        { range: '< -0.3', meaning: 'Dry soil/vegetation', color: '#8B4513' },
        { range: '-0.3 - 0', meaning: 'Moderate water stress', color: '#DEB887' },
        { range: '0 - 0.3', meaning: 'Adequate water content', color: '#87CEEB' },
        { range: '0.3 - 0.7', meaning: 'High water content', color: '#4682B4' },
        { range: '> 0.7', meaning: 'Water bodies', color: '#191970' }
      ]
    },
    ndsi: {
      name: 'NDSI (Normalized Difference Soil Index)',
      icon: <Mountain className="text-orange-600" />,
      formula: '(SWIR1 - SWIR2) / (SWIR1 + SWIR2)',
      description: 'Identifies bare soil and assesses soil moisture and mineral content.',
      ranges: [
        { range: '< 0', meaning: 'Clay-rich soils', color: '#CD853F' },
        { range: '0 - 0.2', meaning: 'Loamy soils', color: '#DEB887' },
        { range: '0.2 - 0.4', meaning: 'Sandy soils', color: '#F4A460' },
        { range: '0.4 - 0.6', meaning: 'Very sandy/rocky', color: '#D2691E' },
        { range: '> 0.6', meaning: 'Exposed minerals', color: '#A0522D' }
      ]
    }
  };

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative min-h-screen flex items-center justify-center p-4">
        <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
          
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <GraduationCap className="mr-2 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Spectral Index Education
              </h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X size={24} />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[70vh]">
            
            {/* Introduction */}
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-6">
              <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-200 mb-2">
                Understanding Spectral Indices
              </h3>
              <p className="text-blue-800 dark:text-blue-300 text-sm">
                Spectral indices are mathematical combinations of reflectance values from different 
                wavelengths of light. They help us understand plant health, water content, soil 
                properties, and environmental stress by analyzing how plants and surfaces reflect 
                different types of light.
              </p>
            </div>

            {/* Spectral Indices */}
            <div className="space-y-4">
              {Object.entries(spectralIndices).map(([indexKey, data]) => (
                <div key={indexKey} className="border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="p-4">
                    <div className="flex items-center mb-3">
                      {data.icon}
                      <h4 className="ml-2 text-lg font-semibold text-gray-900 dark:text-white">
                        {data.name}
                      </h4>
                    </div>
                    
                    <p className="text-gray-700 dark:text-gray-300 mb-3">
                      {data.description}
                    </p>
                    
                    <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded mb-3">
                      <p className="text-sm font-medium text-blue-900 dark:text-blue-200">
                        <strong>Formula:</strong> {data.formula}
                      </p>
                    </div>

                    <button
                      onClick={() => toggleSection(indexKey)}
                      className="flex items-center text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                    >
                      <span>Value Interpretation</span>
                      {expandedSection === indexKey ? 
                        <ChevronUp size={16} className="ml-1" /> : 
                        <ChevronDown size={16} className="ml-1" />
                      }
                    </button>

                    {expandedSection === indexKey && (
                      <div className="mt-3 overflow-x-auto">
                        <table className="min-w-full text-sm">
                          <thead>
                            <tr className="border-b border-gray-200 dark:border-gray-700">
                              <th className="text-left py-2 px-3 font-medium text-gray-900 dark:text-white">Range</th>
                              <th className="text-left py-2 px-3 font-medium text-gray-900 dark:text-white">Meaning</th>
                              <th className="text-left py-2 px-3 font-medium text-gray-900 dark:text-white">Color</th>
                            </tr>
                          </thead>
                          <tbody>
                            {data.ranges.map((range, idx) => (
                              <tr key={idx} className="border-b border-gray-100 dark:border-gray-800">
                                <td className="py-2 px-3 text-gray-700 dark:text-gray-300">{range.range}</td>
                                <td className="py-2 px-3 text-gray-700 dark:text-gray-300">{range.meaning}</td>
                                <td className="py-2 px-3">
                                  <div
                                    className="w-8 h-4 rounded border"
                                    style={{ backgroundColor: range.color }}
                                  ></div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Pest Detection Info */}
            <div className="mt-6 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
              <div className="flex items-center mb-2">
                <Info className="text-yellow-600 mr-2" />
                <h4 className="text-lg font-semibold text-yellow-900 dark:text-yellow-200">
                  How Spectral Analysis Detects Pest Problems
                </h4>
              </div>
              <p className="text-yellow-800 dark:text-yellow-300 text-sm mb-3">
                Pest damage causes changes in plant physiology that can be detected through 
                spectral analysis. By monitoring these changes alongside environmental conditions, 
                we can assess pest risk and recommend preventive measures.
              </p>
              <ul className="text-sm text-yellow-800 dark:text-yellow-300 space-y-1">
                <li>• Reduced NDVI values indicate stressed or damaged vegetation</li>
                <li>• Unusual NDWI patterns suggest water stress from pest damage</li>
                <li>• Environmental factors like temperature and humidity affect pest activity</li>
                <li>• Early detection allows for timely intervention and treatment</li>
              </ul>
            </div>

            {/* Best Practices */}
            <div className="mt-6 bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <h4 className="text-lg font-semibold text-green-900 dark:text-green-200 mb-3">
                Best Practices for Analysis
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h5 className="font-medium text-green-800 dark:text-green-300 mb-2">Data Collection:</h5>
                  <ul className="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <li>• Collect data during optimal lighting conditions</li>
                    <li>• Account for atmospheric effects</li>
                    <li>• Consider seasonal variations</li>
                    <li>• Validate with ground truth measurements</li>
                  </ul>
                </div>
                <div>
                  <h5 className="font-medium text-green-800 dark:text-green-300 mb-2">Analysis Guidelines:</h5>
                  <ul className="text-sm text-green-700 dark:text-green-400 space-y-1">
                    <li>• Use multiple indices for comprehensive assessment</li>
                    <li>• Consider crop type and growth stage</li>
                    <li>• Monitor temporal changes, not just snapshots</li>
                    <li>• Integrate with weather and management data</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4">
            <button
              onClick={onClose}
              className="w-full sm:w-auto px-4 py-2 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SpectralIndexEducation;
