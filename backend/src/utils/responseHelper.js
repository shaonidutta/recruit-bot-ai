/**
 * Standardized API Response Helper
 * Provides consistent response format across all endpoints
 */

/**
 * Send success response
 * @param {Object} res - Express response object
 * @param {Object} data - Response data
 * @param {string} message - Success message
 * @param {number} statusCode - HTTP status code (default: 200)
 */
const sendSuccess = (res, data = null, message = 'Success', statusCode = 200) => {
  return res.status(statusCode).json({
    success: true,
    message,
    data,
    error: null,
    timestamp: new Date().toISOString()
  });
};

/**
 * Send error response
 * @param {Object} res - Express response object
 * @param {string} message - Error message
 * @param {number} statusCode - HTTP status code (default: 500)
 * @param {Object} error - Error details (optional)
 */
const sendError = (res, message = 'Internal Server Error', statusCode = 500, error = null) => {
  return res.status(statusCode).json({
    success: false,
    message,
    data: null,
    error: error || message,
    timestamp: new Date().toISOString()
  });
};

/**
 * Send validation error response
 * @param {Object} res - Express response object
 * @param {Array|Object} errors - Validation errors
 * @param {string} message - Error message
 */
const sendValidationError = (res, errors, message = 'Validation failed') => {
  return res.status(400).json({
    success: false,
    message,
    data: null,
    error: {
      type: 'ValidationError',
      details: errors
    },
    timestamp: new Date().toISOString()
  });
};

/**
 * Send authentication error response
 * @param {Object} res - Express response object
 * @param {string} message - Error message
 */
const sendAuthError = (res, message = 'Authentication failed') => {
  return res.status(401).json({
    success: false,
    message,
    data: null,
    error: {
      type: 'AuthenticationError',
      details: message
    },
    timestamp: new Date().toISOString()
  });
};

/**
 * Send authorization error response
 * @param {Object} res - Express response object
 * @param {string} message - Error message
 */
const sendAuthorizationError = (res, message = 'Access denied') => {
  return res.status(403).json({
    success: false,
    message,
    data: null,
    error: {
      type: 'AuthorizationError',
      details: message
    },
    timestamp: new Date().toISOString()
  });
};

/**
 * Send not found error response
 * @param {Object} res - Express response object
 * @param {string} message - Error message
 */
const sendNotFoundError = (res, message = 'Resource not found') => {
  return res.status(404).json({
    success: false,
    message,
    data: null,
    error: {
      type: 'NotFoundError',
      details: message
    },
    timestamp: new Date().toISOString()
  });
};

module.exports = {
  sendSuccess,
  sendError,
  sendValidationError,
  sendAuthError,
  sendAuthorizationError,
  sendNotFoundError
};
