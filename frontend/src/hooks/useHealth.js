import { useState, useEffect, useCallback } from 'react';
import { healthService } from '../api/services/healthService.js';

export const useHealth = () => {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isHealthy, setIsHealthy] = useState(false);

  // Fetch detailed health status
  const fetchHealth = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await healthService.getDetailedHealth();
      
      if (response.success && response.data) {
        setHealth(response.data);
        
        // Determine if system is healthy
        const systemHealthy = response.data.service?.status === 'healthy' && 
                             response.data.database?.status === 'connected';
        setIsHealthy(systemHealthy);
      } else {
        setHealth(null);
        setIsHealthy(false);
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch health status');
      setHealth(null);
      setIsHealthy(false);
      console.error('Error fetching health status:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Check basic health
  const checkBasicHealth = useCallback(async () => {
    try {
      const response = await healthService.getBasicHealth();
      return response.success;
    } catch (err) {
      console.error('Error checking basic health:', err);
      return false;
    }
  }, []);

  // Check database health
  const checkDatabaseHealth = useCallback(async () => {
    try {
      const response = await healthService.getDatabaseHealth();
      return response.success && response.data?.status === 'connected';
    } catch (err) {
      console.error('Error checking database health:', err);
      return false;
    }
  }, []);

  // Get health status summary
  const getHealthSummary = useCallback(() => {
    if (!health) return null;
    
    return {
      overall: isHealthy ? 'healthy' : 'unhealthy',
      service: health.service?.status || 'unknown',
      database: health.database?.status || 'unknown',
      uptime: health.service?.uptime || 'unknown',
      timestamp: health.timestamp || new Date().toISOString()
    };
  }, [health, isHealthy]);

  // Initial health check and periodic updates
  useEffect(() => {
    fetchHealth();
    
    // Refresh health status every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    
    return () => clearInterval(interval);
  }, [fetchHealth]);

  return {
    health,
    loading,
    error,
    isHealthy,
    fetchHealth,
    checkBasicHealth,
    checkDatabaseHealth,
    getHealthSummary,
    refetch: fetchHealth
  };
};
