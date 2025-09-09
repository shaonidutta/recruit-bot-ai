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
  <Card className="relative overflow-hidden transition-all duration-300 hover:shadow-md hover:scale-105">
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium text-slate-600">
        {title}
      </CardTitle>
      <div className={`text-2xl transition-colors duration-300 ${
        color === 'green' ? 'text-green-500' :
        color === 'red' ? 'text-red-500' :
        color === 'orange' ? 'text-orange-500' :
        color === 'purple' ? 'text-purple-500' :
        'text-blue-500'
      }`}>
        {icon}
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
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <div className="text-2xl font-bold text-slate-900">
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

          <div className="flex items-center justify-between">
            {subtitle && (
              <p className="text-xs text-slate-500">{subtitle}</p>
            )}
            <LiveIndicator
              isUpdating={isUpdating}
              lastUpdated={lastUpdated}
              className="ml-auto"
            />
          </div>
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
