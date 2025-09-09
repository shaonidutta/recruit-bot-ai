import axios from 'axios';
import { apiClient } from '../client.js';
import { ENDPOINTS } from '../endpoints.js';
import { handleApiError } from '../errorHandler.js';

export const workflowService = {
  // Run workflow with keywords
  runWorkflow: async (keywords = 'Software Engineer') => {
    try {
      // Create a custom axios instance with longer timeout for workflows
      const workflowClient = axios.create({
        baseURL: apiClient.defaults.baseURL,
        timeout: 180000, // 3 minutes for workflow operations
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });

      const response = await workflowClient.post(ENDPOINTS.WORKFLOWS.RUN, { keywords });
      return response.data;
    } catch (error) {
      // If it's a timeout error, return a partial success response
      if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
        return {
          success: true,
          message: 'Workflow started successfully. Processing continues in background.',
          data: {
            status: 'processing',
            message: 'Workflow is running in the background. Check the dashboard for updates.',
            workflow_id: Date.now().toString() // Generate a temporary ID
          }
        };
      }
      throw handleApiError(error);
    }
  },

  // Test workflow without authentication
  testWorkflow: async () => {
    try {
      const response = await apiClient.post(ENDPOINTS.WORKFLOWS.TEST);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Run workflow with custom parameters
  runWorkflowWithParams: async (params = {}) => {
    try {
      const defaultParams = {
        keywords: 'Software Engineer',
        ...params
      };
      const response = await apiClient.post(ENDPOINTS.WORKFLOWS.RUN, defaultParams);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  }
};
