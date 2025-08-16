const { runAgent } = require('../services/agentManager');

async function triggerAgent(req, res) {
    try {
        await runAgent();
        res.status(200).json({ message: 'Agent orchestration completed successfully' });
    } catch (error) {
        res.status(500).json({ message: 'Agent orchestration failed', error: error.message });
    }
}

module.exports = { triggerAgent };
