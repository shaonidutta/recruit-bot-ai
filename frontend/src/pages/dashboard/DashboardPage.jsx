import React, { useRef } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import MetricsCards from './components/MetricsCards';
import WorkflowTrigger from './components/WorkflowTrigger';
import ActivityTimeline from './components/ActivityTimeline';
import DashboardAnalytics from './components/DashboardAnalytics';
import JobsList from './components/JobsList';
import { RecentMatchesList } from '../../components/ui/MatchesList';
import { useJobs } from '../../hooks/useJobs';

const DashboardPage = () => {
  const { jobs, loading, error, refetch, fetchRecentJobs, searchJobs, pagination } = useJobs();
  const matchesListRef = useRef(null);

  const handleWorkflowComplete = (result) => {
    // Refresh jobs data after workflow completion
    if (result && result.success) {
      // Give some time for jobs to be processed and stored
      setTimeout(() => {
        refetch();
        // Refresh matches list if it exists
        if (matchesListRef.current && matchesListRef.current.refresh) {
          matchesListRef.current.refresh();
        }
      }, 2000);

      // Dispatch custom event for activity timeline and matches
      const event = new CustomEvent('workflowComplete', {
        detail: {
          keywords: result.keywords || 'Unknown',
          result: result.data || result
        }
      });
      window.dispatchEvent(event);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Clean Header Section */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">AI Recruitment Dashboard</h1>
                  <p className="text-gray-600 text-sm">Manage your recruitment workflow and analytics</p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 bg-green-50 px-3 py-1.5 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-green-700 text-sm font-medium">System Online</span>
              </div>
              <div className="flex items-center space-x-2 bg-blue-50 px-3 py-1.5 rounded-full">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-blue-700 text-sm font-medium">AI Active</span>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Metrics Cards */}
        <MetricsCards />

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Workflow Trigger - Takes 2 columns */}
          <div className="lg:col-span-2">
            <WorkflowTrigger onWorkflowComplete={handleWorkflowComplete} />
          </div>

          {/* Activity Timeline - Takes 1 column */}
          <div className="lg:col-span-1">
            <ActivityTimeline />
          </div>
        </div>

        {/* Dashboard Analytics */}
        <div className="mt-6">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Analytics Overview</h2>
            <p className="text-sm text-gray-600">Track your recruitment performance and metrics</p>
          </div>
          <DashboardAnalytics />
        </div>

        {/* Jobs and Matches Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-6">
          {/* Jobs List */}
          <div>
            <div className="mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Recent Jobs</h2>
              <p className="text-sm text-gray-600">Latest job opportunities discovered by AI agents</p>
            </div>
            <JobsList
              jobs={jobs}
              loading={loading}
              error={error}
              fetchRecentJobs={fetchRecentJobs}
              searchJobs={searchJobs}
              pagination={pagination}
            />
          </div>

          {/* Recent Matches */}
          <div>
            <RecentMatchesList
              ref={matchesListRef}
              limit={5}
              onMatchSelect={(match) => {
                console.log('Match selected:', match);
                // TODO: Open match details modal or navigate to match page
              }}
            />
          </div>
        </div>

      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
