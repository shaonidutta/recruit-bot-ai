import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { cn } from '../../../utils/cn';
import { getMockData, simulateRealTimeUpdate } from '../../../data/mockData';

const MetricCard = ({ title, value, change, trend, percentage, icon, color, isAnimating }) => {
  const [displayValue, setDisplayValue] = useState(0);

  // Animate counter on mount and value changes
  useEffect(() => {
    const duration = 1000; // 1 second
    const steps = 30;
    const increment = value / steps;
    let current = 0;
    
    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setDisplayValue(value);
        clearInterval(timer);
      } else {
        setDisplayValue(Math.floor(current));
      }
    }, duration / steps);

    return () => clearInterval(timer);
  }, [value]);

  const trendColor = trend === 'up' ? 'text-green-600' : 'text-red-600';
  const trendIcon = trend === 'up' ? '↗️' : '↘️';
  const bgGradient = color === 'blue' ? 'from-blue-500 to-blue-600' :
                    color === 'green' ? 'from-green-500 to-green-600' :
                    color === 'orange' ? 'from-orange-500 to-orange-600' :
                    'from-purple-500 to-purple-600';

  return (
    <Card className={cn(
      "relative overflow-hidden transition-all duration-300 hover:shadow-lg hover:scale-105",
      isAnimating && "ring-2 ring-blue-500 ring-opacity-50"
    )}>
      {/* Background gradient */}
      <div className={cn(
        "absolute top-0 right-0 w-20 h-20 bg-gradient-to-br opacity-10 rounded-full -mr-10 -mt-10",
        bgGradient
      )} />
      
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-slate-600">
          {title}
        </CardTitle>
        <span className="text-2xl">{icon}</span>
      </CardHeader>
      
      <CardContent>
        <div className="flex items-baseline space-x-2">
          <div className="text-3xl font-bold text-slate-900">
            {displayValue.toLocaleString()}
          </div>
          {change !== 0 && (
            <Badge 
              variant={trend === 'up' ? 'success' : 'destructive'}
              className="text-xs"
            >
              {trendIcon} {Math.abs(change)}
            </Badge>
          )}
        </div>
        
        <div className="flex items-center justify-between mt-2">
          <p className="text-xs text-slate-500">
            Today
          </p>
          {percentage && (
            <p className={cn("text-xs font-medium", trendColor)}>
              +{percentage}% from yesterday
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

const MetricsCards = () => {
  const [metrics, setMetrics] = useState(getMockData('metrics'));
  const [animatingCard, setAnimatingCard] = useState(null);

  // Simulate real-time updates every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      const updatedMetrics = simulateRealTimeUpdate('metrics');
      if (updatedMetrics) {
        setMetrics(updatedMetrics);
        setAnimatingCard('jobs'); // Animate the jobs card
        setTimeout(() => setAnimatingCard(null), 2000);
      }
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const metricsConfig = [
    {
      key: 'jobsDiscovered',
      title: 'Jobs Discovered',
      icon: '📋',
      color: 'blue'
    },
    {
      key: 'outreachSent',
      title: 'Outreach Sent',
      icon: '📤',
      color: 'green'
    },
    {
      key: 'responsesReceived',
      title: 'Responses Received',
      icon: '📥',
      color: 'orange'
    },
    {
      key: 'matchesMade',
      title: 'Matches Made',
      icon: '🎯',
      color: 'purple'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {metricsConfig.map((config) => {
        const metricData = metrics[config.key];
        return (
          <MetricCard
            key={config.key}
            title={config.title}
            value={metricData.today}
            change={metricData.change}
            trend={metricData.trend}
            percentage={metricData.percentage}
            icon={config.icon}
            color={config.color}
            isAnimating={animatingCard === config.key}
          />
        );
      })}
    </div>
  );
};

export default MetricsCards;
