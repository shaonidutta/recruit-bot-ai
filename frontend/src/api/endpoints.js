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
    LIST: '/api/v1/jobs',
    RECENT: '/api/v1/recent-jobs',
    BY_ID: (id) => `/api/v1/jobs/${id}`,
    STATS: '/api/v1/jobs/stats/summary',
    CREATE: '/api/v1/jobs',
    UPDATE: (id) => `/api/v1/jobs/${id}`,
  },

  // Candidates
  CANDIDATES: {
    LIST: '/api/v1/candidates',
    GET: (id) => `/api/v1/candidates/${id}`,
    CREATE: '/api/v1/candidates',
    UPDATE: (id) => `/api/v1/candidates/${id}`,
    DELETE: (id) => `/api/v1/candidates/${id}`,
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