/**
 * API Service Module
 * Purpose: Centralized API communication layer using Axios
 * Handles authentication headers and common response handling
 * Reference: PROMPT.md → Frontend ↔ Backend communication
 */

import axios from 'axios';

// Base API URL - will be configured based on environment
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle common errors (401, 403, etc.)
    const { status } = error.response || {};
    
    if (status === 401) {
      // Unauthorized - clear auth and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// API service object with methods for common operations
const apiService = {
  // Auth endpoints
  login: (credentials) => apiClient.post('/auth/login/', credentials),
  register: (userData) => apiClient.post('/auth/register/', userData),
  getCurrentUser: () => apiClient.get('/auth/me/'),
  
  // Generic CRUD methods that can be used for any resource
  getAll: (resource) => apiClient.get(`/${resource}/`),
  getById: (resource, id) => apiClient.get(`/${resource}/${id}/`),
  create: (resource, data) => apiClient.post(`/${resource}/`, data),
  update: (resource, id, data) => apiClient.put(`/${resource}/${id}/`, data),
  partialUpdate: (resource, id, data) => apiClient.patch(`/${resource}/${id}/`, data),
  delete: (resource, id) => apiClient.delete(`/${resource}/${id}/`),
};

export default apiService;