import React from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import MetricsCards from './components/MetricsCards';
import WorkflowTrigger from './components/WorkflowTrigger';
import JobsList from './components/JobsList';
import { useJobs } from '../../hooks/useJobs';

const DashboardPage = () => {
  const { refetch } = useJobs();

  const handleWorkflowComplete = (result) => {
    // Refresh jobs data after workflow completion
    if (result && result.success) {
      // Give some time for jobs to be processed and stored
      setTimeout(() => {
        refetch();
      }, 2000);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Welcome Section */}
        <div className="relative bg-gradient-to-r from-blue-500 via-blue-600 to-purple-600 rounded-2xl p-8 text-white overflow-hidden shadow-xl">
          {/* Background pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-0 left-0 w-40 h-40 bg-white rounded-full -translate-x-1/2 -translate-y-1/2"></div>
            <div className="absolute bottom-0 right-0 w-32 h-32 bg-white rounded-full translate-x-1/2 translate-y-1/2"></div>
            <div className="absolute top-1/2 left-1/2 w-24 h-24 bg-white rounded-full -translate-x-1/2 -translate-y-1/2"></div>
          </div>

          <div className="relative z-10 flex items-center justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                  <span className="text-2xl">🤖</span>
                </div>
                <div>
                  <h1 className="text-3xl font-bold">
                    AI Recruitment Command Center
                  </h1>
                  <div className="flex items-center space-x-2 mt-1">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-blue-100 text-sm">System Active</span>
                  </div>
                </div>
              </div>
              <p className="text-blue-100 text-lg max-w-2xl">
                Your AI agents are working 24/7 to discover opportunities and connect talent with precision and speed
              </p>
            </div>
            <div className="hidden lg:block">
              <div className="text-8xl opacity-20 animate-pulse-slow">🚀</div>
            </div>
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="animate-fade-in" style={{animationDelay: '0.2s'}}>
          <MetricsCards />
        </div>

        {/* Action Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-fade-in" style={{animationDelay: '0.4s'}}>
          {/* Workflow Trigger */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden hover:shadow-xl transition-all duration-300">
            <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-4">
              <h2 className="text-xl font-bold text-white flex items-center">
                <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-lg">⚡</span>
                </div>
                Workflow Control
              </h2>
            </div>
            <div className="p-6">
              <WorkflowTrigger onWorkflowComplete={handleWorkflowComplete} />
            </div>
          </div>

          {/* Quick Stats */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-all duration-300">
            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white text-lg">📊</span>
              </div>
              Quick Insights
            </h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Today's Matches</span>
                <span className="font-bold text-green-600">+23</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Active Campaigns</span>
                <span className="font-bold text-blue-600">12</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-gray-600">Response Rate</span>
                <span className="font-bold text-purple-600">87%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Jobs List */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden animate-fade-in" style={{animationDelay: '0.6s'}}>
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900 flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white text-lg">💼</span>
              </div>
              Recent Job Discoveries
            </h2>
          </div>
          <div className="p-6">
            <JobsList />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
