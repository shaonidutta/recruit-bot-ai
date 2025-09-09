import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { LoadingSpinner } from '../../../components/ui/LoadingSpinner';
import { analyticsService } from '../../../api/services/analyticsService';
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch real analytics data
  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await analyticsService.getDashboardAnalytics(7);

        if (response.success) {
          setAnalyticsData({
            jobTrends: response.data.job_trends || [],
            sourceBreakdown: response.data.source_breakdown || []
          });
        } else {
          throw new Error(response.message || 'Failed to fetch analytics data');
        }
      } catch (err) {
        console.error('Error fetching analytics:', err);
        setError(err.message);

        // Fallback to minimal mock data on error
        setAnalyticsData({
          jobTrends: [],
          sourceBreakdown: [
            { name: 'LinkedIn', value: 50, color: '#0077B5' },
            { name: 'Indeed', value: 30, color: '#2557A7' },
            { name: 'Google Jobs', value: 20, color: '#4285F4' }
          ]
        });
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();

    // Refresh data every 60 seconds
    const interval = setInterval(fetchAnalyticsData, 60000);
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

  // Show loading state
  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="lg:col-span-2">
          <CardContent className="flex items-center justify-center py-12">
            <LoadingSpinner />
            <span className="ml-2 text-gray-600">Loading analytics data...</span>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="lg:col-span-2">
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="text-red-600 mb-2">⚠️ Error loading analytics</div>
              <div className="text-sm text-gray-600">{error}</div>
              <div className="text-xs text-gray-500 mt-2">Showing fallback data</div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Job Discovery Trends */}
      <Card className="lg:col-span-2 bg-gradient-to-br from-white to-blue-50 border-0 shadow-xl">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-green-500 to-purple-500" />
        <CardHeader className="relative">
          <CardTitle className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-green-500 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white text-lg">📈</span>
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
                Job Discovery Trends
              </span>
              <Badge variant="outline" className="ml-3 bg-blue-50 text-blue-700 border-blue-200">
                Last 7 days {loading && '(Updating...)'}
              </Badge>
            </div>
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
      <Card className="bg-gradient-to-br from-white to-purple-50 border-0 shadow-xl">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 to-pink-500" />
        <CardHeader className="relative">
          <CardTitle className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white text-lg">🎯</span>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              Job Sources
            </span>
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



    </div>
  );
};

export default DashboardAnalytics;
