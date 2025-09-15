import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, Crop, Hash, Save, ArrowLeft } from 'lucide-react';
import { fieldsAPI } from '../services/api';
import toast from 'react-hot-toast';

const AddField = () => {
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    latitude: '',
    longitude: '',
    area_hectares: '',
    crop_type: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name) {
      toast.error('Field name is required');
      return;
    }

    setIsLoading(true);
    
    try {
      // Convert numeric fields
      const fieldData = {
        ...formData,
        latitude: formData.latitude ? parseFloat(formData.latitude) : null,
        longitude: formData.longitude ? parseFloat(formData.longitude) : null,
        area_hectares: formData.area_hectares ? parseFloat(formData.area_hectares) : null
      };

      await fieldsAPI.create(fieldData);
      toast.success('Field created successfully');
      navigate('/dashboard');
    } catch (error) {
      console.error('Error creating field:', error);
      console.error('Error response:', error.response);
      console.error('Error status:', error.response?.status);
      console.error('Error data:', error.response?.data);
      
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          error.message || 
                          'Failed to create field';
      
      toast.error(`Failed to create field: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="max-w-3xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 sm:px-0">
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 mb-4"
          >
            <ArrowLeft size={16} className="mr-1" />
            Back to Dashboard
          </button>
          
          <h1 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl">
            Add New Field
          </h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Create a new crop field to start monitoring its health with AI
          </p>
        </div>

        {/* Form */}
        <div className="mt-8 px-4 sm:px-0">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
            <form onSubmit={handleSubmit} className="space-y-6 px-6 py-8">
              {/* Field Name */}
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Field Name *
                </label>
                <div className="relative">
                  <input
                    type="text"
                    name="name"
                    id="name"
                    required
                    value={formData.name}
                    onChange={handleChange}
                    className="block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Enter field name (e.g., North Field, Wheat Plot A)"
                  />
                </div>
              </div>

              {/* Location */}
              <div>
                <label htmlFor="location" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Location
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <MapPin size={20} className="text-gray-400" />
                  </div>
                  <input
                    type="text"
                    name="location"
                    id="location"
                    value={formData.location}
                    onChange={handleChange}
                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Enter location (e.g., Farm Section 3, Iowa, USA)"
                  />
                </div>
              </div>

              {/* Coordinates */}
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label htmlFor="latitude" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Latitude
                  </label>
                  <input
                    type="number"
                    name="latitude"
                    id="latitude"
                    step="0.000001"
                    value={formData.latitude}
                    onChange={handleChange}
                    className="block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="e.g., 41.8781"
                  />
                </div>
                
                <div>
                  <label htmlFor="longitude" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Longitude
                  </label>
                  <input
                    type="number"
                    name="longitude"
                    id="longitude"
                    step="0.000001"
                    value={formData.longitude}
                    onChange={handleChange}
                    className="block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    placeholder="e.g., -87.6298"
                  />
                </div>
              </div>

              {/* Area and Crop Type */}
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label htmlFor="area_hectares" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Area (Hectares)
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Hash size={20} className="text-gray-400" />
                    </div>
                    <input
                      type="number"
                      name="area_hectares"
                      id="area_hectares"
                      step="0.01"
                      value={formData.area_hectares}
                      onChange={handleChange}
                      className="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      placeholder="e.g., 10.5"
                    />
                  </div>
                </div>
                
                <div>
                  <label htmlFor="crop_type" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Crop Type
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Crop size={20} className="text-gray-400" />
                    </div>
                    <select
                      name="crop_type"
                      id="crop_type"
                      value={formData.crop_type}
                      onChange={handleChange}
                      className="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                    >
                      <option value="">Select crop type</option>
                      <option value="wheat">Wheat</option>
                      <option value="corn">Corn</option>
                      <option value="soybean">Soybean</option>
                      <option value="rice">Rice</option>
                      <option value="barley">Barley</option>
                      <option value="cotton">Cotton</option>
                      <option value="potato">Potato</option>
                      <option value="tomato">Tomato</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => navigate('/dashboard')}
                    className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Creating...
                      </>
                    ) : (
                      <>
                        <Save size={16} className="mr-2" />
                        Create Field
                      </>
                    )}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddField;
