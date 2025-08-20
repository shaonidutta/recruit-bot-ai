import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { Progress } from '../../../components/ui/Progress';
import { Badge } from '../../../components/ui/Badge';
import { cn } from '../../../utils/cn';
import { getMockData } from '../../../data/mockData';

const MetricRow = ({ label, current, benchmark, unit = '%', trend, improvement }) => {
  const isGood = trend === 'up' || (trend === 'down' && label.includes('Response Time'));
  const trendIcon = isGood ? '📈' : '📉';
  const trendColor = isGood ? 'text-green-600' : 'text-red-600';

  return (
    <div className="flex items-center justify-between py-3 border-b border-slate-100 last:border-b-0">
      <div className="flex-1">
        <p className="text-sm font-medium text-slate-700">{label}</p>
        {benchmark && (
          <p className="text-xs text-slate-500">
            Industry avg: {benchmark}{unit}
          </p>
        )}
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="text-right">
          <div className="text-lg font-bold text-slate-900">
            {typeof current === 'string' ? current : `${current}${unit}`}
          </div>
          {improvement && (
            <div className={cn("text-xs font-medium", trendColor)}>
              {trendIcon} {improvement}% {trend === 'down' ? 'faster' : 'better'}
            </div>
          )}
        </div>
        
        {benchmark && typeof current === 'number' && (
          <div className="w-20">
            <Progress 
              value={Math.min((current / benchmark) * 50, 100)} 
              className="h-2"
            />
          </div>
        )}
      </div>
    </div>
  );
};

const ResponseAnalytics = () => {
  const analytics = getMockData('analytics');
  
  if (!analytics) return null;

  const { responseRate, openRate, avgResponseTime, campaignStats } = analytics;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <span>📊</span>
              <span>Response Analytics</span>
            </CardTitle>
            <p className="text-sm text-slate-600 mt-1">
              Email campaign performance metrics
            </p>
          </div>
          <Badge variant="success" className="animate-pulse">
            15.2% Response Rate
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent>
        {/* Key Metrics */}
        <div className="space-y-1">
          <MetricRow
            label="Response Rate"
            current={responseRate.current}
            benchmark={responseRate.industryAverage}
            trend={responseRate.trend}
            improvement={responseRate.change}
          />
          
          <MetricRow
            label="Email Open Rate"
            current={openRate.current}
            benchmark={openRate.industryAverage}
            trend={openRate.trend}
            improvement={openRate.change}
          />
          
          <MetricRow
            label="Avg Response Time"
            current={avgResponseTime.current}
            benchmark={null}
            unit=""
            trend={avgResponseTime.trend}
            improvement={avgResponseTime.improvement}
          />
        </div>

        {/* Campaign Summary */}
        <div className="mt-6 pt-4 border-t border-slate-100">
          <h4 className="text-sm font-medium text-slate-700 mb-3">Campaign Summary</h4>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-xl font-bold text-blue-700">
                {campaignStats.activeCampaigns}
              </div>
              <p className="text-xs text-blue-600">Active Campaigns</p>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-xl font-bold text-green-700">
                {campaignStats.completedCampaigns}
              </div>
              <p className="text-xs text-green-600">Completed</p>
            </div>
          </div>
        </div>

        {/* Performance Indicators */}
        <div className="mt-4 p-3 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-700">
                Performance vs Industry
              </p>
              <p className="text-xs text-slate-500">
                7.6x better response rate
              </p>
            </div>
            <div className="text-2xl">🚀</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ResponseAnalytics;
