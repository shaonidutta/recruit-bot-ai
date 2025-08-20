export const ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/me',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
  },
  
  // Jobs
  JOBS: {
    LIST: '/jobs',
    BY_ID: (id) => `/jobs/${id}`,
    MATCHES: (id) => `/jobs/${id}/matches`,
    DISCOVER: '/jobs/discover',
  },
  
  // Candidates
  CANDIDATES: {
    LIST: '/candidates',
    BY_ID: (id) => `/candidates/${id}`,
    CREATE: '/candidates',
    UPDATE: (id) => `/candidates/${id}`,
  },
  
  // Dashboard
  DASHBOARD: {
    METRICS: '/dashboard/metrics',
    ACTIVITY: '/dashboard/activity',
  }
};
