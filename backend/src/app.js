const express = require('express');
const app = express();

app.use(express.json());

// Import and use homeRoutes for "/"
const homeRoutes = require('./routes/homeRoutes');
app.use('/', homeRoutes);

module.exports = app;
