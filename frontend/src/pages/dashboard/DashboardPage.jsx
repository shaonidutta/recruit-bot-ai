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
        {/* Enhanced Welcome Section */}
        <div className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-purple-700 to-indigo-800 rounded-2xl p-8 text-white shadow-2xl">
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-0 left-0 w-full h-full">
              <div className="w-full h-full" style={{
                backgroundImage: `radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0)`,
                backgroundSize: '20px 20px'
              }}></div>
            </div>
          </div>

          <div className="relative flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-4 mb-4">
                <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                  <span className="text-2xl">🤖</span>
                </div>
                <div>
                  <h1 className="text-4xl font-bold mb-1 bg-gradient-to-r from-white via-blue-100 to-cyan-100 bg-clip-text text-transparent">
                    AI Recruitment Command Center
                  </h1>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-blue-100 text-sm font-medium">Live System</span>
                  </div>
                </div>
              </div>

              <p className="text-blue-100 text-lg mb-6 max-w-2xl leading-relaxed">
                Your intelligent AI agents are working around the clock to discover opportunities,
                match talent, and automate outreach campaigns.
              </p>

              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2">
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-green-100">System Active</span>
                </div>
                <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2">
                  <div className="w-3 h-3 bg-yellow-400 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-yellow-100">AI Agents Ready</span>
                </div>
                <div className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2">
                  <div className="w-3 h-3 bg-cyan-400 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-cyan-100">Auto-Discovery</span>
                </div>
              </div>
            </div>

            {/* Floating AI Icon */}
            <div className="hidden lg:block">
              <div className="relative">
                <div className="w-32 h-32 bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-sm rounded-3xl flex items-center justify-center transform rotate-12 hover:rotate-0 transition-transform duration-500">
                  <span className="text-6xl transform -rotate-12">🤖</span>
                </div>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full animate-ping"></div>
                <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full"></div>
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
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
            <span>📊</span>
            <span>Analytics Dashboard</span>
          </h2>
          <DashboardAnalytics />
        </div>

        {/* Jobs and Matches Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-6">
          {/* Jobs List */}
          <div>
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
