import { useState, useEffect, useCallback } from 'react';
import { jobsService } from '../api/services/jobsService.js';

export const useJobs = () => {
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState(null);

  // Fetch job statistics
  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await jobsService.getStats();
      if (response.success && response.data) {
        setStats(response.data.stats);
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch job statistics');
      console.error('Error fetching job stats:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch jobs with optional parameters
  const fetchJobs = useCallback(async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await jobsService.getJobs(params);
      if (response.success && response.data) {
        setJobs(response.data.jobs || []);
        setPagination(response.data.pagination || null);
        return response.data;
      }
      return null;
    } catch (err) {
      setError(err.message || 'Failed to fetch jobs');
      console.error('Error fetching jobs:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch recent jobs from latest workflow run
  const fetchRecentJobs = useCallback(async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await jobsService.getRecentJobs(params);
      if (response.success && response.data) {
        setJobs(response.data.jobs || []);
        // Set pagination-like info for recent jobs
        setPagination({
          skip: 0,
          limit: response.data.limit || 10,
          total: response.data.count || 0,
          has_more: false,
          workflow_id: response.data.workflow_id
        });
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch recent jobs');
      console.error('Error fetching recent jobs:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Search jobs
  const searchJobs = useCallback(async (searchTerm, filters = {}) => {
    try {
      setLoading(true);
      setError(null);
      const response = await jobsService.searchJobs(searchTerm, filters);
      if (response.success && response.data) {
        setJobs(response.data.jobs || []);
        setPagination(response.data.pagination || null);
        return response.data;
      }
      return null;
    } catch (err) {
      setError(err.message || 'Failed to search jobs');
      console.error('Error searching jobs:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Get job by ID
  const getJobById = useCallback(async (jobId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await jobsService.getJobById(jobId);
      if (response.success && response.data) {
        return response.data.job;
      }
      return null;
    } catch (err) {
      setError(err.message || 'Failed to fetch job details');
      console.error('Error fetching job by ID:', err);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Refresh all data
  const refetch = useCallback(() => {
    fetchStats();
    fetchRecentJobs({ limit: 10 });
  }, [fetchStats, fetchRecentJobs]);

  // Initial data fetch
  useEffect(() => {
    fetchStats();
    fetchRecentJobs({ limit: 10 });
  }, [fetchStats, fetchRecentJobs]);

  return {
    jobs,
    stats,
    pagination,
    loading,
    error,
    fetchStats,
    fetchJobs,
    fetchRecentJobs,
    searchJobs,
    getJobById,
    refetch
  };
};
