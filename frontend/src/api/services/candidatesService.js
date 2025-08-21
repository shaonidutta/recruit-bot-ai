import { apiClient } from '../client.js';
import { ENDPOINTS } from '../endpoints.js';

export const candidatesService = {
  /**
   * Get all candidates with optional pagination and filtering
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number (optional)
   * @param {number} params.limit - Items per page (optional)
   * @param {string} params.search - Search query (optional)
   * @param {string} params.location - Location filter (optional)
   * @param {string} params.skills - Skills filter (optional)
   * @param {string} params.experience - Experience level filter (optional)
   * @returns {Promise} API response
   */
  async getAllCandidates(params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.CANDIDATES.LIST, {
        params
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching candidates:', error);
      throw error;
    }
  },

  /**
   * Get a single candidate by ID
   * @param {string} id - Candidate ID
   * @returns {Promise} API response
   */
  async getCandidateById(id) {
    try {
      const response = await apiClient.get(ENDPOINTS.CANDIDATES.GET(id));
      return response.data;
    } catch (error) {
      console.error('Error fetching candidate:', error);
      throw error;
    }
  },

  /**
   * Create a new candidate
   * @param {Object} candidateData - Candidate data
   * @returns {Promise} API response
   */
  async createCandidate(candidateData) {
    try {
      const response = await apiClient.post(ENDPOINTS.CANDIDATES.CREATE, candidateData);
      return response.data;
    } catch (error) {
      console.error('Error creating candidate:', error);
      throw error;
    }
  },

  /**
   * Update an existing candidate
   * @param {string} id - Candidate ID
   * @param {Object} candidateData - Updated candidate data
   * @returns {Promise} API response
   */
  async updateCandidate(id, candidateData) {
    try {
      const response = await apiClient.put(ENDPOINTS.CANDIDATES.UPDATE(id), candidateData);
      return response.data;
    } catch (error) {
      console.error('Error updating candidate:', error);
      throw error;
    }
  },

  /**
   * Delete a candidate
   * @param {string} id - Candidate ID
   * @returns {Promise} API response
   */
  async deleteCandidate(id) {
    try {
      const response = await apiClient.delete(ENDPOINTS.CANDIDATES.DELETE(id));
      return response.data;
    } catch (error) {
      console.error('Error deleting candidate:', error);
      throw error;
    }
  },

  /**
   * Export candidates data
   * @param {Object} filters - Current filters applied
   * @returns {Promise} API response
   */
  async exportCandidates(filters = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.CANDIDATES.LIST, {
        params: { ...filters, export: true },
        responseType: 'blob'
      });
      return response;
    } catch (error) {
      console.error('Error exporting candidates:', error);
      throw error;
    }
  }
};