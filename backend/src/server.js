const app = require('./app');
const { startCronJobs } = require('./services/agentCron');

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);

    // Initialize and start all scheduled cron jobs for the application.
    startCronJobs();
});
