import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

/**
 * Dashboard Analytics Component
 * Provides visual analytics and charts for recruitment data
 */
const DashboardAnalytics = () => {
  const [analyticsData, setAnalyticsData] = useState({
    jobTrends: [],
    sourceBreakdown: [],
    workflowSuccess: [],
    emailPerformance: []
  });

  // Generate mock analytics data
  useEffect(() => {
    const generateMockData = () => {
      // Job discovery trends (last 7 days)
      const jobTrends = Array.from({ length: 7 }, (_, i) => {
        const date = new Date();
        date.setDate(date.getDate() - (6 - i));
        return {
          date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          jobs: Math.floor(Math.random() * 50) + 20,
          matches: Math.floor(Math.random() * 15) + 5,
          emails: Math.floor(Math.random() * 25) + 10
        };
      });

      // Job source breakdown
      const sourceBreakdown = [
        { name: 'LinkedIn', value: 45, color: '#0077B5' },
        { name: 'Indeed', value: 35, color: '#2557A7' },
        { name: 'Google Jobs', value: 20, color: '#4285F4' }
      ];

      // Workflow success rates
      const workflowSuccess = [
        { name: 'Job Discovery', success: 95, failed: 5 },
        { name: 'Candidate Matching', success: 87, failed: 13 },
        { name: 'Email Delivery', success: 92, failed: 8 },
        { name: 'Response Rate', success: 15, failed: 85 }
      ];

      // Email performance metrics
      const emailPerformance = [
        { metric: 'Sent', value: 156, color: '#3B82F6' },
        { metric: 'Delivered', value: 143, color: '#10B981' },
        { metric: 'Opened', value: 67, color: '#F59E0B' },
        { metric: 'Replied', value: 23, color: '#8B5CF6' }
      ];

      setAnalyticsData({
        jobTrends,
        sourceBreakdown,
        workflowSuccess,
        emailPerformance
      });
    };

    generateMockData();
    
    // Update data every 30 seconds for demo effect
    const interval = setInterval(generateMockData, 30000);
    return () => clearInterval(interval);
  }, []);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium text-gray-900">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {`${entry.dataKey}: ${entry.value}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Job Discovery Trends */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>📈</span>
            <span>Job Discovery Trends</span>
            <Badge variant="outline" className="ml-auto">Last 7 days</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={analyticsData.jobTrends}>
              <defs>
                <linearGradient id="jobsGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="matchesGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="date" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="jobs"
                stroke="#3B82F6"
                fillOpacity={1}
                fill="url(#jobsGradient)"
                name="Jobs Discovered"
              />
              <Area
                type="monotone"
                dataKey="matches"
                stroke="#10B981"
                fillOpacity={1}
                fill="url(#matchesGradient)"
                name="Matches Found"
              />
              <Line
                type="monotone"
                dataKey="emails"
                stroke="#F59E0B"
                strokeWidth={2}
                name="Emails Sent"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Job Source Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>🎯</span>
            <span>Job Sources</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={analyticsData.sourceBreakdown}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
              >
                {analyticsData.sourceBreakdown.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                formatter={(value) => [`${value}%`, 'Percentage']}
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px'
                }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Workflow Success Rates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>✅</span>
            <span>Success Rates</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={analyticsData.workflowSuccess} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis type="number" domain={[0, 100]} stroke="#6B7280" />
              <YAxis dataKey="name" type="category" width={100} stroke="#6B7280" />
              <Tooltip 
                formatter={(value, name) => [`${value}%`, name === 'success' ? 'Success' : 'Failed']}
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="success" stackId="a" fill="#10B981" />
              <Bar dataKey="failed" stackId="a" fill="#EF4444" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Email Performance */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <span>📧</span>
            <span>Email Campaign Performance</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={analyticsData.emailPerformance}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis dataKey="metric" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]}>
                {analyticsData.emailPerformance.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          
          {/* Email funnel metrics */}
          <div className="grid grid-cols-4 gap-4 mt-4">
            {analyticsData.emailPerformance.map((metric, index) => (
              <div key={metric.metric} className="text-center">
                <div className="text-2xl font-bold" style={{ color: metric.color }}>
                  {metric.value}
                </div>
                <div className="text-sm text-gray-600">{metric.metric}</div>
                {index > 0 && (
                  <div className="text-xs text-gray-500 mt-1">
                    {((metric.value / analyticsData.emailPerformance[0].value) * 100).toFixed(1)}%
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default DashboardAnalytics;
