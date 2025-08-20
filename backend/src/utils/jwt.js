const jwt = require('jsonwebtoken');

/**
 * JWT Utility Functions
 * Handles token generation, verification, and management
 */

/**
 * Generate JWT access token
 * @param {Object} payload - User data to encode in token
 * @returns {string} - JWT access token
 */
const generateAccessToken = (payload) => {
  return jwt.sign(
    payload,
    process.env.JWT_SECRET,
    { 
      expiresIn: process.env.JWT_EXPIRE || '15m',
      issuer: 'ai-recruitment-agent',
      audience: 'ai-recruitment-users'
    }
  );
};

/**
 * Generate JWT refresh token
 * @param {Object} payload - User data to encode in token
 * @returns {string} - JWT refresh token
 */
const generateRefreshToken = (payload) => {
  return jwt.sign(
    payload,
    process.env.JWT_REFRESH_SECRET,
    { 
      expiresIn: process.env.JWT_REFRESH_EXPIRE || '7d',
      issuer: 'ai-recruitment-agent',
      audience: 'ai-recruitment-users'
    }
  );
};

/**
 * Generate both access and refresh tokens
 * @param {Object} user - User object from database
 * @returns {Object} - Object containing both tokens
 */
const generateTokens = (user) => {
  const payload = {
    id: user._id,
    email: user.email,
    name: user.name
  };

  return {
    accessToken: generateAccessToken(payload),
    refreshToken: generateRefreshToken({ id: user._id })
  };
};

/**
 * Verify JWT access token
 * @param {string} token - JWT token to verify
 * @returns {Object} - Decoded token payload
 */
const verifyAccessToken = (token) => {
  try {
    return jwt.verify(token, process.env.JWT_SECRET, {
      issuer: 'ai-recruitment-agent',
      audience: 'ai-recruitment-users'
    });
  } catch (error) {
    throw new Error('Invalid or expired access token');
  }
};

/**
 * Verify JWT refresh token
 * @param {string} token - JWT refresh token to verify
 * @returns {Object} - Decoded token payload
 */
const verifyRefreshToken = (token) => {
  try {
    return jwt.verify(token, process.env.JWT_REFRESH_SECRET, {
      issuer: 'ai-recruitment-agent',
      audience: 'ai-recruitment-users'
    });
  } catch (error) {
    throw new Error('Invalid or expired refresh token');
  }
};

/**
 * Extract token from Authorization header
 * @param {string} authHeader - Authorization header value
 * @returns {string|null} - Extracted token or null
 */
const extractTokenFromHeader = (authHeader) => {
  if (!authHeader) return null;
  
  const parts = authHeader.split(' ');
  if (parts.length !== 2 || parts[0] !== 'Bearer') return null;
  
  return parts[1];
};

/**
 * Get token expiration time
 * @param {string} token - JWT token
 * @returns {Date|null} - Expiration date or null
 */
const getTokenExpiration = (token) => {
  try {
    const decoded = jwt.decode(token);
    return decoded && decoded.exp ? new Date(decoded.exp * 1000) : null;
  } catch (error) {
    return null;
  }
};

module.exports = {
  generateAccessToken,
  generateRefreshToken,
  generateTokens,
  verifyAccessToken,
  verifyRefreshToken,
  extractTokenFromHeader,
  getTokenExpiration
};
