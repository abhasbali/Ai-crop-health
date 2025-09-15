import { authAPI } from './api';
import toast from 'react-hot-toast';

class AuthService {
  constructor() {
    this.token = localStorage.getItem('token');
    this.user = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null;
  }

  // Login user
  async login(email, password) {
    try {
      const response = await authAPI.login(email, password);
      const { access_token, user } = response.data;
      
      // Store token and user data
      this.token = access_token;
      this.user = user;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      toast.success('Login successful!');
      return { success: true, user, token: access_token };
    } catch (error) {
      const message = error.response?.data?.error || 'Login failed';
      toast.error(message);
      return { success: false, error: message };
    }
  }

  // Register new user
  async signup(username, email, password) {
    try {
      const response = await authAPI.signup(username, email, password);
      const { access_token, user } = response.data;
      
      // Store token and user data
      this.token = access_token;
      this.user = user;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      toast.success('Account created successfully!');
      return { success: true, user, token: access_token };
    } catch (error) {
      const message = error.response?.data?.error || 'Signup failed';
      toast.error(message);
      return { success: false, error: message };
    }
  }

  // Logout user
  logout() {
    this.token = null;
    this.user = null;
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    toast.success('Logged out successfully');
    
    // Redirect to login page
    window.location.href = '/login';
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.token && !!this.user;
  }

  // Get current user
  getCurrentUser() {
    return this.user;
  }

  // Get current token
  getToken() {
    return this.token;
  }

  // Refresh user profile
  async refreshProfile() {
    try {
      if (!this.token) {
        return { success: false, error: 'No token available' };
      }

      const response = await authAPI.getProfile();
      const { user } = response.data;
      
      this.user = user;
      localStorage.setItem('user', JSON.stringify(user));
      
      return { success: true, user };
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to refresh profile';
      return { success: false, error: message };
    }
  }

  // Refresh access token
  async refreshToken() {
    try {
      if (!this.token) {
        return { success: false, error: 'No token to refresh' };
      }

      const response = await authAPI.refreshToken();
      const { access_token, user } = response.data;
      
      this.token = access_token;
      this.user = user;
      
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      return { success: true, token: access_token, user };
    } catch (error) {
      // Token refresh failed, logout user
      this.logout();
      return { success: false, error: 'Token refresh failed' };
    }
  }

  // Initialize auth service (check token validity on app start)
  async initialize() {
    if (this.token && this.user) {
      try {
        // Verify token is still valid by making a request
        await authAPI.getProfile();
        return { success: true, user: this.user };
      } catch (error) {
        // Token is invalid, clear it
        if (error.response?.status === 401) {
          this.logout();
          return { success: false, error: 'Token expired' };
        }
        // Other errors, assume token is still valid
        return { success: true, user: this.user };
      }
    }
    
    return { success: false, error: 'No authentication data' };
  }

  // Format user display name
  getUserDisplayName() {
    if (!this.user) return 'Anonymous';
    return this.user.username || this.user.email || 'User';
  }

  // Check if user has specific role/permission (future use)
  hasPermission(permission) {
    // For now, all authenticated users have all permissions
    return this.isAuthenticated();
  }

  // Get user initials for avatar
  getUserInitials() {
    if (!this.user) return 'U';
    const name = this.user.username || this.user.email;
    return name.charAt(0).toUpperCase();
  }
}

// Create singleton instance
const authService = new AuthService();

export default authService;
