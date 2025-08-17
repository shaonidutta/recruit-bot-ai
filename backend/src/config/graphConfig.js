// Simplified state schema for Phase 1 (without zod dependency)
const stateSchema = {
    keywords: 'string',
    linkedinJobs: 'array',
    indeedJobs: 'array',
    allJobs: 'array'
};

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
