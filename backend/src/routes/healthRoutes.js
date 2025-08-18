const express = require('express');
const mongoose = require('mongoose');
const { isConnected, getConnectionStatus } = require('../config/database');
const User = require('../models/User');

const router = express.Router();

/**
 * Health check endpoint
 * GET /api/health
 */
router.get('/', async (req, res) => {
  try {
    const health = {
      status: 'OK',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      database: {
        connected: isConnected(),
        status: getConnectionStatus()
      }
    };

    // Test database connection by counting users
    if (isConnected()) {
      try {
        const userCount = await User.countDocuments();
        health.database.userCount = userCount;
        health.database.testQuery = 'SUCCESS';
      } catch (error) {
        health.database.testQuery = 'FAILED';
        health.database.error = error.message;
      }
    }

    res.status(200).json(health);
  } catch (error) {
    res.status(500).json({
      status: 'ERROR',
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * Database status endpoint
 * GET /api/health/db
 */
router.get('/db', async (req, res) => {
  try {
    if (!isConnected()) {
      return res.status(503).json({
        status: 'DISCONNECTED',
        message: 'Database is not connected',
        connectionStatus: getConnectionStatus()
      });
    }

    // Test database operations
    const dbTest = {
      status: 'CONNECTED',
      connectionStatus: getConnectionStatus(),
      tests: {}
    };

    // Test 1: Count users
    try {
      const userCount = await User.countDocuments();
      dbTest.tests.userCount = {
        status: 'SUCCESS',
        count: userCount
      };
    } catch (error) {
      dbTest.tests.userCount = {
        status: 'FAILED',
        error: error.message
      };
    }

    // Test 2: Database ping
    try {
      await mongoose.connection.db.admin().ping();
      dbTest.tests.ping = {
        status: 'SUCCESS',
        message: 'Database ping successful'
      };
    } catch (error) {
      dbTest.tests.ping = {
        status: 'FAILED',
        error: error.message
      };
    }

    res.status(200).json(dbTest);
  } catch (error) {
    res.status(500).json({
      status: 'ERROR',
      message: error.message
    });
  }
});

module.exports = router;
