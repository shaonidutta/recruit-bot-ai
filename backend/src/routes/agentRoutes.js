const express = require('express');
const router = express.Router();
const { triggerAgent } = require('../controllers/agentController');
const { 
    runAgent, 
    runGoogleJobsAgent, 
    getQueueStats, 
    getAgentStatus, 
    clearQueue, 
    pauseProcessing 
} = require('../services/agentManager');

// Original agent endpoint
router.post('/agent', triggerAgent);

// New workflow endpoints
router.post('/discover', async (req, res) => {
    try {
        const { keywords, location, options } = req.body;
        const result = await runAgent(keywords, location, options);
        res.json(result);
    } catch (error) {
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

// Google Jobs specific endpoint
router.post('/google-jobs', async (req, res) => {
    try {
        const result = await runGoogleJobsAgent(req.body);
        res.json(result);
    } catch (error) {
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

// Queue management endpoints
router.get('/queue/stats', (req, res) => {
    try {
        const stats = getQueueStats();
        res.json({ success: true, stats });
    } catch (error) {
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

router.post('/queue/clear', (req, res) => {
    try {
        const result = clearQueue();
        res.json(result);
    } catch (error) {
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

router.post('/queue/pause', (req, res) => {
    try {
        const result = pauseProcessing();
        res.json(result);
    } catch (error) {
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

// Agent status endpoint
router.get('/status', (req, res) => {
    try {
        const status = getAgentStatus();
        res.json({ success: true, status });
    } catch (error) {
        res.status(500).json({ 
            success: false, 
            error: error.message 
        });
    }
});

// Integration test endpoint for Python services
router.post('/test-integration', async (req, res) => {
    try {
        const axios = require('axios');
        const { job_title = 'software engineer' } = req.body;
        
        // Test Python services health
        const healthResponse = await axios.get('http://services:8000/');
        
        // Test Indeed job discovery
        const jobsResponse = await axios.post('http://services:8000/api/discover/indeed', {
            job_title: job_title
        });
        
        res.json({
            success: true,
            integration_test: {
                python_services_health: healthResponse.data,
                indeed_jobs_count: jobsResponse.data.length,
                sample_jobs: jobsResponse.data.slice(0, 2)
            }
        });
    } catch (error) {
        res.status(500).json({ 
            success: false, 
            error: error.message,
            integration_test: 'failed'
        });
    }
});

module.exports = router;
