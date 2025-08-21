import React from 'react';
import { ExternalLink, MapPin, Building, Clock, DollarSign } from 'lucide-react';
import { Card } from '../ui/Card.jsx';
import { Badge } from '../ui/Badge.jsx';
import { Button } from '../ui/Button.jsx';
import { LoadingSpinner } from '../ui/LoadingSpinner.jsx';

const JobsTable = ({ jobs, loading, onJobClick }) => {
  if (loading) {
    return (
      <Card className="p-8">
        <div className="flex items-center justify-center">
          <LoadingSpinner size="lg" />
          <span className="ml-3 text-gray-600">Loading jobs...</span>
        </div>
      </Card>
    );
  }

  if (!jobs || jobs.length === 0) {
    return (
      <Card className="p-8">
        <div className="text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No jobs found</h3>
          <p className="text-gray-600">Try adjusting your filters or search criteria.</p>
        </div>
      </Card>
    );
  }

  const formatSalary = (minSalary, maxSalary) => {
    if (!minSalary && !maxSalary) return 'Not specified';
    if (minSalary && maxSalary) {
      return `$${minSalary.toLocaleString()} - $${maxSalary.toLocaleString()}`;
    }
    if (minSalary) return `$${minSalary.toLocaleString()}+`;
    if (maxSalary) return `Up to $${maxSalary.toLocaleString()}`;
    return 'Not specified';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  const getJobTypeColor = (jobType) => {
    const colors = {
      'full-time': 'bg-green-100 text-green-800',
      'part-time': 'bg-blue-100 text-blue-800',
      'contract': 'bg-purple-100 text-purple-800',
      'freelance': 'bg-orange-100 text-orange-800',
      'internship': 'bg-yellow-100 text-yellow-800'
    };
    return colors[jobType?.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-4">
      {/* Desktop Table View */}
      <div className="hidden lg:block">
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Job Details
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Company
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Salary
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Posted
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {jobs.map((job) => (
                  <tr key={job._id || job.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <h3 className="text-sm font-semibold text-gray-900 mb-1">
                          {job.title || 'Untitled Job'}
                        </h3>
                        <p className="text-sm text-gray-600 line-clamp-2">
                          {job.description ? job.description.substring(0, 100) + '...' : 'No description available'}
                        </p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <Building className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-900">
                          {job.company || 'Unknown Company'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-900">
                          {job.location || 'Remote'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge className={getJobTypeColor(job.job_type)}>
                        {job.job_type || 'Full-time'}
                      </Badge>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <DollarSign className="h-4 w-4 text-gray-400 mr-1" />
                        <span className="text-sm text-gray-900">
                          {formatSalary(job.salary_min, job.salary_max)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-600">
                          {formatDate(job.created_at || job.posted_date)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onJobClick && onJobClick(job)}
                        >
                          View Details
                        </Button>
                        {job.url && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(job.url, '_blank')}
                          >
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* Mobile Card View */}
      <div className="lg:hidden space-y-4">
        {jobs.map((job) => (
          <Card key={job._id || job.id} className="p-4">
            <div className="space-y-3">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {job.title || 'Untitled Job'}
                  </h3>
                  <div className="flex items-center text-sm text-gray-600 mb-2">
                    <Building className="h-4 w-4 mr-1" />
                    <span>{job.company || 'Unknown Company'}</span>
                  </div>
                </div>
                <Badge className={getJobTypeColor(job.job_type)}>
                  {job.job_type || 'Full-time'}
                </Badge>
              </div>

              {/* Details */}
              <div className="space-y-2">
                <div className="flex items-center text-sm text-gray-600">
                  <MapPin className="h-4 w-4 mr-2" />
                  <span>{job.location || 'Remote'}</span>
                </div>
                
                <div className="flex items-center text-sm text-gray-600">
                  <DollarSign className="h-4 w-4 mr-2" />
                  <span>{formatSalary(job.salary_min, job.salary_max)}</span>
                </div>
                
                <div className="flex items-center text-sm text-gray-600">
                  <Clock className="h-4 w-4 mr-2" />
                  <span>{formatDate(job.created_at || job.posted_date)}</span>
                </div>
              </div>

              {/* Description */}
              {job.description && (
                <p className="text-sm text-gray-600 line-clamp-3">
                  {job.description.substring(0, 150)}...
                </p>
              )}

              {/* Actions */}
              <div className="flex items-center space-x-2 pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onJobClick && onJobClick(job)}
                  className="flex-1"
                >
                  View Details
                </Button>
                {job.url && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => window.open(job.url, '_blank')}
                  >
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default JobsTable;