// Application constants

export const ROUTES = {
  HOME: '/',
  LANDING: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  DASHBOARD: '/dashboard',
  JOBS: '/jobs',
  CANDIDATES: '/candidates',
  CAMPAIGNS: '/campaigns',
  ANALYTICS: '/analytics',
  SETTINGS: '/settings'
};

export const USER_ROLES = {
  ADMIN: 'admin',
  RECRUITER: 'recruiter',
  VIEWER: 'viewer'
};

export const AUTH_STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user'
};

export const API_STATUS = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error'
};

export const FORM_VALIDATION_MESSAGES = {
  REQUIRED: 'This field is required',
  INVALID_EMAIL: 'Please enter a valid email address',
  PASSWORD_TOO_SHORT: 'Password must be at least 6 characters long',
  PASSWORDS_DONT_MATCH: 'Passwords do not match',
  NAME_TOO_SHORT: 'Name must be at least 2 characters long'
};
