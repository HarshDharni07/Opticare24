/**
 * Utility Functions
 * Purpose: Common helper functions used throughout the OptiCare24 application
 * Reference: PROMPT.md → Various modules requiring shared functionality
 */

import { format, parseISO } from 'date-fns';

/**
 * Format a date string to a human-readable format
 * @param {string} dateString - ISO date string
 * @param {string} formatString - Format pattern (default: 'MMM dd, yyyy')
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString, formatString = 'MMM dd, yyyy') => {
  if (!dateString) return '';
  try {
    return format(parseISO(dateString), formatString);
  } catch (error) {
    console.error('Date formatting error:', error);
    return dateString;
  }
};

/**
 * Format currency values
 * @param {number} amount - Amount to format
 * @param {string} currency - Currency code (default: 'USD')
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount, currency = 'USD') => {
  if (amount === null || amount === undefined) return '';
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2
  }).format(amount);
};

/**
 * Generate a random hex color
 * @returns {string} Hex color code
 */
export const getRandomColor = () => {
  return '#' + Math.floor(Math.random() * 16777215).toString(16);
};

/**
 * Convert role name to display name
 * @param {string} role - Role code from backend
 * @returns {string} Human-readable role name
 */
export const getRoleDisplayName = (role) => {
  const roleMap = {
    'admin': 'Administrator',
    'manager': 'Manager',
    'staff': 'Staff Member',
    'optometrist': 'Optometrist',
    'customer': 'Customer'
  };
  
  return roleMap[role] || role;
};

/**
 * Truncate text with ellipsis if too long
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length before truncation
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
};

/**
 * Extract error message from API error response
 * @param {Error} error - Error object from API call
 * @returns {string} Error message
 */
export const getErrorMessage = (error) => {
  return error.response?.data?.detail || 
         error.response?.data?.message ||
         error.message || 
         'An unexpected error occurred';
};