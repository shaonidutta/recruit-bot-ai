import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { Button } from '../../../components/ui/Button';
import { cn } from '../../../utils/cn';
import { getMockData, simulateRealTimeUpdate } from '../../../data/mockData';

const JobCard = ({ job, isNew }) => {
  const [isVisible, setIsVisible] = useState(!isNew);

  useEffect(() => {
    if (isNew) {
      const timer = setTimeout(() => setIsVisible(true), 100);
      return () => clearTimeout(timer);
    }
  }, [isNew]);

  const getSourceColor = (source) => {
    const colors = {
      linkedin: 'bg-blue-100 text-blue-800',
      indeed: 'bg-indigo-100 text-indigo-800',
      glassdoor: 'bg-green-100 text-green-800',
      angellist: 'bg-gray-100 text-gray-800'
    };
    return colors[source] || 'bg-gray-100 text-gray-800';
  };

  const getMatchScoreColor = (score) => {
    if (score >= 90) return 'text-green-600 bg-green-50';
    if (score >= 80) return 'text-blue-600 bg-blue-50';
    if (score >= 70) return 'text-orange-600 bg-orange-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className={cn(
      "transform transition-all duration-500 ease-out",
      isVisible ? "translate-x-0 opacity-100" : "translate-x-full opacity-0"
    )}>
      <Card className={cn(
        "hover:shadow-md transition-all duration-200 cursor-pointer border-l-4",
        job.urgencyScore >= 90 ? "border-l-red-500" :
        job.urgencyScore >= 80 ? "border-l-orange-500" :
        "border-l-blue-500",
        isNew && "ring-2 ring-blue-500 ring-opacity-30 animate-pulse"
      )}>
        <CardContent className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <h3 className="font-semibold text-slate-900 text-sm">
                  {job.title}
                </h3>
                {isNew && (
                  <Badge variant="destructive" className="text-xs animate-pulse">
                    NEW
                  </Badge>
                )}
              </div>
              
              <p className="text-sm text-slate-600 mb-2">
                {job.company}
              </p>
              
              <div className="flex items-center space-x-4 text-xs text-slate-500">
                <span className="flex items-center">
                  📍 {job.location}
                </span>
                <span className="flex items-center">
                  💰 ${job.salary.min.toLocaleString()}-${job.salary.max.toLocaleString()}
                </span>
                <span className="flex items-center">
                  ⏰ {job.discoveredAt}
                </span>
              </div>
            </div>
            
            <div className="flex flex-col items-end space-y-2 ml-4">
              <Badge className={cn("text-xs font-medium", getSourceColor(job.source))}>
                {job.source.toUpperCase()}
              </Badge>
              
              <div className={cn(
                "px-2 py-1 rounded-full text-xs font-medium",
                getMatchScoreColor(job.matchScore)
              )}>
                🎯 {job.matchScore}%
              </div>
              
              <div className="text-xs text-slate-500">
                👤 {job.candidateCount} matches
              </div>
            </div>
          </div>
          
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100">
            <div className="flex items-center space-x-2">
              <div className={cn(
                "w-2 h-2 rounded-full",
                job.urgencyScore >= 90 ? "bg-red-500 animate-pulse" :
                job.urgencyScore >= 80 ? "bg-orange-500" :
                "bg-blue-500"
              )} />
              <span className="text-xs text-slate-500">
                Urgency: {job.urgencyScore}/100
              </span>
            </div>
            
            <div className="flex space-x-2">
              <Button size="sm" variant="outline" className="text-xs h-7">
                View Details
              </Button>
              <Button size="sm" className="text-xs h-7">
                Start Campaign
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const LiveJobFeed = () => {
  const [jobs, setJobs] = useState(getMockData('jobs') || []);

  // Simulate new jobs appearing every 45 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      const newJob = simulateRealTimeUpdate('newJob');
      if (newJob) {
        setJobs(prevJobs => [newJob, ...prevJobs.slice(0, 4)]); // Keep only 5 jobs
      }
    }, 45000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="col-span-full">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <CardTitle className="text-lg font-semibold">
              🔴 Live Job Discovery Feed
            </CardTitle>
          </div>
          <Badge variant="outline" className="text-xs">
            Auto-refresh: 30s
          </Badge>
        </div>
        <p className="text-sm text-slate-600">
          AI agents discovering jobs in real-time across multiple platforms
        </p>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {jobs.length > 0 ? (
          jobs.map((job) => (
            <JobCard key={job.id} job={job} isNew={job.isNew} />
          ))
        ) : (
          <div className="text-center py-8 text-slate-500">
            <div className="text-4xl mb-2">🔍</div>
            <p>AI agents are scanning for new opportunities...</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default LiveJobFeed;
