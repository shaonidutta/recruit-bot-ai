import { useState, useEffect, useCallback } from 'react';
import { matchService } from '../api/services/matchService';

/**
 * Custom hook for managing match data
 * Provides methods to fetch, filter, and manage job-candidate matches
 */
export const useMatches = (initialParams = {}) => {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 10,
    total: 0,
    has_more: false
  });

  // Fetch matches with current parameters
  const fetchMatches = useCallback(async (params = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      const mergedParams = { ...initialParams, ...params };
      const response = await matchService.getMatches(mergedParams);
      
      if (response.success) {
        setMatches(response.data.matches || []);
        setPagination(response.data.pagination || {});
      } else {
        throw new Error(response.message || 'Failed to fetch matches');
      }
    } catch (err) {
      console.error('Error fetching matches:', err);
      setError(err.message || 'Failed to fetch matches');
      setMatches([]);
    } finally {
      setLoading(false);
    }
  }, [initialParams]);

  // Fetch recent matches
  const fetchRecentMatches = useCallback(async (limit = 10, hours = 24) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await matchService.getRecentMatches(limit, hours);
      
      if (response.success) {
        setMatches(response.data.matches || []);
        // Set pagination info for recent matches
        setPagination({
          skip: 0,
          limit: limit,
          total: response.data.matches?.length || 0,
          has_more: false
        });
      } else {
        throw new Error(response.message || 'Failed to fetch recent matches');
      }
    } catch (err) {
      console.error('Error fetching recent matches:', err);
      setError(err.message || 'Failed to fetch recent matches');
      setMatches([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch matches for specific job
  const fetchMatchesForJob = useCallback(async (jobId, params = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await matchService.getMatchesForJob(jobId, params);
      
      if (response.success) {
        setMatches(response.data.matches || []);
        // Set pagination info
        setPagination({
          skip: 0,
          limit: params.limit || 20,
          total: response.data.matches?.length || 0,
          has_more: false
        });
      } else {
        throw new Error(response.message || 'Failed to fetch job matches');
      }
    } catch (err) {
      console.error('Error fetching job matches:', err);
      setError(err.message || 'Failed to fetch job matches');
      setMatches([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch matches for specific candidate
  const fetchMatchesForCandidate = useCallback(async (candidateId, params = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await matchService.getMatchesForCandidate(candidateId, params);
      
      if (response.success) {
        setMatches(response.data.matches || []);
        // Set pagination info
        setPagination({
          skip: 0,
          limit: params.limit || 20,
          total: response.data.matches?.length || 0,
          has_more: false
        });
      } else {
        throw new Error(response.message || 'Failed to fetch candidate matches');
      }
    } catch (err) {
      console.error('Error fetching candidate matches:', err);
      setError(err.message || 'Failed to fetch candidate matches');
      setMatches([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load more matches (pagination)
  const loadMore = useCallback(async () => {
    if (!pagination.has_more || loading) return;

    try {
      setLoading(true);
      
      const params = {
        ...initialParams,
        skip: pagination.skip + pagination.limit,
        limit: pagination.limit
      };
      
      const response = await matchService.getMatches(params);
      
      if (response.success) {
        setMatches(prev => [...prev, ...(response.data.matches || [])]);
        setPagination(response.data.pagination || {});
      }
    } catch (err) {
      console.error('Error loading more matches:', err);
      setError(err.message || 'Failed to load more matches');
    } finally {
      setLoading(false);
    }
  }, [initialParams, pagination, loading]);

  // Refresh matches
  const refresh = useCallback(() => {
    fetchMatches();
  }, [fetchMatches]);

  // Filter matches by score
  const filterByScore = useCallback((minScore) => {
    return matches.filter(match => match.match_score >= minScore);
  }, [matches]);

  // Get top matches
  const getTopMatches = useCallback((count = 5) => {
    return [...matches]
      .sort((a, b) => b.match_score - a.match_score)
      .slice(0, count);
  }, [matches]);

  // Search matches locally
  const searchMatches = useCallback((searchTerm) => {
    if (!searchTerm) return matches;
    
    const term = searchTerm.toLowerCase();
    return matches.filter(match => 
      match.candidate_name?.toLowerCase().includes(term) ||
      match.job_title?.toLowerCase().includes(term) ||
      match.company_name?.toLowerCase().includes(term) ||
      match.match_reasons?.some(reason => reason.toLowerCase().includes(term))
    );
  }, [matches]);

  // Initial load
  useEffect(() => {
    if (Object.keys(initialParams).length > 0) {
      fetchMatches();
    }
  }, []); // Remove fetchMatches from dependency to prevent infinite loop

  return {
    // Data
    matches,
    loading,
    error,
    pagination,
    
    // Actions
    fetchMatches,
    fetchRecentMatches,
    fetchMatchesForJob,
    fetchMatchesForCandidate,
    loadMore,
    refresh,
    
    // Utilities
    filterByScore,
    getTopMatches,
    searchMatches,
    
    // Computed values
    hasMatches: matches.length > 0,
    isEmpty: !loading && matches.length === 0,
    canLoadMore: pagination.has_more && !loading
  };
};

/**
 * Hook for match statistics
 */
export const useMatchStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await matchService.getMatchStats();
      
      if (response.success) {
        setStats(response.data);
      } else {
        throw new Error(response.message || 'Failed to fetch match statistics');
      }
    } catch (err) {
      console.error('Error fetching match stats:', err);
      setError(err.message || 'Failed to fetch match statistics');
      setStats(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return {
    stats,
    loading,
    error,
    refresh: fetchStats
  };
};

/**
 * Hook for match summary (dashboard)
 */
export const useMatchSummary = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSummary = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await matchService.getMatchSummary();
      
      if (response.success) {
        setSummary(response.data);
      } else {
        throw new Error(response.message || 'Failed to fetch match summary');
      }
    } catch (err) {
      console.error('Error fetching match summary:', err);
      setError(err.message || 'Failed to fetch match summary');
      setSummary(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  return {
    summary,
    loading,
    error,
    refresh: fetchSummary
  };
};

export default useMatches;
