const { runAgent } = require('../services/agentManager');

/**
 * @function triggerAgent
 * @description Controller to initiate the agent orchestration process.
 * It can be triggered via an HTTP request or a scheduled job.
 * @param {object} req - The Express request object.
 * @param {object} res - The Express response object.
 */
async function triggerAgent(req, res) {
    try {
        const result = await runAgent();
        res.status(200).json({ message: 'Agent orchestration completed successfully', data: result });
    } catch (error) {
        console.error('Error in triggerAgent controller:', error); // Log the full error on the server
        res.status(500).json({ message: 'Agent orchestration failed', error: error.message });
    }
}

module.exports = { triggerAgent };
