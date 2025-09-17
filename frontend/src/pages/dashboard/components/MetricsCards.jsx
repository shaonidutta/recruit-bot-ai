import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { LoadingSpinner } from '../../../components/ui/LoadingSpinner';
import { AnimatedCounter, GrowthIndicator, LiveIndicator } from '../../../components/ui/AnimatedCounter';
import { useJobs } from '../../../hooks/useJobs';
import { useHealth } from '../../../hooks/useHealth';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import { jobsService } from '../../../api/services/jobsService';
import { candidatesService } from '../../../api/services/candidatesService';
import { useState, useEffect } from 'react';

const MetricCard = ({
  title,
  value,
  previousValue,
  loading,
  error,
  icon,
  color = 'blue',
  subtitle,
  isUpdating,
  lastUpdated,
  formatter
}) => (
  <Card className="bg-white border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200">
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium text-gray-600">
        {title}
      </CardTitle>
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm ${
        color === 'green' ? 'bg-green-100 text-green-600' :
        color === 'red' ? 'bg-red-100 text-red-600' :
        color === 'orange' ? 'bg-orange-100 text-orange-600' :
        color === 'purple' ? 'bg-purple-100 text-purple-600' :
        'bg-blue-100 text-blue-600'
      }`}>
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {color === 'green' ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          ) : color === 'purple' ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
          ) : color === 'orange' ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m8 6V8a2 2 0 00-2-2H10a2 2 0 00-2 2v8a2 2 0 002 2h4a2 2 0 002-2z" />
          )}
        </svg>
      </div>
    </CardHeader>
    <CardContent>
      {loading ? (
        <div className="flex items-center space-x-2">
          <LoadingSpinner size="sm" />
          <span className="text-sm text-slate-500">Loading...</span>
        </div>
      ) : error ? (
        <div className="text-red-500 text-sm">Error loading data</div>
      ) : (
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <div className="text-2xl font-bold text-gray-900">
              {typeof value === 'string' ? value : (
                <AnimatedCounter
                  value={value || 0}
                  formatter={formatter || ((val) => val.toLocaleString())}
                />
              )}
            </div>
            {previousValue !== undefined && (
              <GrowthIndicator
                current={value || 0}
                previous={previousValue || 0}
              />
            )}
          </div>

          {subtitle && (
            <p className="text-xs text-gray-500">{subtitle}</p>
          )}
        </div>
      )}
    </CardContent>
  </Card>
);

const MetricsCards = () => {
  const { stats, loading: jobsLoading, error: jobsError } = useJobs();
  const { health, loading: healthLoading, error: healthError, isHealthy } = useHealth();

  // Store previous values for growth calculation
  const [previousStats, setPreviousStats] = useState(null);

  // Real-time polling for enhanced metrics
  const {
    data: realtimeStats,
    loading: realtimeLoading,
    error: realtimeError,
    lastUpdated
  } = useRealTimeData(
    async () => {
      const response = await jobsService.getStats();
      return response.success ? response.data.stats : null;
    },
    30000 // Poll every 30 seconds
  );

  // Update previous stats when new data arrives
  useEffect(() => {
    if (realtimeStats && stats) {
      setPreviousStats(stats);
    }
  }, [realtimeStats, stats]);

  // Use real-time data if available, fallback to regular stats
  const currentStats = realtimeStats || stats;
  const isLoading = (jobsLoading && !stats) || (realtimeLoading && !realtimeStats && !stats);
  const hasError = jobsError || realtimeError;

  // Only show updating indicator if we don't have any data yet, not during routine polling
  const isUpdating = realtimeLoading && !currentStats;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="Total Jobs"
        value={currentStats?.total_jobs}
        previousValue={previousStats?.total_jobs}
        loading={isLoading}
        error={hasError}
        icon="💼"
        color="blue"
        subtitle="Jobs discovered"
        isUpdating={isUpdating}
        lastUpdated={lastUpdated}
      />
      <MetricCard
        title="Active Jobs"
        value={currentStats?.active_jobs}
        previousValue={previousStats?.active_jobs}
        loading={isLoading}
        error={hasError}
        icon="🎯"
        color="green"
        subtitle="Currently active"
        isUpdating={isUpdating}
        lastUpdated={lastUpdated}
      />
      <MetricCard
        title="Total Candidates"
        value={currentStats?.total_candidates}
        previousValue={previousStats?.total_candidates}
        loading={isLoading}
        error={hasError}
        icon="👥"
        color="purple"
        subtitle="Candidate profiles"
        isUpdating={isUpdating}
        lastUpdated={lastUpdated}
      />
      <MetricCard
        title="Total Matches"
        value={currentStats?.total_matches || 0}
        previousValue={previousStats?.total_matches}
        loading={isLoading}
        error={hasError}
        icon="⚡"
        color="orange"
        subtitle="Job-candidate matches"
        isUpdating={isUpdating}
        lastUpdated={lastUpdated}
      />
    </div>
  );
};

export default MetricsCards;
