const axios = require('axios');

async function fetchJobs(agentEndpoint, keywords) {
    try {
        const base = process.env.SERVICES_BASE_URL;
        // Normalize join (avoid double slashes)
        const url = `${String(base).replace(/\/$/, '')}/${String(agentEndpoint).replace(/^\//, '')}`;
        console.log(`Fetching jobs from: ${url}`);
        const response = await axios.get(url, {
            params: { keywords },
            timeout: 15000,
        });
        console.log("🚀 ~ fetchJobs ~ response:", response.data)
        console.log(`${agentEndpoint} Agent found ${response.data.jobs.length} jobs`);
        return response.data.jobs;
    } catch (error) {
        console.error(`${agentEndpoint} Agent error:`, error?.response?.data || error.message);
        return [];
    }
}

module.exports = fetchJobs;
