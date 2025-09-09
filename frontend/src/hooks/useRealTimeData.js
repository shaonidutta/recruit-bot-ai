import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * Custom hook for real-time data polling with cleanup and error handling
 * @param {Function} fetchFunction - Function that returns a promise with data
 * @param {number} interval - Polling interval in milliseconds (default: 30000)
 * @param {Object} options - Configuration options
 * @returns {Object} - { data, loading, error, lastUpdated, refetch, pause, resume }
 */
export const useRealTimeData = (fetchFunction, interval = 30000, options = {}) => {
  const [state, setState] = useState({
    data: null,
    loading: false,
    error: null,
    lastUpdated: null
  });

  const intervalRef = useRef(null);
  const mountedRef = useRef(true);
  const { enablePolling = true, dependencies = [] } = options;

  const fetchData = useCallback(async () => {
    if (!mountedRef.current) return;
    
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const result = await fetchFunction();
      if (mountedRef.current) {
        setState({
          data: result,
          loading: false,
          error: null,
          lastUpdated: new Date()
        });
      }
    } catch (error) {
      if (mountedRef.current) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: error.message || 'Failed to fetch data'
        }));
      }
    }
  }, [fetchFunction, ...dependencies]);

  const pause = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const resume = useCallback(() => {
    if (!intervalRef.current && enablePolling) {
      intervalRef.current = setInterval(fetchData, interval);
    }
  }, [fetchData, interval, enablePolling]);

  // Initial fetch and setup polling
  useEffect(() => {
    fetchData(); // Initial fetch
    
    if (enablePolling) {
      intervalRef.current = setInterval(fetchData, interval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchData, interval, enablePolling]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Pause polling when page is hidden (performance optimization)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        pause();
      } else {
        resume();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [pause, resume]);

  return {
    ...state,
    refetch: fetchData,
    pause,
    resume
  };
};

/**
 * Hook for adaptive polling that adjusts interval based on user activity
 * @param {Function} fetchFunction - Function that returns a promise with data
 * @param {number} baseInterval - Base polling interval
 * @param {Object} options - Configuration options
 * @returns {Object} - Same as useRealTimeData
 */
export const useAdaptivePolling = (fetchFunction, baseInterval = 30000, options = {}) => {
  const [interval, setInterval] = useState(baseInterval);
  
  useEffect(() => {
    const handleVisibilityChange = () => {
      // Slow down polling when page is hidden
      setInterval(document.hidden ? baseInterval * 4 : baseInterval);
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [baseInterval]);
  
  return useRealTimeData(fetchFunction, interval, options);
};
