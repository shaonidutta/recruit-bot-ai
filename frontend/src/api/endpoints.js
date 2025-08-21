export const ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    ME: '/api/v1/auth/profile',
    LOGOUT: '/api/v1/auth/logout',
    REFRESH: '/api/v1/auth/refresh',
  },

  // Jobs
  JOBS: {
    LIST: '/api/jobs',
    RECENT: '/api/recent-jobs',
    BY_ID: (id) => `/api/jobs/${id}`,
    STATS: '/api/jobs/stats/summary',
    CREATE: '/api/jobs',
    UPDATE: (id) => `/api/jobs/${id}`,
  },

  // Workflows
  WORKFLOWS: {
    RUN: '/api/v1/workflows/run',
    TEST: '/api/v1/workflows/test-no-auth',
  },

  // Health
  HEALTH: {
    BASIC: '/health',
    DATABASE: '/health/db',
    DETAILED: '/health/detailed',
  }
};
