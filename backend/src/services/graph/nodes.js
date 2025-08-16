// Logger replaced with console.log

// Start node that just passes state through
const startNode = async (state) => {
    console.log('Workflow started with keywords:', state.keywords);
    return {};
};

// Factory function to create agent nodes with error handling
function createAgentNode(agentName, agentFunc) {
    return async (state) => {
        console.log('Agent started:', agentName);
        try {
            const jobs = await agentFunc(state.keywords);
            console.log('Agent success:', agentName, jobs.length);
            return { [`${agentName}Jobs`]: jobs };
        } catch (error) {
            console.log('Agent error:', agentName, error.message);
            return { [`${agentName}Jobs`]: [] };
        }
    };
}

// Aggregator node to collect all jobs from all agents
const aggregateNode = async (state) => {
    console.log('Aggregate started');
    const allJobs = Object.keys(state)
        .filter((key) => key.endsWith('Jobs'))
        .flatMap((key) => state[key] || []);

    if (allJobs.length) {
        try {
            // Comment out for now if MongoDB is not set up
            // await Job.insertMany(allJobs);
            console.log('Aggregate success. Count:', allJobs.length);
        } catch (error) {
            console.log('DB error:', error.message);
        }
    } else {
        console.log('No jobs');
    }

    return { allJobs };
};

module.exports = {
    startNode,
    createAgentNode,
    aggregateNode
};
