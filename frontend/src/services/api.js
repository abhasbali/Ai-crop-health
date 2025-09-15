import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance with default config
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE || 'http://localhost:5000/api',
  timeout: 30000,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors globally
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle authentication errors
    if (error.response?.status === 401 || error.response?.status === 422) {
      // Token expired, invalid, or malformed
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
    
    // Handle other errors (but don't show toast for auth initialization errors)
    if (!error.config?.url?.includes('/auth/me')) {
      const message = error.response?.data?.error || error.message || 'An error occurred';
      toast.error(message);
    }
    
    return Promise.reject(error);
  }
);

// Auth API functions
export const authAPI = {
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
    
  signup: (username, email, password) =>
    api.post('/auth/signup', { username, email, password }),
    
  getProfile: () =>
    api.get('/auth/me'),
    
  refreshToken: () =>
    api.post('/auth/refresh'),
};

// Fields API functions
export const fieldsAPI = {
  getAll: () =>
    api.get('/fields'),
    
  create: (fieldData) =>
    api.post('/fields', fieldData),
    
  getById: (id) =>
    api.get(`/fields/${id}`),
    
  update: (id, fieldData) =>
    api.put(`/fields/${id}`, fieldData),
    
  delete: (id) =>
    api.delete(`/fields/${id}`),
};

// Predictions API functions
export const predictionsAPI = {
  uploadData: (formData) =>
    api.post('/predictions/upload-data', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),
    
  predict: (data) =>
    api.post('/predictions/predict', data),
    
  getAlerts: (unreadOnly = false) =>
    api.get('/predictions/alerts', {
      params: { unread_only: unreadOnly }
    }),
    
  getHistory: (fieldId) =>
    api.get(`/predictions/history/${fieldId}`),
    
  getModelInfo: () =>
    api.get('/predictions/model-info'),
    
  analyzeNDVI: (data) =>
    api.post('/predictions/ndvi-analysis', data),
    
  // Multi-spectral analysis
  multiSpectralAnalysis: (data) =>
    api.post('/predictions/multi-spectral-analysis', data),
    
  // Get spectral analysis for a field
  getSpectralAnalysis: (fieldId) =>
    api.get(`/predictions/spectral-analysis/${fieldId}`),
    
  // Hyperspectral visualization
  hyperspectralVisualization: (data) =>
    api.post('/predictions/hyperspectral-visualization', data),
    
  // Field health assessment
  fieldHealthAssessment: (fieldId) =>
    api.get(`/predictions/field-health-assessment/${fieldId}`),
};

// Utility functions
export const apiUtils = {
  // Handle file upload with progress
  uploadWithProgress: (formData, onProgress) => {
    return api.post('/predictions/upload-data', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        if (onProgress) {
          onProgress(progress);
        }
      },
    });
  },
  
  // Check API health
  healthCheck: () =>
    api.get('/health'),
    
  // Get app status
  getStatus: () =>
    api.get('/status'),
};

export default api;
