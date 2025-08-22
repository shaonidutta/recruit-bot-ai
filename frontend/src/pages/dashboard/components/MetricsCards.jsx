import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { LoadingSpinner } from '../../../components/ui/LoadingSpinner';
import { useJobs } from '../../../hooks/useJobs';
import { useHealth } from '../../../hooks/useHealth';
import { TrendingUp, TrendingDown, Activity, Database, Users, Briefcase, CheckCircle, AlertCircle } from 'lucide-react';

const MetricCard = ({
  title,
  value,
  loading,
  error,
  icon: IconComponent,
  color = 'blue',
  subtitle,
  trend,
  trendValue,
  gradient = false
}) => {
  const colorClasses = {
    blue: {
      icon: 'text-blue-500',
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      gradient: 'from-blue-500 to-blue-600',
      hover: 'hover:border-blue-300'
    },
    green: {
      icon: 'text-green-500',
      bg: 'bg-green-50',
      border: 'border-green-200',
      gradient: 'from-green-500 to-green-600',
      hover: 'hover:border-green-300'
    },
    red: {
      icon: 'text-red-500',
      bg: 'bg-red-50',
      border: 'border-red-200',
      gradient: 'from-red-500 to-red-600',
      hover: 'hover:border-red-300'
    },
    orange: {
      icon: 'text-orange-500',
      bg: 'bg-orange-50',
      border: 'border-orange-200',
      gradient: 'from-orange-500 to-orange-600',
      hover: 'hover:border-orange-300'
    },
    purple: {
      icon: 'text-purple-500',
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      gradient: 'from-purple-500 to-purple-600',
      hover: 'hover:border-purple-300'
    }
  };

  const currentColor = colorClasses[color];

  return (
    <Card className={`relative overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1 border-2 ${currentColor.border} ${currentColor.hover} group`}>
      {/* Gradient overlay */}
      {gradient && (
        <div className={`absolute inset-0 bg-gradient-to-br ${currentColor.gradient} opacity-5 group-hover:opacity-10 transition-opacity duration-300`}></div>
      )}

      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
        <CardTitle className="text-sm font-medium text-slate-600 group-hover:text-slate-800 transition-colors">
          {title}
        </CardTitle>
        <div className={`p-2 rounded-lg ${currentColor.bg} group-hover:scale-110 transition-transform duration-300`}>
          <IconComponent className={`w-5 h-5 ${currentColor.icon}`} />
        </div>
      </CardHeader>

      <CardContent className="relative z-10">
        {loading ? (
          <div className="flex items-center space-x-2">
            <LoadingSpinner size="sm" />
            <span className="text-sm text-slate-500">Loading...</span>
          </div>
        ) : error ? (
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-500" />
            <span className="text-red-500 text-sm">Error loading data</span>
          </div>
        ) : (
          <div>
            <div className="flex items-baseline space-x-2">
              <div className="text-3xl font-bold text-slate-900 group-hover:scale-105 transition-transform duration-300">
                {typeof value === 'string' ? value : (value || 0).toLocaleString()}
              </div>
              {trend && (
                <div className={`flex items-center text-sm ${trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'}`}>
                  {trend === 'up' ? (
                    <TrendingUp className="w-4 h-4 mr-1" />
                  ) : trend === 'down' ? (
                    <TrendingDown className="w-4 h-4 mr-1" />
                  ) : null}
                  {trendValue && <span>{trendValue}</span>}
                </div>
              )}
            </div>
            {subtitle && (
              <p className="text-xs text-slate-500 mt-2 group-hover:text-slate-600 transition-colors">{subtitle}</p>
            )}
          </div>
        )}
      </CardContent>

      {/* Animated border */}
      <div className={`absolute inset-0 rounded-lg border-2 border-transparent bg-gradient-to-r ${currentColor.gradient} opacity-0 group-hover:opacity-20 transition-opacity duration-300 -z-10`}></div>
    </Card>
  );
};

const MetricsCards = () => {
  const { stats, loading: jobsLoading, error: jobsError } = useJobs();
  const { health, loading: healthLoading, error: healthError, isHealthy } = useHealth();

  return (
    <div className="space-y-6">
      {/* Primary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Jobs"
          value={stats?.total_jobs}
          loading={jobsLoading}
          error={jobsError}
          icon={Briefcase}
          color="blue"
          subtitle="Jobs discovered"
          trend="up"
          trendValue="+12%"
          gradient={true}
        />
        <MetricCard
          title="Total Candidates"
          value={stats?.total_candidates}
          loading={jobsLoading}
          error={jobsError}
          icon={Users}
          color="green"
          subtitle="Candidate profiles"
          trend="up"
          trendValue="+8%"
          gradient={true}
        />
        <MetricCard
          title="System Status"
          value={isHealthy ? 'Healthy' : 'Issues'}
          loading={healthLoading}
          error={healthError}
          icon={isHealthy ? CheckCircle : AlertCircle}
          color={isHealthy ? 'green' : 'red'}
          subtitle="Service status"
          gradient={true}
        />
        <MetricCard
          title="Database"
          value={health?.database?.status === 'connected' ? 'Connected' : 'Disconnected'}
          loading={healthLoading}
          error={healthError}
          icon={Database}
          color={health?.database?.status === 'connected' ? 'green' : 'red'}
          subtitle="Database connection"
          gradient={true}
        />
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Active Matches"
          value={stats?.active_matches || 0}
          loading={jobsLoading}
          error={jobsError}
          icon={Activity}
          color="purple"
          subtitle="Current job-candidate matches"
          trend="up"
          trendValue="+15%"
        />
        <MetricCard
          title="Success Rate"
          value="94.2%"
          loading={false}
          error={null}
          icon={TrendingUp}
          color="green"
          subtitle="Match accuracy rate"
          trend="up"
          trendValue="+2.1%"
        />
        <MetricCard
          title="Processing Speed"
          value="2.3s"
          loading={false}
          error={null}
          icon={Activity}
          color="orange"
          subtitle="Average processing time"
          trend="down"
          trendValue="-0.5s"
        />
      </div>
    </div>
  );
};

export default MetricsCards;
