/**
 * Date utility functions
 * Lightweight alternatives to date-fns for basic date formatting
 */

/**
 * Format a date to show time ago (e.g., "2 hours ago", "3 days ago")
 * @param {Date|string} date - The date to format
 * @returns {string} - Formatted time ago string
 */
export const formatTimeAgo = (date) => {
  if (!date) return '';
  
  const now = new Date();
  const targetDate = new Date(date);
  const diffInSeconds = Math.floor((now - targetDate) / 1000);
  
  if (diffInSeconds < 60) {
    return 'just now';
  }
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) {
    return `${diffInMinutes} minute${diffInMinutes === 1 ? '' : 's'} ago`;
  }
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) {
    return `${diffInHours} hour${diffInHours === 1 ? '' : 's'} ago`;
  }
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) {
    return `${diffInDays} day${diffInDays === 1 ? '' : 's'} ago`;
  }
  
  const diffInWeeks = Math.floor(diffInDays / 7);
  if (diffInWeeks < 4) {
    return `${diffInWeeks} week${diffInWeeks === 1 ? '' : 's'} ago`;
  }
  
  const diffInMonths = Math.floor(diffInDays / 30);
  if (diffInMonths < 12) {
    return `${diffInMonths} month${diffInMonths === 1 ? '' : 's'} ago`;
  }
  
  const diffInYears = Math.floor(diffInDays / 365);
  return `${diffInYears} year${diffInYears === 1 ? '' : 's'} ago`;
};

/**
 * Format a date to a readable string (e.g., "Jan 15, 2024")
 * @param {Date|string} date - The date to format
 * @returns {string} - Formatted date string
 */
export const formatDate = (date) => {
  if (!date) return '';
  
  const targetDate = new Date(date);
  return targetDate.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

/**
 * Format a date to include time (e.g., "Jan 15, 2024 at 2:30 PM")
 * @param {Date|string} date - The date to format
 * @returns {string} - Formatted date and time string
 */
export const formatDateTime = (date) => {
  if (!date) return '';
  
  const targetDate = new Date(date);
  return targetDate.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
};

/**
 * Check if a date is today
 * @param {Date|string} date - The date to check
 * @returns {boolean} - True if the date is today
 */
export const isToday = (date) => {
  if (!date) return false;
  
  const today = new Date();
  const targetDate = new Date(date);
  
  return today.toDateString() === targetDate.toDateString();
};

/**
 * Check if a date is within the last N days
 * @param {Date|string} date - The date to check
 * @param {number} days - Number of days to check within
 * @returns {boolean} - True if the date is within the last N days
 */
export const isWithinDays = (date, days) => {
  if (!date) return false;
  
  const now = new Date();
  const targetDate = new Date(date);
  const diffInDays = Math.floor((now - targetDate) / (1000 * 60 * 60 * 24));
  
  return diffInDays <= days;
};

/**
 * Get relative time with more detailed breakdown
 * @param {Date|string} date - The date to format
 * @returns {object} - Object with time breakdown
 */
export const getTimeBreakdown = (date) => {
  if (!date) return null;
  
  const now = new Date();
  const targetDate = new Date(date);
  const diffInSeconds = Math.floor((now - targetDate) / 1000);
  
  return {
    seconds: diffInSeconds,
    minutes: Math.floor(diffInSeconds / 60),
    hours: Math.floor(diffInSeconds / 3600),
    days: Math.floor(diffInSeconds / 86400),
    weeks: Math.floor(diffInSeconds / 604800),
    months: Math.floor(diffInSeconds / 2592000),
    years: Math.floor(diffInSeconds / 31536000)
  };
};

export default {
  formatTimeAgo,
  formatDate,
  formatDateTime,
  isToday,
  isWithinDays,
  getTimeBreakdown
};
