const { sendError } = require('../utils/responseHelper');

/**
 * Global Error Handler Middleware
 * Catches and handles all unhandled errors
 */

/**
 * Handle Mongoose validation errors
 * @param {Object} error - Mongoose validation error
 * @returns {Object} - Formatted error response
 */
const handleValidationError = (error) => {
  const errors = Object.values(error.errors).map(err => ({
    field: err.path,
    message: err.message,
    value: err.value
  }));

  return {
    message: 'Validation failed',
    statusCode: 400,
    errors
  };
};

/**
 * Handle Mongoose duplicate key errors
 * @param {Object} error - Mongoose duplicate key error
 * @returns {Object} - Formatted error response
 */
const handleDuplicateKeyError = (error) => {
  const field = Object.keys(error.keyValue)[0];
  const value = error.keyValue[field];

  return {
    message: `${field.charAt(0).toUpperCase() + field.slice(1)} '${value}' already exists`,
    statusCode: 409,
    errors: [{
      field,
      message: `${field} must be unique`,
      value
    }]
  };
};

/**
 * Handle Mongoose cast errors
 * @param {Object} error - Mongoose cast error
 * @returns {Object} - Formatted error response
 */
const handleCastError = (error) => {
  return {
    message: `Invalid ${error.path}: ${error.value}`,
    statusCode: 400,
    errors: [{
      field: error.path,
      message: `Invalid ${error.path}`,
      value: error.value
    }]
  };
};

/**
 * Global error handler middleware
 * @param {Object} error - Error object
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
const errorHandler = (error, req, res, next) => {
  let formattedError = {
    message: error.message || 'Internal Server Error',
    statusCode: error.statusCode || 500,
    errors: null
  };

  // Log error for debugging
  console.error('Error:', {
    message: error.message,
    stack: error.stack,
    url: req.originalUrl,
    method: req.method,
    timestamp: new Date().toISOString()
  });

  // Handle specific error types
  if (error.name === 'ValidationError') {
    formattedError = handleValidationError(error);
  } else if (error.code === 11000) {
    formattedError = handleDuplicateKeyError(error);
  } else if (error.name === 'CastError') {
    formattedError = handleCastError(error);
  } else if (error.name === 'JsonWebTokenError') {
    formattedError = {
      message: 'Invalid token',
      statusCode: 401,
      errors: null
    };
  } else if (error.name === 'TokenExpiredError') {
    formattedError = {
      message: 'Token expired',
      statusCode: 401,
      errors: null
    };
  }

  // Send error response
  sendError(
    res,
    formattedError.message,
    formattedError.statusCode,
    formattedError.errors
  );
};

/**
 * Handle unhandled promise rejections
 */
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Close server & exit process
  process.exit(1);
});

/**
 * Handle uncaught exceptions
 */
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

module.exports = errorHandler;
