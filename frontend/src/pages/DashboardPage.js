import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Activity, TrendingUp, AlertTriangle } from 'lucide-react';
import FieldCard from '../components/FieldCard';
import { fieldsAPI, predictionsAPI } from '../services/api';
import toast from 'react-hot-toast';

const DashboardPage = () => {
  const [fields, setFields] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalFields: 0,
    goodHealth: 0,
    moderateHealth: 0,
    poorHealth: 0,
    recentAlerts: 0
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch fields and alerts in parallel
      const [fieldsResponse, alertsResponse] = await Promise.all([
        fieldsAPI.getAll(),
        predictionsAPI.getAlerts()
      ]);

      const fieldsData = fieldsResponse.data.fields || [];
      const alertsData = alertsResponse.data.alerts || [];

      setFields(fieldsData);
      setAlerts(alertsData);

      // Calculate stats
      const stats = {
        totalFields: fieldsData.length,
        goodHealth: fieldsData.filter(f => f.status?.toLowerCase() === 'good').length,
        moderateHealth: fieldsData.filter(f => f.status?.toLowerCase() === 'moderate').length,
        poorHealth: fieldsData.filter(f => f.status?.toLowerCase() === 'poor').length,
        recentAlerts: alertsData.length
      };
      setStats(stats);

    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleEditField = (field) => {
    // Navigate to edit field page
    console.log('Edit field:', field);
    toast('Edit field functionality not implemented yet', { icon: 'ℹ️' });
  };

  const handleDeleteField = async (field) => {
    if (window.confirm(`Are you sure you want to delete field "${field.name}"?`)) {
      try {
        await fieldsAPI.delete(field.id);
        toast.success('Field deleted successfully');
        fetchData(); // Refresh data
      } catch (error) {
        console.error('Error deleting field:', error);
        toast.error('Failed to delete field');
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="px-4 sm:px-0">
          <div className="md:flex md:items-center md:justify-between">
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold leading-7 text-gray-900 dark:text-white sm:text-3xl sm:truncate">
                Dashboard
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Monitor and manage your crop fields with AI-powered insights
              </p>
            </div>
            <div className="mt-4 flex md:mt-0 md:ml-4">
              <Link
                to="/add-field"
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <Plus size={20} className="mr-2" />
                Add Field
              </Link>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="mt-8 px-4 sm:px-0">
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {/* Total Fields */}
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Activity className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        Total Fields
                      </dt>
                      <dd className="text-lg font-medium text-gray-900 dark:text-white">
                        {stats.totalFields}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Good Health */}
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <TrendingUp className="h-6 w-6 text-green-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        Good Health
                      </dt>
                      <dd className="text-lg font-medium text-green-600 dark:text-green-400">
                        {stats.goodHealth}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Moderate Health */}
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Activity className="h-6 w-6 text-yellow-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        Moderate Health
                      </dt>
                      <dd className="text-lg font-medium text-yellow-600 dark:text-yellow-400">
                        {stats.moderateHealth}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Poor Health */}
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <AlertTriangle className="h-6 w-6 text-red-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                        Need Attention
                      </dt>
                      <dd className="text-lg font-medium text-red-600 dark:text-red-400">
                        {stats.poorHealth}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Alerts */}
        {alerts.length > 0 && (
          <div className="mt-8 px-4 sm:px-0">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white mb-4">
                  Recent Alerts
                </h3>
                <div className="space-y-3">
                  {alerts.slice(0, 5).map((alert) => (
                    <div key={alert.id} className="flex items-center p-3 bg-red-50 dark:bg-red-900/20 rounded-md">
                      <AlertTriangle className="h-5 w-5 text-red-400 mr-3" />
                      <div className="flex-1">
                        <p className="text-sm text-gray-900 dark:text-white">
                          {alert.message}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          Field: {alert.field_name} • {alert.relative_time || 'Recently'}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Fields Grid */}
        <div className="mt-8 px-4 sm:px-0">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Your Fields
          </h2>
          
          {fields.length === 0 ? (
            <div className="text-center py-12">
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg border border-gray-200 dark:border-gray-700 p-8">
                <Activity className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No fields yet
                </h3>
                <p className="text-gray-500 dark:text-gray-400 mb-4">
                  Get started by adding your first crop field to monitor.
                </p>
                <Link
                  to="/add-field"
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700"
                >
                  <Plus size={20} className="mr-2" />
                  Add Your First Field
                </Link>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {fields.map((field) => (
                <FieldCard
                  key={field.id}
                  field={field}
                  onEdit={handleEditField}
                  onDelete={handleDeleteField}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
