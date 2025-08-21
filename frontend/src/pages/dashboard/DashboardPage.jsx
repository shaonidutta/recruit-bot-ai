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
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold mb-2">
                AI Recruitment Command Center
              </h1>
              <p className="text-blue-100">
                Your AI agents are working 24/7 to discover opportunities and connect talent
              </p>
            </div>
            <div className="text-6xl opacity-20">🤖</div>
          </div>
        </div>

        {/* Metrics Cards */}
        <MetricsCards />

        {/* Workflow Trigger */}
        <WorkflowTrigger onWorkflowComplete={handleWorkflowComplete} />

        {/* Jobs List */}
        <JobsList />

      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
