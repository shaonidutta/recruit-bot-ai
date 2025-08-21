export const ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/profile',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
  },

  // Jobs
  JOBS: {
    LIST: '/jobs',
    GET: (id) => `/jobs/${id}`,
    CREATE: '/jobs',
    UPDATE: (id) => `/jobs/${id}`,
    DELETE: (id) => `/jobs/${id}`,
  },

  // Candidates
  CANDIDATES: {
    LIST: '/candidates',
    GET: (id) => `/candidates/${id}`,
    CREATE: '/candidates',
    UPDATE: (id) => `/candidates/${id}`,
    DELETE: (id) => `/candidates/${id}`,
  },

};
