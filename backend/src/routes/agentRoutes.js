const express = require('express');
const router = express.Router();
const { triggerAgent } = require('../controllers/agentController');

router.post('/agent', triggerAgent);

module.exports = router;
