import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { AnimatedCounter } from '../../../components/ui/AnimatedCounter';

/**
 * Activity Timeline Component
 * Shows recent workflow activities and system events
 */
const ActivityTimeline = () => {
  const [activities, setActivities] = useState([]);

  // Load activities from localStorage on mount
  useEffect(() => {
    const savedActivities = localStorage.getItem('workflow_activities');
    if (savedActivities) {
      try {
        const parsed = JSON.parse(savedActivities);
        setActivities(parsed.slice(0, 10)); // Keep only last 10 activities
      } catch (error) {
        console.error('Error parsing saved activities:', error);
      }
    }
  }, []);

  // Listen for new workflow completions
  useEffect(() => {
    const handleWorkflowComplete = (event) => {
      const { keywords, result } = event.detail;
      
      const newActivity = {
        id: Date.now(),
        type: 'workflow_complete',
        title: `Workflow Completed: ${keywords}`,
        description: `Discovered ${result?.jobs_discovered || 0} jobs, sent ${result?.emails_sent || 0} emails`,
        timestamp: new Date(),
        data: result,
        icon: '🚀',
        color: 'green'
      };

      setActivities(prev => {
        const updated = [newActivity, ...prev].slice(0, 10);
        localStorage.setItem('workflow_activities', JSON.stringify(updated));
        return updated;
      });
    };

    // Listen for custom workflow events
    window.addEventListener('workflowComplete', handleWorkflowComplete);
    
    return () => {
      window.removeEventListener('workflowComplete', handleWorkflowComplete);
    };
  }, []);

  // Add some demo activities if none exist
  useEffect(() => {
    if (activities.length === 0) {
      const demoActivities = [
        {
          id: 1,
          type: 'system_start',
          title: 'System Initialized',
          description: 'AI Recruitment Agent started successfully',
          timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
          icon: '⚡',
          color: 'blue'
        },
        {
          id: 2,
          type: 'database_connect',
          title: 'Database Connected',
          description: 'Successfully connected to MongoDB database',
          timestamp: new Date(Date.now() - 1000 * 60 * 25), // 25 minutes ago
          icon: '🗄️',
          color: 'green'
        },
        {
          id: 3,
          type: 'agents_ready',
          title: 'AI Agents Ready',
          description: 'Job discovery and matching agents initialized',
          timestamp: new Date(Date.now() - 1000 * 60 * 20), // 20 minutes ago
          icon: '🤖',
          color: 'purple'
        }
      ];
      
      setActivities(demoActivities);
      localStorage.setItem('workflow_activities', JSON.stringify(demoActivities));
    }
  }, [activities.length]);

  const formatTimeAgo = (date) => {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
  };

  const getActivityColor = (color) => {
    const colors = {
      green: 'bg-green-100 text-green-800 border-green-200',
      blue: 'bg-blue-100 text-blue-800 border-blue-200',
      purple: 'bg-purple-100 text-purple-800 border-purple-200',
      orange: 'bg-orange-100 text-orange-800 border-orange-200',
      red: 'bg-red-100 text-red-800 border-red-200'
    };
    return colors[color] || colors.blue;
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <span className="text-lg">📊</span>
          <span>Recent Activity</span>
          <Badge variant="outline" className="ml-auto">
            Live
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {activities.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">🔄</div>
              <p>No recent activity</p>
              <p className="text-sm">Run a workflow to see activity here</p>
            </div>
          ) : (
            activities.map((activity, index) => (
              <div key={activity.id} className="relative">
                {/* Timeline line */}
                {index < activities.length - 1 && (
                  <div className="absolute left-6 top-12 w-0.5 h-8 bg-gray-200" />
                )}
                
                <div className="flex items-start space-x-3">
                  {/* Activity icon */}
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-lg border-2 ${getActivityColor(activity.color)}`}>
                    {activity.icon}
                  </div>
                  
                  {/* Activity content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {activity.title}
                      </h4>
                      <span className="text-xs text-gray-500 flex-shrink-0">
                        {formatTimeAgo(new Date(activity.timestamp))}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-600 mt-1">
                      {activity.description}
                    </p>
                    
                    {/* Activity data */}
                    {activity.data && (
                      <div className="flex items-center space-x-4 mt-2">
                        {activity.data.jobs_discovered && (
                          <div className="flex items-center space-x-1 text-xs">
                            <span className="text-blue-600 font-medium">
                              <AnimatedCounter value={activity.data.jobs_discovered} />
                            </span>
                            <span className="text-gray-500">jobs</span>
                          </div>
                        )}
                        {activity.data.emails_sent && (
                          <div className="flex items-center space-x-1 text-xs">
                            <span className="text-green-600 font-medium">
                              <AnimatedCounter value={activity.data.emails_sent} />
                            </span>
                            <span className="text-gray-500">emails</span>
                          </div>
                        )}
                        {activity.data.processing_time && (
                          <div className="flex items-center space-x-1 text-xs">
                            <span className="text-purple-600 font-medium">
                              {activity.data.processing_time}s
                            </span>
                            <span className="text-gray-500">duration</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
        
        {/* Clear activities button */}
        {activities.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <button
              onClick={() => {
                setActivities([]);
                localStorage.removeItem('workflow_activities');
              }}
              className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
            >
              Clear activity history
            </button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ActivityTimeline;
