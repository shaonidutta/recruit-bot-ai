const { z } = require('zod');

// Define the schema for the state object using Zod
const stateSchema = z.object({
    keywords: z.string(),
    linkedinJobs: z.array(z.any()).optional(),
    indeedJobs: z.array(z.any()).optional(),
    allJobs: z.array(z.any()).optional(),
});

const agentConfig = {
    linkedin: {
        name: 'linkedin',
        path: '../agents/linkedinAgent'
    },
    indeed: {
        name: 'indeed',
        path: '../agents/indeedAgent'
    }
};

module.exports = { stateSchema, agentConfig };
