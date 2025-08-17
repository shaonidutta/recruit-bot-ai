require('dotenv').config();
const { buildGraph } = require('./graph/graphBuilder');
const { connectDB } = require('../utils/dbHelper');

// Build the graph once when the module loads
const graph = buildGraph();



async function runAgent(keywords = 'Software Engineer') {
    console.log('Starting with keywords:', keywords);

    try {
        // Uncomment this when you want to save to DB
        // await connectDB();

        const result = await graph.invoke({ keywords });
        console.log('Completed. Jobs count:', result.allJobs?.length || 0);
        // await mongoose.disconnect();
        return result;
    } catch (error) {
        console.log('Workflow error:', error);
        throw error;
    }
} module.exports = { runAgent };
