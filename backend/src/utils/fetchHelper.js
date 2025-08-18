const axios = require('axios');

async function fetchJobs(agentEndpoint, keywords) {
    try {
        const url = `${process.env.SERVICES_BASE_URL}/${agentEndpoint}`;
        console.log(`Fetching jobs from: ${url}`);
        const response = await axios.get(
            url,
            { keywords }
        );
        console.log("🚀 ~ fetchJobs ~ response:", response.data)
        console.log(`${agentEndpoint} Agent found ${response.data.jobs.length} jobs`);
        return response.data.jobs;
    } catch (error) {
        console.error(`${agentEndpoint} Agent error:`, error.message);
        return [];
    }
}

module.exports = fetchJobs;
