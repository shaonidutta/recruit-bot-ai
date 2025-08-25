import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../../components/ui/Card';
import { Button } from '../../../components/ui/Button';
import { Input } from '../../../components/ui/Input';
import { Badge } from '../../../components/ui/Badge';
import { LoadingSpinner } from '../../../components/ui/LoadingSpinner';

const JobCard = ({ job, onViewDetails }) => (
  <div className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-all duration-200 hover:border-slate-300">
    <div className="flex justify-between items-start mb-3">
      <div className="flex-1">
        <h3 className="font-semibold text-slate-900 text-lg mb-1 line-clamp-2">
          {job.title || 'Untitled Position'}
        </h3>
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <span className="flex items-center gap-1">
            <span>🏢</span>
            <span className="font-medium">{job.company || 'Unknown Company'}</span>
          </span>
          {job.via && (
            <Badge variant="outline" className="text-xs">
              {job.via}
            </Badge>
          )}
        </div>
      </div>
    </div>
    
    <div className="space-y-2 mb-4">
      {job.location && (
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <span>📍</span>
          <span>{job.location}</span>
        </div>
      )}
      
      {job.salary && (
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <span>💰</span>
          <span>{job.salary}</span>
        </div>
      )}

      {job.description && (
        <div className="text-sm text-slate-600 line-clamp-2">
          {job.description.substring(0, 150)}
          {job.description.length > 150 && '...'}
        </div>
      )}
    </div>

    <div className="flex justify-between items-center pt-3 border-t border-slate-100">
      <div className="text-xs text-slate-500">
        {job.created_at ? (
          <>Posted {new Date(job.created_at).toLocaleDateString()}</>
        ) : (
          'Recently posted'
        )}
      </div>
      <Button 
        variant="outline" 
        size="sm"
        onClick={() => onViewDetails(job)}
        className="text-xs"
      >
        View Details
      </Button>
    </div>
  </div>
);

const JobsList = ({ jobs, loading, error, searchJobs, fetchRecentJobs, pagination }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedJob, setSelectedJob] = useState(null);

  const handleSearch = async () => {
    if (searchTerm.trim()) {
      await searchJobs(searchTerm, { limit: 20 });
    } else {
      await fetchRecentJobs({ limit: 20 });
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleViewDetails = (job) => {
    setSelectedJob(job);
    // For now, just log the job details
    // In a full implementation, this would open a modal or navigate to a detail page
    console.log('Job details:', job);
    
    // You could also show an alert with job details for demo purposes
    alert(`Job Details:\n\nTitle: ${job.title}\nCompany: ${job.company}\nLocation: ${job.location || 'Not specified'}\nSalary: ${job.salary || 'Not specified'}\n\nDescription: ${job.description ? job.description.substring(0, 200) + '...' : 'No description available'}`);
  };

  const handleLoadMore = () => {
    // For now, just refresh recent jobs since we don't have fetchJobs
    // In a full implementation, this would handle pagination properly
    fetchRecentJobs({ limit: jobs.length + 10 });
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">📋</span>
            <div className="flex flex-col">
              <span>Recent Jobs</span>
              {pagination?.workflow_id && (
                <span className="text-xs text-slate-500 font-normal">
                  From workflow: {pagination.workflow_id}
                </span>
              )}
            </div>
          </div>
          <Badge variant="outline" className="text-sm">
            {jobs.length} jobs
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search Section */}
        <div className="flex gap-2">
          <Input
            placeholder="Search jobs by title, company, or keywords..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={handleKeyPress}
            className="flex-1"
          />
          <Button 
            onClick={handleSearch} 
            disabled={loading}
            className="min-w-[80px]"
          >
            {loading ? <LoadingSpinner size="sm" /> : 'Search'}
          </Button>
        </div>

        {/* Jobs List */}
        <div className="space-y-4">
          {loading && jobs.length === 0 ? (
            <div className="flex justify-center items-center py-12">
              <div className="text-center">
                <LoadingSpinner size="lg" />
                <p className="text-slate-500 mt-2">Loading jobs...</p>
              </div>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <div className="text-red-500 mb-2">❌</div>
              <p className="text-red-600 font-medium">Error loading jobs</p>
              <p className="text-red-500 text-sm">{error}</p>
              <Button
                variant="outline"
                onClick={() => fetchRecentJobs({ limit: 20 })}
                className="mt-4"
              >
                Try Again
              </Button>
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🔍</div>
              <p className="text-slate-600 font-medium mb-2">No jobs found</p>
              <p className="text-slate-500 text-sm mb-4">
                {searchTerm
                  ? `No jobs match "${searchTerm}". Try different keywords.`
                  : 'No recent jobs found. Try running the workflow to discover new jobs.'
                }
              </p>
              {!searchTerm && (
                <Button 
                  variant="outline"
                  onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                >
                  Run Job Discovery
                </Button>
              )}
            </div>
          ) : (
            <>
              <div className="grid gap-4">
                {jobs.map((job, index) => (
                  <JobCard 
                    key={job.id || job._id || index} 
                    job={job} 
                    onViewDetails={handleViewDetails}
                  />
                ))}
              </div>
              
              {/* Load More Button */}
              {jobs.length >= 10 && (
                <div className="text-center pt-4">
                  <Button 
                    variant="outline" 
                    onClick={handleLoadMore}
                    disabled={loading}
                  >
                    {loading ? (
                      <div className="flex items-center gap-2">
                        <LoadingSpinner size="sm" />
                        <span>Loading more...</span>
                      </div>
                    ) : (
                      'Load More Jobs'
                    )}
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default JobsList;
