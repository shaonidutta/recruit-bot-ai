import { apiClient } from '../client.js';
import { ENDPOINTS } from '../endpoints.js';
import { handleApiError } from '../errorHandler.js';

export const matchService = {
  /**
   * Get all matches with filtering and pagination
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of matches to return (default: 10)
   * @param {number} params.skip - Number of matches to skip (default: 0)
   * @param {string} params.job_id - Filter by job ID (optional)
   * @param {string} params.candidate_id - Filter by candidate ID (optional)
   * @param {number} params.min_score - Minimum match score (optional)
   * @returns {Promise} API response
   */
  async getMatches(params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.MATCHES.LIST, {
        params: {
          limit: 10,
          skip: 0,
          ...params
        }
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Get recent matches from the last N hours
   * @param {number} limit - Number of recent matches to return (default: 10)
   * @param {number} hours - Look back this many hours (default: 24)
   * @returns {Promise} API response
   */
  async getRecentMatches(limit = 10, hours = 24) {
    try {
      const response = await apiClient.get(ENDPOINTS.MATCHES.RECENT, {
        params: { limit, hours }
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Get specific match by ID with full details
   * @param {string} matchId - Match ID
   * @returns {Promise} API response
   */
  async getMatchById(matchId) {
    try {
      const response = await apiClient.get(ENDPOINTS.MATCHES.BY_ID(matchId));
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Get all matches for a specific job
   * @param {string} jobId - Job ID
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of matches to return (default: 20)
   * @param {number} params.min_score - Minimum match score (optional)
   * @returns {Promise} API response
   */
  async getMatchesForJob(jobId, params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.MATCHES.FOR_JOB(jobId), {
        params: {
          limit: 20,
          ...params
        }
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Get all matches for a specific candidate
   * @param {string} candidateId - Candidate ID
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of matches to return (default: 20)
   * @param {number} params.min_score - Minimum match score (optional)
   * @returns {Promise} API response
   */
  async getMatchesForCandidate(candidateId, params = {}) {
    try {
      const response = await apiClient.get(ENDPOINTS.MATCHES.FOR_CANDIDATE(candidateId), {
        params: {
          limit: 20,
          ...params
        }
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Get match statistics and metrics
   * @returns {Promise} API response
   */
  async getMatchStats() {
    try {
      const response = await apiClient.get(ENDPOINTS.MATCHES.STATS);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Search matches with advanced filtering
   * @param {Object} filters - Search filters
   * @param {string} filters.job_title - Filter by job title (optional)
   * @param {string} filters.candidate_name - Filter by candidate name (optional)
   * @param {number} filters.min_score - Minimum match score (optional)
   * @param {number} filters.max_score - Maximum match score (optional)
   * @param {string} filters.date_from - Filter matches from this date (optional)
   * @param {string} filters.date_to - Filter matches to this date (optional)
   * @param {number} filters.limit - Number of results (default: 20)
   * @param {number} filters.skip - Number to skip (default: 0)
   * @returns {Promise} API response
   */
  async searchMatches(filters = {}) {
    try {
      const params = {
        limit: 20,
        skip: 0,
        ...filters
      };

      const response = await apiClient.get(ENDPOINTS.MATCHES.LIST, { params });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Get matches with high scores (above threshold)
   * @param {number} threshold - Minimum score threshold (default: 0.8)
   * @param {number} limit - Number of matches to return (default: 10)
   * @returns {Promise} API response
   */
  async getHighQualityMatches(threshold = 0.8, limit = 10) {
    try {
      const response = await apiClient.get(ENDPOINTS.MATCHES.LIST, {
        params: {
          min_score: threshold,
          limit,
          skip: 0
        }
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Get matches created today
   * @param {number} limit - Number of matches to return (default: 20)
   * @returns {Promise} API response
   */
  async getTodaysMatches(limit = 20) {
    try {
      const response = await apiClient.get(ENDPOINTS.MATCHES.RECENT, {
        params: {
          limit,
          hours: 24
        }
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  /**
   * Get match summary for dashboard
   * @returns {Promise} Combined match data for dashboard display
   */
  async getMatchSummary() {
    try {
      // Get both stats and recent matches in parallel
      const [statsResponse, recentResponse] = await Promise.all([
        this.getMatchStats(),
        this.getRecentMatches(5, 24)
      ]);

      return {
        success: true,
        data: {
          stats: statsResponse.success ? statsResponse.data : null,
          recent_matches: recentResponse.success ? recentResponse.data.matches : [],
          summary: {
            total_matches: statsResponse.success ? statsResponse.data.total_matches : 0,
            recent_count: recentResponse.success ? recentResponse.data.matches.length : 0,
            avg_score: statsResponse.success ? statsResponse.data.score_statistics?.average : 0
          }
        }
      };
    } catch (error) {
      throw handleApiError(error);
    }
  }
};

export default matchService;
