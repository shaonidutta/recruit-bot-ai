import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './Card';
import { LoadingSpinner } from './LoadingSpinner';
import { Progress } from './Progress';
import { useMatchStats } from '../../hooks/useMatches';

/**
 * Match Statistics Component
 * Displays comprehensive match statistics and metrics
 */
export const MatchStats = ({ showDistribution = true, showTrends = false }) => {
  const { stats, loading, error, refresh } = useMatchStats();

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>📊</span>
            <span>Match Statistics</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner size="md" />
            <span className="ml-2 text-gray-600">Loading statistics...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>📊</span>
            <span>Match Statistics</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-red-600 mb-2">⚠️ Error loading statistics</div>
            <p className="text-gray-600 mb-4">{error}</p>
            <button 
              onClick={refresh}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Try Again
            </button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!stats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>📊</span>
            <span>Match Statistics</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-gray-400 text-4xl mb-4">📊</div>
            <p className="text-gray-600">No statistics available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const {
    total_matches,
    recent_matches_24h,
    score_statistics,
    score_distribution
  } = stats;

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>📊</span>
            <span>Match Statistics</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Total Matches */}
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-1">
                {total_matches?.toLocaleString() || 0}
              </div>
              <div className="text-sm text-gray-600">Total Matches</div>
            </div>

            {/* Recent Matches */}
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-1">
                {recent_matches_24h?.toLocaleString() || 0}
              </div>
              <div className="text-sm text-gray-600">Last 24 Hours</div>
            </div>

            {/* Average Score */}
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-1">
                {score_statistics?.average ? `${Math.round(score_statistics.average * 100)}%` : 'N/A'}
              </div>
              <div className="text-sm text-gray-600">Average Score</div>
            </div>
          </div>

          {/* Score Range */}
          {score_statistics && (
            <div className="mt-6 pt-6 border-t">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Score Range</h4>
              <div className="flex justify-between text-sm">
                <div>
                  <span className="text-gray-600">Minimum: </span>
                  <span className="font-medium">{Math.round(score_statistics.minimum * 100)}%</span>
                </div>
                <div>
                  <span className="text-gray-600">Maximum: </span>
                  <span className="font-medium">{Math.round(score_statistics.maximum * 100)}%</span>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Score Distribution */}
      {showDistribution && score_distribution && score_distribution.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span>📈</span>
              <span>Score Distribution</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {score_distribution.map((range, index) => (
                <div key={index} className="flex items-center space-x-4">
                  <div className="w-16 text-sm text-gray-600 font-medium">
                    {range.range}
                  </div>
                  <div className="flex-1">
                    <Progress 
                      value={range.percentage} 
                      className="h-2"
                    />
                  </div>
                  <div className="w-20 text-right">
                    <div className="text-sm font-medium">{range.count}</div>
                    <div className="text-xs text-gray-500">{range.percentage}%</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

/**
 * Compact Match Stats for dashboard
 */
export const CompactMatchStats = () => {
  const { stats, loading, error } = useMatchStats();

  if (loading) {
    return (
      <div className="flex items-center space-x-2 text-sm text-gray-600">
        <LoadingSpinner size="sm" />
        <span>Loading stats...</span>
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="text-sm text-red-600">
        Stats unavailable
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-4 text-sm">
      <div>
        <span className="text-gray-600">Total: </span>
        <span className="font-medium">{stats.total_matches || 0}</span>
      </div>
      <div>
        <span className="text-gray-600">Today: </span>
        <span className="font-medium">{stats.recent_matches_24h || 0}</span>
      </div>
      <div>
        <span className="text-gray-600">Avg: </span>
        <span className="font-medium">
          {stats.score_statistics?.average ? `${Math.round(stats.score_statistics.average * 100)}%` : 'N/A'}
        </span>
      </div>
    </div>
  );
};

/**
 * Match Quality Indicator
 */
export const MatchQualityIndicator = ({ score, size = 'md' }) => {
  const percentage = Math.round(score * 100);
  
  const getQualityLevel = (score) => {
    if (score >= 0.9) return { level: 'Excellent', color: 'text-green-600', bg: 'bg-green-100' };
    if (score >= 0.8) return { level: 'Very Good', color: 'text-green-600', bg: 'bg-green-100' };
    if (score >= 0.7) return { level: 'Good', color: 'text-yellow-600', bg: 'bg-yellow-100' };
    if (score >= 0.6) return { level: 'Fair', color: 'text-yellow-600', bg: 'bg-yellow-100' };
    if (score >= 0.5) return { level: 'Poor', color: 'text-red-600', bg: 'bg-red-100' };
    return { level: 'Very Poor', color: 'text-red-600', bg: 'bg-red-100' };
  };

  const quality = getQualityLevel(score);
  
  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2'
  };

  return (
    <div className={`inline-flex items-center rounded-full ${quality.bg} ${quality.color} ${sizeClasses[size]} font-medium`}>
      <span className="mr-1">{percentage}%</span>
      <span>{quality.level}</span>
    </div>
  );
};

export default MatchStats;
