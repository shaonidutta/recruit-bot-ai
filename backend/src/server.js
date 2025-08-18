require('dotenv').config();
const app = require('./app');
const { startCronJobs } = require('./services/agentCron');

const { connectDB } = require('./config/database');

const PORT = process.env.PORT || 3000;

// Connect to database
connectDB();

app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
    console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`🔗 Frontend URL: ${process.env.FRONTEND_URL || 'http://localhost:5173'}`);
    console.log(`Server running on port ${PORT}`);

    // Initialize and start all scheduled cron jobs for the application.
    startCronJobs();
});
