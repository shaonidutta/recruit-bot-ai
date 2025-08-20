// cron/agentCron.js

const cron = require('node-cron');
const { runAgent } = require('./agentManager');

/**
 * @function runScheduledAgentOrchestration
 * @description Executes the agent orchestration logic directly for the cron job.
 * Calls the core business logic without HTTP layer abstractions.
 */
async function runScheduledAgentOrchestration() {
    console.log(`[CronJob] Starting agent orchestration at ${new Date().toISOString()}`);

    try {
        const result = await runAgent(); // Call the core business logic directly
        console.log(`[CronJob] Agent orchestration completed successfully. Jobs found: ${result.allJobs?.length || 0}`);
    } catch (error) {
        console.error(`[CronJob] Agent orchestration failed:`, error);
    }
}

/**
 * @function startCronJobs
 * @description Initializes and schedules all cron jobs for the application.
 * Reads the schedule and timezone from environment variables.
 * Only starts if CRON_AGENT_ENABLED is set to true.
 */
function startCronJobs() {
    const isEnabled = process.env.CRON_AGENT_ENABLED === 'true';

    if (!isEnabled) {
        console.log('[CronJob] Cron jobs are disabled via CRON_AGENT_ENABLED environment variable.');
        return;
    }

    const schedule = process.env.CRON_SCHEDULE || '0 2 * * *'; // Default: 2:00 AM daily
    const timezone = process.env.CRON_TIMEZONE || 'UTC';

    cron.schedule(
        schedule,
        runScheduledAgentOrchestration,
        {
            scheduled: true,
            timezone
        }
    );

    console.log(`[CronJob] Agent orchestration job scheduled with pattern "${schedule}" in timezone "${timezone}".`);
}

module.exports = { startCronJobs };
