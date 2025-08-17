const express = require('express');
const app = express();

app.use(express.json());

// Import and use homeRoutes for "/"
const homeRoutes = require('./routes/homeRoutes');
const agentRoutes = require('./routes/agentRoutes');


app.use('/', homeRoutes);
app.use('/api', agentRoutes);


module.exports = app;
