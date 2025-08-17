// Temporarily simplified graph builder to avoid langgraph dependency issues
const { agentConfig } = require('../../config/graphConfig');

function buildGraph() {
    // Simplified graph structure for Phase 1
    const graph = {
        agents: {},
        workflow: ['start', 'agents', 'aggregate']
    };

    // Load agents
    try {
        Object.entries(agentConfig).forEach(([key, config]) => {
            try {
                graph.agents[key] = require(config.path);
                console.log('Loaded agent:', key);
            } catch (err) {
                console.warn(`Failed to load agent ${key}:`, err.message);
            }
        });
    } catch (err) {
        console.warn('Error loading agents:', err.message);
    }

    return graph;
}

function executeGraph(graph, input) {
    // Simple sequential execution for Phase 1
    const results = {
        input,
        agentResults: {},
        aggregatedJobs: []
    };

    // Execute each agent
    Object.entries(graph.agents).forEach(([agentName, agentFunc]) => {
        try {
            if (typeof agentFunc === 'function') {
                results.agentResults[agentName] = agentFunc(input);
            }
        } catch (err) {
            console.error(`Error executing agent ${agentName}:`, err.message);
            results.agentResults[agentName] = { error: err.message };
        }
    });

    return results;
}

module.exports = { buildGraph, executeGraph };
