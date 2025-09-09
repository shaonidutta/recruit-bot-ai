import React from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import MetricsCards from './components/MetricsCards';
import WorkflowTrigger from './components/WorkflowTrigger';
import ActivityTimeline from './components/ActivityTimeline';
import DashboardAnalytics from './components/DashboardAnalytics';
import JobsList from './components/JobsList';
import { useJobs } from '../../hooks/useJobs';

const DashboardPage = () => {
  const { jobs, loading, error, refetch, fetchRecentJobs, searchJobs, pagination } = useJobs();

  const handleWorkflowComplete = (result) => {
    // Refresh jobs data after workflow completion
    if (result && result.success) {
      // Give some time for jobs to be processed and stored
      setTimeout(() => {
        refetch();
      }, 2000);

      // Dispatch custom event for activity timeline
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
        {/* Enhanced Welcome Section */}
        <div className="bg-gradient-to-r from-blue-500 via-purple-600 to-indigo-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2 bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent">
                AI Recruitment Command Center
              </h1>
              <p className="text-blue-100 text-lg">
                Your AI agents are working 24/7 to discover opportunities and connect talent
              </p>
              <div className="flex items-center space-x-4 mt-3">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-sm text-blue-100">System Active</span>
                </div>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                  <span className="text-sm text-blue-100">AI Agents Ready</span>
                </div>
              </div>
            </div>
            <div className="text-6xl opacity-30 animate-pulse">🤖</div>
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
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <span>📊</span>
            <span>Analytics Dashboard</span>
          </h2>
          <DashboardAnalytics />
        </div>

        {/* Jobs List */}
        <div className="mt-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <span>💼</span>
            <span>Recent Job Discoveries</span>
          </h2>
          <JobsList
            jobs={jobs}
            loading={loading}
            error={error}
            fetchRecentJobs={fetchRecentJobs}
            searchJobs={searchJobs}
            pagination={pagination}
          />
        </div>

      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
