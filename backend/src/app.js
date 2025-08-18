const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const routes = require('./routes');
const errorHandler = require('./middleware/errorHandler');

const app = express();

// Security middleware
app.use(helmet());

// Import and use agentRoutes
const agentRoutes = require('./routes/agentRoutes');

app.use('/api', agentRoutes);



// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// CORS configuration
app.use(cors({
  origin: process.env.FRONTEND_URL,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Routes
app.use('/', routes);

// Global error handler 
app.use(errorHandler);

module.exports = app;
