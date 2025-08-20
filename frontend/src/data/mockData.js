// 🗑️ EASILY DELETABLE MOCK DATA
// This file contains all mock data for the AI Recruitment Agent dashboard
// To switch to real APIs: 
// 1. Set VITE_USE_MOCK_DATA=false in .env
// 2. Delete this entire /data folder
// 3. Update service calls to use real API endpoints

// Dashboard Metrics (Real-time KPIs)
export const dashboardMetrics = {
  jobsDiscovered: {
    today: 247,
    change: +23,
    trend: 'up',
    percentage: 10.3
  },
  outreachSent: {
    today: 89,
    change: +12,
    trend: 'up',
    percentage: 15.6
  },
  responsesReceived: {
    today: 12,
    change: +4,
    trend: 'up',
    percentage: 50.0
  },
  matchesMade: {
    today: 34,
    change: +8,
    trend: 'up',
    percentage: 30.8
  }
};

// Live Job Discovery Feed
export const liveJobs = [
  {
    id: '1',
    title: 'Senior React Developer',
    company: 'TechCorp Inc',
    location: 'San Francisco, CA',
    salary: { min: 120000, max: 150000, currency: 'USD' },
    discoveredAt: '2 minutes ago',
    matchScore: 92,
    candidateCount: 3,
    source: 'linkedin',
    urgencyScore: 95,
    isNew: true
  },
  {
    id: '2',
    title: 'Frontend Engineer',
    company: 'StartupXYZ',
    location: 'Remote',
    salary: { min: 100000, max: 130000, currency: 'USD' },
    discoveredAt: '5 minutes ago',
    matchScore: 88,
    candidateCount: 2,
    source: 'indeed',
    urgencyScore: 82,
    isNew: true
  },
  {
    id: '3',
    title: 'Full Stack Developer',
    company: 'BigTech Corp',
    location: 'New York, NY',
    salary: { min: 140000, max: 170000, currency: 'USD' },
    discoveredAt: '8 minutes ago',
    matchScore: 85,
    candidateCount: 4,
    source: 'glassdoor',
    urgencyScore: 78,
    isNew: false
  },
  {
    id: '4',
    title: 'React Native Developer',
    company: 'MobileFirst Inc',
    location: 'Austin, TX',
    salary: { min: 110000, max: 140000, currency: 'USD' },
    discoveredAt: '12 minutes ago',
    matchScore: 90,
    candidateCount: 2,
    source: 'angellist',
    urgencyScore: 88,
    isNew: false
  },
  {
    id: '5',
    title: 'JavaScript Engineer',
    company: 'InnovateLab',
    location: 'Seattle, WA',
    salary: { min: 115000, max: 145000, currency: 'USD' },
    discoveredAt: '15 minutes ago',
    matchScore: 87,
    candidateCount: 3,
    source: 'linkedin',
    urgencyScore: 75,
    isNew: false
  }
];

// Match Pipeline Data
export const pipelineData = {
  stages: [
    { name: 'Jobs Discovered', count: 247, color: '#3B82F6' },
    { name: 'AI Matches Found', count: 89, color: '#10B981' },
    { name: 'Outreach Sent', count: 12, color: '#F59E0B' },
    { name: 'Responses Received', count: 8, color: '#8B5CF6' }
  ],
  conversionRates: [
    { from: 'Jobs Discovered', to: 'AI Matches Found', rate: 36.0 },
    { from: 'AI Matches Found', to: 'Outreach Sent', rate: 13.5 },
    { from: 'Outreach Sent', to: 'Responses Received', rate: 66.7 }
  ]
};

// Response Analytics (Email Campaign Performance)
export const responseAnalytics = {
  responseRate: {
    current: 15.2,
    industryAverage: 2.0,
    trend: 'up',
    change: +2.1
  },
  openRate: {
    current: 68.4,
    industryAverage: 45.0,
    trend: 'up',
    change: +5.2
  },
  avgResponseTime: {
    current: '4.2 hours',
    previous: '6.1 hours',
    trend: 'down', // down is good for response time
    improvement: 31.1
  },
  campaignStats: {
    totalCampaigns: 23,
    activeCampaigns: 8,
    completedCampaigns: 15,
    pausedCampaigns: 0
  }
};

// Recent Activity Timeline
export const recentActivity = [
  {
    id: '1',
    type: 'job_discovered',
    title: 'Job Discovered',
    description: 'Senior React Developer at TechCorp',
    timestamp: '2 minutes ago',
    icon: '🔍',
    color: 'blue'
  },
  {
    id: '2',
    type: 'match_found',
    title: 'Match Found',
    description: 'Alex Chen - 92% match for Frontend role',
    timestamp: '5 minutes ago',
    icon: '🎯',
    color: 'green'
  },
  {
    id: '3',
    type: 'email_sent',
    title: 'Email Sent',
    description: 'Outreach to Sarah Johnson @ TechCorp',
    timestamp: '8 minutes ago',
    icon: '📤',
    color: 'orange'
  },
  {
    id: '4',
    type: 'response_received',
    title: 'Response Received',
    description: 'Positive reply from hiring manager',
    timestamp: '15 minutes ago',
    icon: '📥',
    color: 'purple'
  },
  {
    id: '5',
    type: 'candidate_matched',
    title: 'Candidate Matched',
    description: 'Maria Rodriguez matched to 3 new positions',
    timestamp: '22 minutes ago',
    icon: '👤',
    color: 'indigo'
  }
];

// Source Performance Data
export const sourcePerformance = [
  { source: 'LinkedIn', jobs: 89, matches: 34, responseRate: 18.2, color: '#0077B5' },
  { source: 'Indeed', jobs: 67, matches: 28, responseRate: 14.1, color: '#2557A7' },
  { source: 'Glassdoor', jobs: 45, matches: 15, responseRate: 12.8, color: '#0CAA41' },
  { source: 'AngelList', jobs: 32, matches: 8, responseRate: 16.7, color: '#000000' },
  { source: 'Direct', jobs: 14, matches: 4, responseRate: 21.4, color: '#6366F1' }
];

// Mock API Response Simulator
export const simulateApiDelay = (ms = 1000) => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

// Environment-based data switching
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA !== 'false';

export const getMockData = (dataType) => {
  if (!USE_MOCK_DATA) return null;
  
  const mockDataMap = {
    metrics: dashboardMetrics,
    jobs: liveJobs,
    pipeline: pipelineData,
    analytics: responseAnalytics,
    activity: recentActivity,
    sources: sourcePerformance
  };
  
  return mockDataMap[dataType] || null;
};

// Real-time data simulation (for demo purposes)
export const simulateRealTimeUpdate = (dataType) => {
  const updates = {
    metrics: () => ({
      ...dashboardMetrics,
      jobsDiscovered: {
        ...dashboardMetrics.jobsDiscovered,
        today: dashboardMetrics.jobsDiscovered.today + Math.floor(Math.random() * 3)
      }
    }),
    newJob: () => ({
      id: Date.now().toString(),
      title: 'Software Engineer',
      company: 'TechStart Inc',
      location: 'Remote',
      salary: { min: 90000, max: 120000, currency: 'USD' },
      discoveredAt: 'Just now',
      matchScore: 85 + Math.floor(Math.random() * 10),
      candidateCount: Math.floor(Math.random() * 5) + 1,
      source: ['linkedin', 'indeed', 'glassdoor'][Math.floor(Math.random() * 3)],
      urgencyScore: 70 + Math.floor(Math.random() * 25),
      isNew: true
    })
  };
  
  return updates[dataType] ? updates[dataType]() : null;
};

export default {
  dashboardMetrics,
  liveJobs,
  pipelineData,
  responseAnalytics,
  recentActivity,
  sourcePerformance,
  getMockData,
  simulateApiDelay,
  simulateRealTimeUpdate
};
