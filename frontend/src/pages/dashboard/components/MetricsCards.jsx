import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { LoadingSpinner } from '../../../components/ui/LoadingSpinner';
import { useJobs } from '../../../hooks/useJobs';
import { useHealth } from '../../../hooks/useHealth';

const MetricCard = ({ title, value, loading, error, icon, color = 'blue', subtitle }) => (
  <Card className="relative overflow-hidden transition-all duration-300 hover:shadow-md">
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium text-slate-600">
        {title}
      </CardTitle>
      <div className={`text-2xl ${color === 'green' ? 'text-green-500' : color === 'red' ? 'text-red-500' : color === 'orange' ? 'text-orange-500' : 'text-blue-500'}`}>
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
        <div>
          <div className="text-2xl font-bold text-slate-900">
            {typeof value === 'string' ? value : (value || 0).toLocaleString()}
          </div>
          {subtitle && (
            <p className="text-xs text-slate-500 mt-1">{subtitle}</p>
          )}
        </div>
      )}
    </CardContent>
  </Card>
);

const MetricsCards = () => {
  const { stats, loading: jobsLoading, error: jobsError } = useJobs();
  const { health, loading: healthLoading, error: healthError, isHealthy } = useHealth();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="Total Jobs"
        value={stats?.total_jobs}
        loading={jobsLoading}
        error={jobsError}
        icon="💼"
        color="blue"
        subtitle="Jobs discovered"
      />
      <MetricCard
        title="Total Candidates"
        value={stats?.total_candidates}
        loading={jobsLoading}
        error={jobsError}
        icon="👥"
        color="green"
        subtitle="Candidate profiles"
      />
      <MetricCard
        title="System Status"
        value={isHealthy ? 'Healthy' : 'Issues'}
        loading={healthLoading}
        error={healthError}
        icon="🔧"
        color={isHealthy ? 'green' : 'red'}
        subtitle="Service status"
      />
      <MetricCard
        title="Database"
        value={health?.database?.status === 'connected' ? 'Connected' : 'Disconnected'}
        loading={healthLoading}
        error={healthError}
        icon="🗄️"
        color={health?.database?.status === 'connected' ? 'green' : 'red'}
        subtitle="Database connection"
      />
    </div>
  );
};

export default MetricsCards;
