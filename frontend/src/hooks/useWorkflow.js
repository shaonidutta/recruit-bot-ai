import { useState, useCallback } from 'react';
import { workflowService } from '../api/services/workflowService.js';

export const useWorkflow = () => {
  const [workflowStatus, setWorkflowStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastRun, setLastRun] = useState(null);

  // Run workflow with keywords
  const runWorkflow = useCallback(async (keywords) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await workflowService.runWorkflow(keywords);
      
      if (response.success) {
        const workflowResult = {
          success: true,
          message: response.message || 'Workflow completed successfully',
          data: response.data || {},
          timestamp: new Date().toISOString()
        };
        
        setWorkflowStatus(workflowResult);
        setLastRun(workflowResult);
        return workflowResult;
      } else {
        const errorResult = {
          success: false,
          message: response.message || 'Workflow failed',
          error: response.error,
          timestamp: new Date().toISOString()
        };
        
        setWorkflowStatus(errorResult);
        return errorResult;
      }
    } catch (err) {
      const errorMessage = err.message || 'Failed to run workflow';
      setError(errorMessage);
      
      const errorResult = {
        success: false,
        message: errorMessage,
        error: err,
        timestamp: new Date().toISOString()
      };
      
      setWorkflowStatus(errorResult);
      console.error('Error running workflow:', err);
      return errorResult;
    } finally {
      setLoading(false);
    }
  }, []);

  // Test workflow
  const testWorkflow = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await workflowService.testWorkflow();
      
      if (response.success) {
        const testResult = {
          success: true,
          message: 'Test workflow completed successfully',
          data: response.data || {},
          timestamp: new Date().toISOString()
        };
        
        setWorkflowStatus(testResult);
        return testResult;
      } else {
        const errorResult = {
          success: false,
          message: response.message || 'Test workflow failed',
          error: response.error,
          timestamp: new Date().toISOString()
        };
        
        setWorkflowStatus(errorResult);
        return errorResult;
      }
    } catch (err) {
      const errorMessage = err.message || 'Failed to test workflow';
      setError(errorMessage);
      
      const errorResult = {
        success: false,
        message: errorMessage,
        error: err,
        timestamp: new Date().toISOString()
      };
      
      setWorkflowStatus(errorResult);
      console.error('Error testing workflow:', err);
      return errorResult;
    } finally {
      setLoading(false);
    }
  }, []);

  // Clear workflow status
  const clearStatus = useCallback(() => {
    setWorkflowStatus(null);
    setError(null);
  }, []);

  return {
    workflowStatus,
    lastRun,
    loading,
    error,
    runWorkflow,
    testWorkflow,
    clearStatus
  };
};
