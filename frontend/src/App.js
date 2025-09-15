import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import authService from './services/auth';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import Signup from './pages/Signup';
import DashboardPage from './pages/DashboardPage';
import AddField from './pages/AddField';
import FieldDetails from './components/FieldDetails';
import SpectralAnalysisPage from './pages/SpectralAnalysisPage';
import './index.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = authService.isAuthenticated();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Public Route Component (redirect to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const isAuthenticated = authService.isAuthenticated();
  return !isAuthenticated ? children : <Navigate to="/dashboard" replace />;
};

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      const result = await authService.initialize();
      setIsAuthenticated(result.success);
    } catch (error) {
      console.error('Auth initialization error:', error);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              theme: {
                primary: '#4ade80',
                secondary: '#black',
              },
            },
            error: {
              duration: 5000,
              theme: {
                primary: '#ef4444',
                secondary: '#black',
              },
            },
          }}
        />
        
        {isAuthenticated && <Navbar />}
        
        <main className={isAuthenticated ? 'pt-0' : ''}>
          <Routes>
            {/* Public Routes */}
            <Route
              path="/login"
              element={
                <PublicRoute>
                  <Login />
                </PublicRoute>
              }
            />
            <Route
              path="/signup"
              element={
                <PublicRoute>
                  <Signup />
                </PublicRoute>
              }
            />

            {/* Protected Routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/add-field"
              element={
                <ProtectedRoute>
                  <AddField />
                </ProtectedRoute>
              }
            />
            <Route
              path="/field/:id"
              element={
                <ProtectedRoute>
                  <FieldDetails />
                </ProtectedRoute>
              }
            />
            <Route
              path="/spectral-analysis"
              element={
                <ProtectedRoute>
                  <SpectralAnalysisPage />
                </ProtectedRoute>
              }
            />

            {/* Default redirect */}
            <Route
              path="/"
              element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />}
            />
            
            {/* Catch all route */}
            <Route
              path="*"
              element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />}
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
