const authService = require('../services/authService');
const { verifyRefreshToken } = require('../utils/jwt');
const {
  sendSuccess,
  sendError,
  sendAuthError,
  sendNotFoundError
} = require('../utils/responseHelper');

/**
 * Authentication Controller
 * Handles user registration, login, logout, and token management
 */

/**
 * Register a new user
 * POST /api/v1/auth/register
 */
const register = async (req, res) => {
  try {
    const result = await authService.registerUser(req.body);
    sendSuccess(res, result, 'User registered successfully', 201);
  } catch (error) {
    console.error('Registration error:', error);
    if (error.message === 'User with this email already exists') {
      return sendError(res, error.message, 409);
    }
    sendError(res, 'Registration failed', 500, error.message);
  }
};

/**
 * Login user
 * POST /api/v1/auth/login
 */
const login = async (req, res) => {
  try {
    const { email, password } = req.body;
    const result = await authService.loginUser(email, password);
    sendSuccess(res, result, 'Login successful');
  } catch (error) {
    console.error('Login error:', error);
    if (error.message === 'Invalid email or password') {
      return sendAuthError(res, error.message);
    }
    sendError(res, 'Login failed', 500, error.message);
  }
};

/**
 * Refresh access token
 * POST /api/v1/auth/refresh
 */
const refreshToken = async (req, res) => {
  try {
    const { refreshToken } = req.body;

    // Verify refresh token
    const decoded = verifyRefreshToken(refreshToken);

    // Generate new tokens
    const tokens = await authService.refreshUserTokens(decoded.id);

    sendSuccess(res, tokens, 'Token refreshed successfully');

  } catch (error) {
    console.error('Token refresh error:', error);
    sendAuthError(res, 'Invalid refresh token');
  }
};

/**
 * Get current user profile
 * GET /api/v1/auth/me
 */
const getProfile = async (req, res) => {
  try {
    const userData = await authService.getUserProfile(req.user.id);
    sendSuccess(res, { user: userData }, 'Profile retrieved successfully');
  } catch (error) {
    console.error('Get profile error:', error);
    if (error.message === 'User not found') {
      return sendNotFoundError(res, error.message);
    }
    sendError(res, 'Failed to retrieve profile', 500, error.message);
  }
};



/**
 * Logout user (client-side token removal)
 * POST /api/v1/auth/logout
 */
const logout = async (req, res) => {
  try {
    // In a stateless JWT system, logout is handled client-side
    // This endpoint exists for consistency and future token blacklisting
    sendSuccess(res, null, 'Logout successful');
  } catch (error) {
    console.error('Logout error:', error);
    sendError(res, 'Logout failed', 500, error.message);
  }
};

module.exports = {
  register,
  login,
  refreshToken,
  getProfile,
  logout
};
