import { apiClient } from '../client.js';
import { ENDPOINTS } from '../endpoints.js';
import { handleApiError } from '../errorHandler.js';

export const healthService = {
  // Get basic health status
  getBasicHealth: async () => {
    try {
      const response = await apiClient.get(ENDPOINTS.HEALTH.BASIC);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Get database health status
  getDatabaseHealth: async () => {
    try {
      const response = await apiClient.get(ENDPOINTS.HEALTH.DATABASE);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Get detailed health status
  getDetailedHealth: async () => {
    try {
      const response = await apiClient.get(ENDPOINTS.HEALTH.DETAILED);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Check if system is healthy
  isSystemHealthy: async () => {
    try {
      const response = await healthService.getDetailedHealth();
      return response.data && 
             response.data.service?.status === 'healthy' && 
             response.data.database?.status === 'connected';
    } catch (error) {
      return false;
    }
  }
};
