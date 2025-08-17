const { StateGraph } = require('@langchain/langgraph');
const { stateSchema, agentConfig } = require('../../config/graphConfig');
const { startNode, createAgentNode, aggregateNode } = require('./nodes');

function buildGraph() {
    const sg = new StateGraph(stateSchema);

    // Load agents
    const agents = Object.entries(agentConfig).reduce((acc, [key, config]) => {
        acc[key] = require(config.path);
        return acc;
    }, {});

    // Add nodes
    sg.addNode('start', startNode);

    Object.entries(agents).forEach(([agentName, agentFunc]) => {
        console.log('Added node for agent:', agentName);
        sg.addNode(agentName, createAgentNode(agentName, agentFunc));
    });

    sg.addNode('aggregate', aggregateNode);

    // Set entry point
    sg.setEntryPoint('start');

    // Add edges
    Object.keys(agents).forEach(agentName => {
        sg.addEdge('start', agentName);
        sg.addEdge(agentName, 'aggregate');
    });

    // Compile
    console.log('Compiling graph...');
    return sg.compile();
}

module.exports = { buildGraph };
