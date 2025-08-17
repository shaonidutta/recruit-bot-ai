require('dotenv').config();
const { buildGraph, executeGraph } = require('./graph/graphBuilder');
const { connectDB } = require('../utils/dbHelper');
const { jobQueue } = require('./queueManager');
const GoogleJobsAgent = require('./agents/googleJobsAgent');

// Build the graph once when the module loads
const graph = buildGraph();

// Initialize agents
const googleJobsAgent = new GoogleJobsAgent();

/**
 * Run the main agent workflow
 * @param {string} keywords - Search keywords
 * @param {string} location - Search location
 * @param {Object} options - Additional options
 */
async function runAgent(keywords = 'Software Engineer', location = 'United States', options = {}) {
    console.log(`[AgentManager] Starting job discovery for: ${keywords} in ${location}`);

    try {
        // Connect to database
        await connectDB();

        // Run the simplified graph workflow
        const result = executeGraph(graph, { 
            keywords, 
            location,
            ...options 
        });
        
        console.log(`[AgentManager] Graph workflow completed. Jobs found: ${result.allJobs?.length || 0}`);
        
        return {
            success: true,
            totalJobs: result.allJobs?.length || 0,
            jobs: result.allJobs || [],
            queueStats: jobQueue.getStats(),
            workflow: 'graph'
        };
    } catch (error) {
        console.error('[AgentManager] Workflow error:', error);
        throw error;
    }
}

/**
 * Run Google Jobs agent specifically
 * @param {Object} params - Search parameters
 */
async function runGoogleJobsAgent(params) {
    console.log('[AgentManager] Running Google Jobs agent');
    
    try {
        await connectDB();
        const result = await googleJobsAgent.searchJobs(params);
        
        return {
            ...result,
            queueStats: jobQueue.getStats()
        };
    } catch (error) {
        console.error('[AgentManager] Google Jobs agent error:', error);
        throw error;
    }
}

/**
 * Get queue statistics
 */
function getQueueStats() {
    return jobQueue.getStats();
}

/**
 * Get agent status
 */
function getAgentStatus() {
    return {
        graph: {
            status: 'ready',
            type: 'workflow'
        },
        googleJobs: googleJobsAgent.getStatus(),
        queue: jobQueue.getStats()
    };
}

/**
 * Clear the job queue
 */
function clearQueue() {
    jobQueue.clearQueue();
    return { success: true, message: 'Queue cleared' };
}

/**
 * Pause job processing
 */
function pauseProcessing() {
    jobQueue.pauseProcessing();
    return { success: true, message: 'Processing paused' };
}

module.exports = { 
    runAgent,
    runGoogleJobsAgent,
    getQueueStats,
    getAgentStatus,
    clearQueue,
    pauseProcessing,
    jobQueue
};
