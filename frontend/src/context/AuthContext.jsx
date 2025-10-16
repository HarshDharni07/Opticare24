/**
 * Authentication Context Provider
 * Purpose: Manages global authentication state and user role information
 * Provides login/logout functions to all components
 * Reference: PROMPT.md → Authentication & User Roles section
 */

import { createContext, useState, useEffect, useContext } from 'react';
import apiService from '../api/apiService';

// Create the auth context
export const AuthContext = createContext(null);

// Custom hook for using the auth context
export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [userRole, setUserRole] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('token');
      
      if (!token) {
        setIsLoading(false);
        return;
      }
      
      try {
        const response = await apiService.getCurrentUser();
        setCurrentUser(response.data);
        setUserRole(response.data.role);
      } catch (err) {
        console.error('Auth check failed:', err);
        localStorage.removeItem('token');
        setError('Authentication session expired');
      } finally {
        setIsLoading(false);
      }
    };
    
    checkAuthStatus();
  }, []);

  // Login function
  const login = async (credentials) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.login(credentials);
      const { token, user } = response.data;
      
      // Store token and user data
      localStorage.setItem('token', token);
      setCurrentUser(user);
      setUserRole(user.role);
      
      return user;
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    setCurrentUser(null);
    setUserRole(null);
  };

  // Register function
  const register = async (userData) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.register(userData);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  // Auth context value
  const value = {
    currentUser,
    userRole,
    isAuthenticated: !!currentUser,
    isLoading,
    error,
    login,
    logout,
    register
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};