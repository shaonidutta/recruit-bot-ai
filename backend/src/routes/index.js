const express = require('express');
const authRoutes = require('./authRoutes');
const healthRoutes = require('./healthRoutes');

const router = express.Router();

/**
 * API Routes Configuration
 * Aggregates all route modules
 */

// Health check routes (no versioning for health checks)
router.use('/health', healthRoutes);

// API v1 routes
router.use('/api/v1/auth', authRoutes);

// API documentation route
router.get('/api', (_, res) => {
  res.json({
    message: 'AI Recruitment Agent API',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      auth: '/api/v1/auth',
      documentation: '/api'
    },
    timestamp: new Date().toISOString()
  });
});

module.exports = router;
