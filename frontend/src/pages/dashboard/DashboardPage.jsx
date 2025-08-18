import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import MetricsCards from './components/MetricsCards';
import LiveJobFeed from './components/LiveJobFeed';
import MatchPipeline from './components/MatchPipeline';
import ResponseAnalytics from './components/ResponseAnalytics';
import { LoadingSpinner } from '../../components/ui/LoadingSpinner';

const DashboardPage = () => {
  const [isLoading, setIsLoading] = useState(true);

  // Simulate initial loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-4 text-slate-600">Loading AI Command Center...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold mb-2">
                Welcome to AI Recruitment Command Center
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

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 lg:gap-6">
          {/* Live Job Feed - Takes full width on mobile, 2 columns on desktop */}
          <div className="xl:col-span-2 order-2 xl:order-1">
            <LiveJobFeed />
          </div>

          {/* Right Sidebar - Analytics */}
          <div className="space-y-4 lg:space-y-6 order-1 xl:order-2">
            <MatchPipeline />
            <ResponseAnalytics />
          </div>
        </div>

        {/* Footer Stats */}
        <div className="bg-white rounded-lg p-6 border border-slate-200">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-2xl font-bold text-slate-900">500+</div>
              <p className="text-sm text-slate-600">Jobs/Day Target</p>
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-900">200+</div>
              <p className="text-sm text-slate-600">Outreaches/Day Target</p>
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-900">15%</div>
              <p className="text-sm text-slate-600">Response Rate Goal</p>
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-900">24/7</div>
              <p className="text-sm text-slate-600">AI Operation</p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
