const { verifyAccessToken, extractTokenFromHeader } = require('../utils/jwt');
const { sendAuthError } = require('../utils/responseHelper');
const User = require('../models/User');

/**
 * Authentication Middleware
 * Verifies JWT tokens and attaches user to request
 */

/**
 * Verify JWT token and authenticate user
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
const authenticateToken = async (req, res, next) => {
  try {
    // Extract token from Authorization header
    const token = extractTokenFromHeader(req.headers.authorization);
    
    if (!token) {
      return sendAuthError(res, 'Access token is required');
    }

    // Verify token
    const decoded = verifyAccessToken(token);
    
    // Find user in database
    const user = await User.findById(decoded.id);
    if (!user) {
      return sendAuthError(res, 'User not found');
    }

    // Attach user to request object
    req.user = {
      id: user._id,
      email: user.email,
      name: user.name
    };

    next();
  } catch (error) {
    console.error('Authentication error:', error.message);
    return sendAuthError(res, error.message);
  }
};

/**
 * Optional authentication middleware
 * Attaches user if token is valid, but doesn't require authentication
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
const optionalAuth = async (req, res, next) => {
  try {
    const token = extractTokenFromHeader(req.headers.authorization);
    
    if (token) {
      const decoded = verifyAccessToken(token);
      const user = await User.findById(decoded.id);
      
      if (user) {
        req.user = {
          id: user._id,
          email: user.email,
          name: user.name
        };
      }
    }
    
    next();
  } catch (error) {
    // Continue without authentication for optional auth
    next();
  }
};

/**
 * Check if user is authenticated
 * @param {Object} req - Express request object
 * @returns {boolean} - True if user is authenticated
 */
const isAuthenticated = (req) => {
  return req.user && req.user.id;
};

module.exports = {
  authenticateToken,
  optionalAuth,
  isAuthenticated
};
