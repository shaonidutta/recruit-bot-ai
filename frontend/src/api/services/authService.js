import { apiClient } from '../client.js';
import { ENDPOINTS } from '../endpoints.js';
import { handleApiError } from '../errorHandler.js';

export const authService = {
  // Login user
  login: async (email, password) => {
    try {
      const response = await apiClient.post(ENDPOINTS.AUTH.LOGIN, {
        email,
        password
      });

      // Store tokens and user in localStorage
      if (response.data.success && response.data.data) {
        const { user, tokens } = response.data.data;
        localStorage.setItem('accessToken', tokens.accessToken);
        localStorage.setItem('refreshToken', tokens.refreshToken);
        localStorage.setItem('user', JSON.stringify(user));
      }

      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Register user
  register: async (userData) => {
    try {
      const response = await apiClient.post(ENDPOINTS.AUTH.REGISTER, userData);

      // Store tokens and user in localStorage
      if (response.data.success && response.data.data) {
        const { user, tokens } = response.data.data;
        localStorage.setItem('accessToken', tokens.accessToken);
        localStorage.setItem('refreshToken', tokens.refreshToken);
        localStorage.setItem('user', JSON.stringify(user));
      }

      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  // Logout user
  logout: async () => {
    try {
      // Call backend logout endpoint
      await apiClient.post(ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error);
    } finally {
      // Always clear local storage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
    }
  },

  // Get current user from storage
  getCurrentUser: () => {
    const accessToken = localStorage.getItem('accessToken');
    const user = localStorage.getItem('user');

    if (accessToken && user) {
      return {
        accessToken,
        user: JSON.parse(user)
      };
    }
    return null;
  },

  // Verify token with backend
  verifyToken: async () => {
    try {
      const response = await apiClient.get(ENDPOINTS.AUTH.ME);
      if (response.data.success && response.data.data) {
        // Update localStorage with fresh user data
        localStorage.setItem('user', JSON.stringify(response.data.data.user));

        return {
          user: response.data.data.user,
          accessToken: localStorage.getItem('accessToken')
        };
      }
      return null;
    } catch (error) {
      console.error('Auth/me endpoint failed:', error);

      // If auth/me fails but we have valid tokens, try to use localStorage data
      const accessToken = localStorage.getItem('accessToken');
      const user = localStorage.getItem('user');

      if (accessToken && user) {
        try {
          return {
            user: JSON.parse(user),
            accessToken
          };
        } catch (parseError) {
          console.error('Failed to parse user data from localStorage:', parseError);
        }
      }

      // If everything fails, clear storage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      return null;
    }
  },

  // Refresh access token
  refreshToken: async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post(ENDPOINTS.AUTH.REFRESH, {
        refreshToken
      });

      if (response.data.success && response.data.data) {
        const { tokens } = response.data.data;
        localStorage.setItem('accessToken', tokens.accessToken);
        localStorage.setItem('refreshToken', tokens.refreshToken);
        return response.data.data;
      }

      throw new Error('Token refresh failed');
    } catch (error) {
      // Clear storage if refresh fails
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      throw error;
    }
  }
};
