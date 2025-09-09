import React, { useState, useEffect } from 'react';

/**
 * Animated counter component that smoothly transitions between numbers
 * @param {number} value - Target value to animate to
 * @param {number} duration - Animation duration in milliseconds (default: 1000)
 * @param {Function} formatter - Optional formatter function for the display value
 * @param {string} className - Additional CSS classes
 */
export const AnimatedCounter = ({ 
  value, 
  duration = 1000, 
  formatter = (val) => val.toLocaleString(),
  className = ""
}) => {
  const [displayValue, setDisplayValue] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (value === displayValue) return;

    setIsAnimating(true);
    const startValue = displayValue;
    const difference = value - startValue;
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function for smooth animation
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      const currentValue = Math.round(startValue + (difference * easeOutCubic));
      
      setDisplayValue(currentValue);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setIsAnimating(false);
      }
    };

    requestAnimationFrame(animate);
  }, [value, duration, displayValue]);

  return (
    <span className={`${className} ${isAnimating ? 'text-blue-600' : ''} transition-colors duration-300`}>
      {formatter(displayValue)}
    </span>
  );
};

/**
 * Growth indicator component showing percentage change
 * @param {number} current - Current value
 * @param {number} previous - Previous value
 * @param {boolean} showIcon - Whether to show trend icon
 * @param {string} className - Additional CSS classes
 */
export const GrowthIndicator = ({ 
  current, 
  previous, 
  showIcon = true, 
  className = "" 
}) => {
  if (!previous || previous === 0) return null;

  const growth = ((current - previous) / previous) * 100;
  const isPositive = growth > 0;
  const isNeutral = growth === 0;

  if (isNeutral) return null;

  const formatGrowth = (value) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  return (
    <div className={`flex items-center space-x-1 text-xs ${className}`}>
      {showIcon && (
        <span className={`${isPositive ? 'text-green-500' : 'text-red-500'}`}>
          {isPositive ? '↗' : '↘'}
        </span>
      )}
      <span className={`font-medium ${
        isPositive ? 'text-green-600' : 'text-red-600'
      }`}>
        {formatGrowth(growth)}
      </span>
    </div>
  );
};

/**
 * Live indicator showing update status
 * @param {boolean} isUpdating - Whether data is currently updating
 * @param {Date} lastUpdated - Last update timestamp
 * @param {string} className - Additional CSS classes
 */
export const LiveIndicator = ({ 
  isUpdating, 
  lastUpdated, 
  className = "" 
}) => {
  const formatTimeAgo = (date) => {
    if (!date) return 'Never';
    
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  return (
    <div className={`flex items-center space-x-2 text-xs text-gray-500 ${className}`}>
      <div className={`w-2 h-2 rounded-full ${
        isUpdating 
          ? 'bg-green-500 animate-pulse' 
          : 'bg-gray-300'
      }`} />
      <span>
        {isUpdating ? 'Updating...' : `Updated ${formatTimeAgo(lastUpdated)}`}
      </span>
    </div>
  );
};

/**
 * Progress bar component for workflow status
 * @param {number} progress - Progress percentage (0-100)
 * @param {string} status - Current status message
 * @param {boolean} animated - Whether to show animated stripes
 * @param {string} className - Additional CSS classes
 */
export const ProgressBar = ({ 
  progress, 
  status, 
  animated = false, 
  className = "" 
}) => {
  return (
    <div className={`w-full ${className}`}>
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-gray-700">{status}</span>
        <span className="text-sm text-gray-500">{Math.round(progress)}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${
            animated 
              ? 'bg-gradient-to-r from-blue-500 to-blue-600 bg-[length:20px_20px] animate-pulse' 
              : 'bg-blue-500'
          }`}
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>
    </div>
  );
};
