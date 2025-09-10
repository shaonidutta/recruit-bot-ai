import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './Card';
import { Button } from './Button';
import { LoadingSpinner } from './LoadingSpinner';
import { MatchCard, CompactMatchCard } from './MatchCard';
import { useMatches } from '../../hooks/useMatches';

/**
 * MatchesList Component
 * Displays a list of job-candidate matches with filtering and pagination
 */
export const MatchesList = ({ 
  title = "Recent Matches",
  jobId = null,
  candidateId = null,
  limit = 10,
  compact = false,
  showFilters = false,
  showLoadMore = true,
  onMatchSelect,
  onMatchContact,
  onMatchApprove,
  onMatchReject
}) => {
  const [filters, setFilters] = useState({
    min_score: null,
    limit: limit
  });

  // Determine which fetch method to use based on props
  const getInitialParams = () => {
    const params = { limit };
    if (jobId) params.job_id = jobId;
    if (candidateId) params.candidate_id = candidateId;
    return params;
  };

  const {
    matches,
    loading,
    error,
    pagination,
    fetchMatches,
    fetchRecentMatches,
    fetchMatchesForJob,
    fetchMatchesForCandidate,
    loadMore,
    refresh,
    hasMatches,
    isEmpty,
    canLoadMore
  } = useMatches(getInitialParams());

  // Initial data fetch
  useEffect(() => {
    if (jobId) {
      fetchMatchesForJob(jobId, filters);
    } else if (candidateId) {
      fetchMatchesForCandidate(candidateId, filters);
    } else {
      fetchRecentMatches(filters.limit);
    }
  }, [jobId, candidateId]); // Remove functions and filters from dependency to prevent infinite loop

  // Handle filter changes
  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  // Handle match actions
  const handleMatchSelect = (match) => {
    onMatchSelect?.(match);
  };

  const handleMatchContact = (match) => {
    onMatchContact?.(match);
  };

  const handleMatchApprove = (match) => {
    onMatchApprove?.(match);
  };

  const handleMatchReject = (match) => {
    onMatchReject?.(match);
  };

  // Render loading state
  if (loading && !hasMatches) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>🎯</span>
            <span>{title}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner size="md" />
            <span className="ml-2 text-gray-600">Loading matches...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Render error state
  if (error && !hasMatches) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>🎯</span>
            <span>{title}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-red-600 mb-2">⚠️ Error loading matches</div>
            <p className="text-gray-600 mb-4">{error}</p>
            <Button onClick={refresh} variant="outline">
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Render empty state
  if (isEmpty) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>🎯</span>
            <span>{title}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-gray-400 text-4xl mb-4">🔍</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No matches found</h3>
            <p className="text-gray-600 mb-4">
              {jobId ? 'No candidates match this job yet.' : 
               candidateId ? 'No jobs match this candidate yet.' :
               'No recent matches available. Run a workflow to generate matches.'}
            </p>
            <Button onClick={refresh} variant="outline">
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <span>🎯</span>
            <span>{title}</span>
            <span className="text-sm font-normal text-gray-500">
              ({matches.length} {matches.length === 1 ? 'match' : 'matches'})
            </span>
          </CardTitle>
          
          <div className="flex items-center space-x-2">
            {/* Refresh Button */}
            <Button
              size="sm"
              variant="outline"
              onClick={refresh}
              disabled={loading}
              className="text-xs"
            >
              {loading ? <LoadingSpinner size="sm" /> : '🔄'}
              Refresh
            </Button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="flex items-center space-x-4 mt-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm text-gray-600">Min Score:</label>
              <select
                value={filters.min_score || ''}
                onChange={(e) => handleFilterChange({ 
                  min_score: e.target.value ? parseFloat(e.target.value) : null 
                })}
                className="text-sm border rounded px-2 py-1"
              >
                <option value="">All</option>
                <option value="0.9">90%+</option>
                <option value="0.8">80%+</option>
                <option value="0.7">70%+</option>
                <option value="0.6">60%+</option>
                <option value="0.5">50%+</option>
              </select>
            </div>
          </div>
        )}
      </CardHeader>

      <CardContent>
        {/* Matches List */}
        <div className={`space-y-${compact ? '2' : '4'}`}>
          {matches.map((match) => {
            const MatchComponent = compact ? CompactMatchCard : MatchCard;
            return (
              <MatchComponent
                key={match.id}
                match={match}
                onViewDetails={handleMatchSelect}
                onContact={handleMatchContact}
                onApprove={handleMatchApprove}
                onReject={handleMatchReject}
              />
            );
          })}
        </div>

        {/* Load More Button */}
        {showLoadMore && canLoadMore && (
          <div className="mt-6 text-center">
            <Button
              onClick={loadMore}
              disabled={loading}
              variant="outline"
              className="w-full"
            >
              {loading ? (
                <>
                  <LoadingSpinner size="sm" />
                  <span className="ml-2">Loading more...</span>
                </>
              ) : (
                `Load More Matches (${pagination.total - matches.length} remaining)`
              )}
            </Button>
          </div>
        )}

        {/* Loading indicator for additional matches */}
        {loading && hasMatches && (
          <div className="mt-4 text-center">
            <LoadingSpinner size="sm" />
            <span className="ml-2 text-sm text-gray-600">Loading...</span>
          </div>
        )}

        {/* Error indicator */}
        {error && hasMatches && (
          <div className="mt-4 text-center text-red-600 text-sm">
            Error: {error}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

/**
 * Recent Matches Component - Specialized for dashboard
 */
export const RecentMatchesList = ({ limit = 5, onMatchSelect }) => {
  return (
    <MatchesList
      title="Recent Matches"
      limit={limit}
      compact={true}
      showFilters={false}
      showLoadMore={false}
      onMatchSelect={onMatchSelect}
    />
  );
};

/**
 * Job Matches Component - Shows matches for a specific job
 */
export const JobMatchesList = ({ jobId, jobTitle, onMatchSelect, onMatchContact }) => {
  return (
    <MatchesList
      title={`Matches for ${jobTitle || 'Job'}`}
      jobId={jobId}
      limit={20}
      compact={false}
      showFilters={true}
      showLoadMore={true}
      onMatchSelect={onMatchSelect}
      onMatchContact={onMatchContact}
    />
  );
};

/**
 * Candidate Matches Component - Shows matches for a specific candidate
 */
export const CandidateMatchesList = ({ candidateId, candidateName, onMatchSelect }) => {
  return (
    <MatchesList
      title={`Matches for ${candidateName || 'Candidate'}`}
      candidateId={candidateId}
      limit={20}
      compact={false}
      showFilters={true}
      showLoadMore={true}
      onMatchSelect={onMatchSelect}
    />
  );
};

export default MatchesList;
