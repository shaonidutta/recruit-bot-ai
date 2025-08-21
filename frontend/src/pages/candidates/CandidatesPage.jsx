import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout.jsx';
import CandidatesFilter from '../../components/candidates/CandidatesFilter.jsx';
import CandidatesTable from '../../components/candidates/CandidatesTable.jsx';
import { Pagination } from '../../components/ui/Pagination.jsx';
import { Card } from '../../components/ui/Card.jsx';
import { Button } from '../../components/ui/Button.jsx';
import { RefreshCw, Download, UserPlus } from 'lucide-react';
import { candidatesService } from '../../api/services/candidatesService.js';
import { jobsService } from '../../api/services/jobsService.js';

const CandidatesPage = () => {
  const [candidates, setCandidates] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [filteredCandidates, setFilteredCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [filters, setFilters] = useState({
    search: '',
    location: '',
    skills: '',
    experience: '',
    jobFilter: ''
  });

  // Fetch candidates from API
  const fetchCandidates = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await candidatesService.getAllCandidates();
      
      if (response.success && response.data) {
        setCandidates(response.data);
        setFilteredCandidates(response.data);
      } else {
        setCandidates([]);
        setFilteredCandidates([]);
      }
    } catch (err) {
      console.error('Error fetching candidates:', err);
      setError('Failed to load candidates. Please try again.');
      setCandidates([]);
      setFilteredCandidates([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch jobs for filtering
  const fetchJobs = useCallback(async () => {
    try {
      const response = await jobsService.getAllJobs();
      if (response.success && response.data) {
        setJobs(response.data);
      }
    } catch (err) {
      console.error('Error fetching jobs:', err);
      // Don't show error for jobs as it's secondary data
    }
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchCandidates();
    fetchJobs();
  }, [fetchCandidates, fetchJobs]);

  // Filter candidates based on current filters
  const applyFilters = useCallback((candidatesList, currentFilters) => {
    let filtered = [...candidatesList];

    // Search filter
    if (currentFilters.search) {
      const searchTerm = currentFilters.search.toLowerCase();
      filtered = filtered.filter(candidate => 
        (candidate.name && candidate.name.toLowerCase().includes(searchTerm)) ||
        (candidate.first_name && candidate.first_name.toLowerCase().includes(searchTerm)) ||
        (candidate.last_name && candidate.last_name.toLowerCase().includes(searchTerm)) ||
        (candidate.firstName && candidate.firstName.toLowerCase().includes(searchTerm)) ||
        (candidate.lastName && candidate.lastName.toLowerCase().includes(searchTerm)) ||
        (candidate.email && candidate.email.toLowerCase().includes(searchTerm)) ||
        (candidate.title && candidate.title.toLowerCase().includes(searchTerm)) ||
        (candidate.current_role && candidate.current_role.toLowerCase().includes(searchTerm)) ||
        (candidate.currentPosition && candidate.currentPosition.toLowerCase().includes(searchTerm)) ||
        (candidate.skills && (
          Array.isArray(candidate.skills) 
            ? candidate.skills.some(skill => skill.toLowerCase().includes(searchTerm))
            : candidate.skills.toLowerCase().includes(searchTerm)
        ))
      );
    }

    // Location filter
    if (currentFilters.location) {
      const locationTerm = currentFilters.location.toLowerCase();
      filtered = filtered.filter(candidate => 
        candidate.location && candidate.location.toLowerCase().includes(locationTerm)
      );
    }

    // Skills filter
    if (currentFilters.skills) {
      const skillsTerm = currentFilters.skills.toLowerCase();
      filtered = filtered.filter(candidate => {
        if (!candidate.skills) return false;
        if (Array.isArray(candidate.skills)) {
          return candidate.skills.some(skill => skill.toLowerCase().includes(skillsTerm));
        }
        return candidate.skills.toLowerCase().includes(skillsTerm);
      });
    }

    // Experience filter
    if (currentFilters.experience) {
      filtered = filtered.filter(candidate => {
        // Handle both experience (string) and experience_years (number) fields
        if (candidate.experience) {
          return candidate.experience.toLowerCase() === currentFilters.experience.toLowerCase();
        }
        // Map experience_years to experience levels
        if (candidate.experience_years !== undefined && candidate.experience_years !== null) {
          let experienceLevel = '';
          if (candidate.experience_years <= 2) experienceLevel = 'entry';
          else if (candidate.experience_years <= 5) experienceLevel = 'mid';
          else if (candidate.experience_years <= 10) experienceLevel = 'senior';
          else experienceLevel = 'lead';
          return experienceLevel === currentFilters.experience.toLowerCase();
        }
        return false;
      });
    }

    // Job filter - this would filter candidates based on job requirements
    // For now, we'll implement a basic filter that matches candidates to job skills
    if (currentFilters.jobFilter) {
      const selectedJob = jobs.find(job => (job.id || job._id) === currentFilters.jobFilter);
      if (selectedJob && selectedJob.skills) {
        const jobSkills = Array.isArray(selectedJob.skills) 
          ? selectedJob.skills 
          : selectedJob.skills.split(',').map(s => s.trim());
        
        filtered = filtered.filter(candidate => {
          if (!candidate.skills) return false;
          const candidateSkills = Array.isArray(candidate.skills) 
            ? candidate.skills 
            : candidate.skills.split(',').map(s => s.trim());
          
          // Check if candidate has at least one matching skill
          return jobSkills.some(jobSkill => 
            candidateSkills.some(candidateSkill => 
              candidateSkill.toLowerCase().includes(jobSkill.toLowerCase()) ||
              jobSkill.toLowerCase().includes(candidateSkill.toLowerCase())
            )
          );
        });
      }
    }

    return filtered;
  }, [jobs]);

  // Apply filters when filters or candidates change
  useEffect(() => {
    const filtered = applyFilters(candidates, filters);
    setFilteredCandidates(filtered);
    setCurrentPage(1); // Reset to first page when filters change
  }, [candidates, filters, applyFilters]);

  // Handle filter changes
  const handleFilterChange = useCallback((newFilters) => {
    setFilters(newFilters);
  }, []);

  // Handle refresh
  const handleRefresh = () => {
    fetchCandidates();
    fetchJobs();
  };

  // Handle export
  const handleExport = async () => {
    try {
      const response = await candidatesService.exportCandidates(filters);
      
      // Create blob and download
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `candidates-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting candidates:', err);
      setError('Failed to export candidates. Please try again.');
    }
  };

  // Handle candidate click
  const handleCandidateClick = (candidate) => {
    // TODO: Navigate to candidate detail page or open modal
    console.log('Candidate clicked:', candidate);
  };

  // Calculate pagination
  const totalItems = filteredCandidates.length;
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentCandidates = filteredCandidates.slice(startIndex, endIndex);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Candidates</h1>
            <p className="text-gray-600 mt-1">
              Manage and filter candidate profiles with job matching
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
              disabled={filteredCandidates.length === 0}
              className="flex items-center space-x-2"
            >
              <Download className="h-4 w-4" />
              <span>Export</span>
            </Button>

            <Button
              className="flex items-center space-x-2"
            >
              <UserPlus className="h-4 w-4" />
              <span>Add Candidate</span>
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
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </Card>
        )}

        {/* Filter Component */}
        <CandidatesFilter
          onFilterChange={handleFilterChange}
          totalCandidates={filteredCandidates.length}
          jobs={jobs}
        />

        {/* Table Component */}
        <CandidatesTable
          candidates={currentCandidates}
          loading={loading}
          onCandidateClick={handleCandidateClick}
        />

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              totalItems={totalItems}
              itemsPerPage={itemsPerPage}
            />
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default CandidatesPage;