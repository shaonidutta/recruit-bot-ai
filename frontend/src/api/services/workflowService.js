import { apiClient } from '../client.js';
import { ENDPOINTS } from '../endpoints.js';
import { handleApiError } from '../errorHandler.js';

export const workflowService = {
  // Run workflow with keywords
  runWorkflow: async (keywords = 'Software Engineer') => {
    try {
      const response = await apiClient.post(ENDPOINTS.WORKFLOWS.RUN, { keywords });
      return response.data;
    } catch (error) {
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
