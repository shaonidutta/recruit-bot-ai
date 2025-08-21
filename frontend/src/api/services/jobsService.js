import { apiClient } from '../client.js';
import { ENDPOINTS } from '../endpoints.js';
import { handleApiError } from '../errorHandler.js';

export const jobsService = {
  // Get job statistics
  getStats: async () => {
    try {
      const response = await apiClient.get(ENDPOINTS.JOBS.STATS);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Get jobs list with pagination and search
  getJobs: async (params = {}) => {
    try {
      const response = await apiClient.get(ENDPOINTS.JOBS.LIST, { params });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Get job by ID
  getJobById: async (jobId) => {
    try {
      const response = await apiClient.get(ENDPOINTS.JOBS.BY_ID(jobId));
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Create new job
  createJob: async (jobData) => {
    try {
      const response = await apiClient.post(ENDPOINTS.JOBS.CREATE, jobData);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Update job
  updateJob: async (jobId, jobData) => {
    try {
      const response = await apiClient.put(ENDPOINTS.JOBS.UPDATE(jobId), jobData);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Search jobs with filters
  searchJobs: async (searchTerm, filters = {}) => {
    try {
      const params = {
        search: searchTerm,
        ...filters
      };
      const response = await apiClient.get(ENDPOINTS.JOBS.LIST, { params });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Get recent jobs from latest workflow run
  getRecentJobs: async (params = {}) => {
    try {
      const response = await apiClient.get(ENDPOINTS.JOBS.RECENT, { params });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
};
