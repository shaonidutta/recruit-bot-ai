import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout.jsx';
import JobsFilter from '../../components/jobs/JobsFilter.jsx';
import JobsTable from '../../components/jobs/JobsTable.jsx';
import { Pagination } from '../../components/ui/Pagination.jsx';
import { Card } from '../../components/ui/Card.jsx';
import { Button } from '../../components/ui/Button.jsx';
import { RefreshCw, Download } from 'lucide-react';
import { jobsService } from '../../api/services/jobsService.js';

const JobsPage = () => {
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [filters, setFilters] = useState({
    search: '',
    location: '',
    company: '',
    jobType: '',
    salaryRange: ''
  });

  // Fetch jobs from API
  const fetchJobs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await jobsService.getJobs();
      
      if (response.success && response.data && response.data.jobs) {
        setJobs(response.data.jobs);
        setFilteredJobs(response.data.jobs);
      } else {
        setJobs([]);
        setFilteredJobs([]);
      }
    } catch (err) {
      console.error('Error fetching jobs:', err);
      setError('Failed to load jobs. Please try again.');
      setJobs([]);
      setFilteredJobs([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  // Filter jobs based on current filters
  const applyFilters = useCallback((jobsList, currentFilters) => {
    let filtered = [...jobsList];

    // Search filter
    if (currentFilters.search) {
      const searchTerm = currentFilters.search.toLowerCase();
      filtered = filtered.filter(job => 
        (job.title && job.title.toLowerCase().includes(searchTerm)) ||
        (job.company && job.company.toLowerCase().includes(searchTerm)) ||
        (job.description && job.description.toLowerCase().includes(searchTerm))
      );
    }

    // Location filter
    if (currentFilters.location) {
      const locationTerm = currentFilters.location.toLowerCase();
      filtered = filtered.filter(job => 
        job.location && job.location.toLowerCase().includes(locationTerm)
      );
    }

    // Company filter
    if (currentFilters.company) {
      const companyTerm = currentFilters.company.toLowerCase();
      filtered = filtered.filter(job => 
        job.company && job.company.toLowerCase().includes(companyTerm)
      );
    }

    // Job type filter
    if (currentFilters.jobType) {
      filtered = filtered.filter(job => 
        job.job_type && job.job_type.toLowerCase() === currentFilters.jobType.toLowerCase()
      );
    }

    // Salary range filter
    if (currentFilters.salaryRange) {
      const [minSalary, maxSalary] = currentFilters.salaryRange.split('-').map(s => {
        if (s.includes('+')) return parseInt(s.replace('+', ''));
        return parseInt(s) || 0;
      });

      filtered = filtered.filter(job => {
        const jobMin = job.salary_min || 0;
        const jobMax = job.salary_max || 999999;
        
        if (currentFilters.salaryRange.includes('+')) {
          return jobMin >= minSalary || jobMax >= minSalary;
        }
        
        return (jobMin >= minSalary && jobMin <= maxSalary) ||
               (jobMax >= minSalary && jobMax <= maxSalary) ||
               (jobMin <= minSalary && jobMax >= maxSalary);
      });
    }

    return filtered;
  }, []);

  // Handle filter changes
  const handleFilterChange = useCallback((newFilters) => {
    setFilters(newFilters);
    const filtered = applyFilters(jobs, newFilters);
    setFilteredJobs(filtered);
    setCurrentPage(1); // Reset to first page when filters change
  }, [jobs, applyFilters]);

  // Handle page changes
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  // Handle job click (for future implementation)
  const handleJobClick = (job) => {
    console.log('Job clicked:', job);
    // TODO: Implement job details modal or navigation
  };

  // Handle refresh
  const handleRefresh = () => {
    fetchJobs();
  };

  // Handle export (placeholder)
  const handleExport = () => {
    console.log('Export jobs:', filteredJobs);
    // TODO: Implement CSV/Excel export functionality
  };

  // Calculate pagination
  const totalItems = filteredJobs.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentJobs = filteredJobs.slice(startIndex, endIndex);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Jobs</h1>
            <p className="text-gray-600 mt-1">
              Discover and manage job opportunities from various sources
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              onClick={handleRefresh}
              disabled={loading}
              className="flex items-center space-x-2"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </Button>
            
            <Button
              variant="outline"
              onClick={handleExport}
              disabled={filteredJobs.length === 0}
              className="flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Export</span>
            </Button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <Card className="p-4 bg-red-50 border-red-200">
            <div className="flex items-center">
              <div className="text-red-600">
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
              <div className="ml-auto">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setError(null)}
                  className="text-red-600 hover:text-red-800"
                >
                  ×
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Filters */}
        <JobsFilter 
          onFilterChange={handleFilterChange}
          totalJobs={filteredJobs.length}
        />

        {/* Jobs Table */}
        <JobsTable 
          jobs={currentJobs}
          loading={loading}
          onJobClick={handleJobClick}
        />

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
              totalItems={totalItems}
              itemsPerPage={itemsPerPage}
            />
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default JobsPage;