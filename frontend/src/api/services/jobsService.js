import { apiClient } from '../client.js';
import { ENDPOINTS } from '../endpoints.js';

export const jobsService = {
  /**
   * Get all jobs with optional pagination and filtering
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number (optional)
   * @param {number} params.limit - Items per page (optional)
   * @param {string} params.search - Search query (optional)
   * @param {string} params.location - Location filter (optional)
   * @param {string} params.company - Company filter (optional)
   * @param {string} params.jobType - Job type filter (optional)
   * @returns {Promise} API response
   */
  async getAllJobs(params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.JOBS.LIST, {
        params
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching jobs:', error);
      throw error;
    }
  },

  /**
   * Get a single job by ID
   * @param {string} id - Job ID
   * @returns {Promise} API response
   */
  async getJobById(id) {
    try {
      const response = await apiClient.get(ENDPOINTS.JOBS.GET(id));
      return response.data;
    } catch (error) {
      console.error('Error fetching job:', error);
      throw error;
    }
  },

  /**
   * Create a new job
   * @param {Object} jobData - Job data
   * @returns {Promise} API response
   */
  async createJob(jobData) {
    try {
      const response = await apiClient.post(ENDPOINTS.JOBS.CREATE, jobData);
      return response.data;
    } catch (error) {
      console.error('Error creating job:', error);
      throw error;
    }
  },

  /**
   * Update an existing job
   * @param {string} id - Job ID
   * @param {Object} jobData - Updated job data
   * @returns {Promise} API response
   */
  async updateJob(id, jobData) {
    try {
      const response = await apiClient.put(ENDPOINTS.JOBS.UPDATE(id), jobData);
      return response.data;
    } catch (error) {
      console.error('Error updating job:', error);
      throw error;
    }
  },

  /**
   * Delete a job
   * @param {string} id - Job ID
   * @returns {Promise} API response
   */
  async deleteJob(id) {
    try {
      const response = await apiClient.delete(ENDPOINTS.JOBS.DELETE(id));
      return response.data;
    } catch (error) {
      console.error('Error deleting job:', error);
      throw error;
    }
  }
};

export default jobsService;