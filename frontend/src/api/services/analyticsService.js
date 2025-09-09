/**
 * Analytics API Service
 * Handles all analytics-related API calls
 */

import { apiClient } from '../client';
import { ENDPOINTS } from '../endpoints';

export const analyticsService = {
  /**
   * Get dashboard analytics data
   * @param {number} days - Number of days to analyze (default: 7)
   * @returns {Promise<Object>} Dashboard analytics data
   */
  async getDashboardAnalytics(days = 7) {
    try {
      const response = await apiClient.get(`${ENDPOINTS.ANALYTICS.DASHBOARD}?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard analytics:', error);
      throw error;
    }
  },

  /**
   * Get trend analytics for specific metrics
   * @param {string} metric - Metric to analyze (jobs, matches, candidates)
   * @param {number} days - Number of days to analyze (default: 30)
   * @returns {Promise<Object>} Trend analytics data
   */
  async getTrendAnalytics(metric = 'jobs', days = 30) {
    try {
      const response = await apiClient.get(
        `${ENDPOINTS.ANALYTICS.TRENDS}?metric=${metric}&days=${days}`
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching trend analytics:', error);
      throw error;
    }
  },

  /**
   * Get performance metrics and KPIs
   * @returns {Promise<Object>} Performance metrics data
   */
  async getPerformanceMetrics() {
    try {
      const response = await apiClient.get(ENDPOINTS.ANALYTICS.PERFORMANCE);
      return response.data;
    } catch (error) {
      console.error('Error fetching performance metrics:', error);
      throw error;
    }
  },

  /**
   * Get job discovery trends
   * @param {number} days - Number of days to analyze
   * @returns {Promise<Object>} Job discovery trend data
   */
  async getJobTrends(days = 7) {
    try {
      const analytics = await this.getDashboardAnalytics(days);
      return {
        success: analytics.success,
        data: analytics.success ? analytics.data.job_trends : [],
        message: analytics.message
      };
    } catch (error) {
      console.error('Error fetching job trends:', error);
      throw error;
    }
  },

  /**
   * Get job source breakdown
   * @returns {Promise<Object>} Job source breakdown data
   */
  async getSourceBreakdown() {
    try {
      const analytics = await this.getDashboardAnalytics(30); // Use 30 days for source analysis
      return {
        success: analytics.success,
        data: analytics.success ? analytics.data.source_breakdown : [],
        message: analytics.message
      };
    } catch (error) {
      console.error('Error fetching source breakdown:', error);
      throw error;
    }
  },

  /**
   * Get workflow success rates
   * @returns {Promise<Object>} Workflow success rates data
   */
  async getWorkflowSuccess() {
    try {
      const analytics = await this.getDashboardAnalytics(30);
      return {
        success: analytics.success,
        data: analytics.success ? analytics.data.workflow_success : [],
        message: analytics.message
      };
    } catch (error) {
      console.error('Error fetching workflow success rates:', error);
      throw error;
    }
  },

  /**
   * Get email performance metrics
   * @returns {Promise<Object>} Email performance data
   */
  async getEmailPerformance() {
    try {
      const analytics = await this.getDashboardAnalytics(30);
      return {
        success: analytics.success,
        data: analytics.success ? analytics.data.email_performance : [],
        message: analytics.message
      };
    } catch (error) {
      console.error('Error fetching email performance:', error);
      throw error;
    }
  },

  /**
   * Get comprehensive analytics summary
   * @param {number} days - Number of days to analyze
   * @returns {Promise<Object>} Complete analytics summary
   */
  async getAnalyticsSummary(days = 7) {
    try {
      const [dashboard, performance] = await Promise.all([
        this.getDashboardAnalytics(days),
        this.getPerformanceMetrics()
      ]);

      return {
        success: dashboard.success && performance.success,
        data: {
          dashboard: dashboard.success ? dashboard.data : null,
          performance: performance.success ? performance.data : null,
          generated_at: new Date().toISOString()
        },
        message: 'Analytics summary retrieved successfully'
      };
    } catch (error) {
      console.error('Error fetching analytics summary:', error);
      throw error;
    }
  },

  /**
   * Refresh analytics data (force cache refresh)
   * @returns {Promise<Object>} Refreshed analytics data
   */
  async refreshAnalytics() {
    try {
      // Add cache-busting parameter
      const timestamp = Date.now();
      const response = await apiClient.get(
        `${ENDPOINTS.ANALYTICS.DASHBOARD}?days=7&_t=${timestamp}`
      );
      return response.data;
    } catch (error) {
      console.error('Error refreshing analytics:', error);
      throw error;
    }
  }
};

export default analyticsService;
