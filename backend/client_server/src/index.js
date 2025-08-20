const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const connectDB = require('./utils/db');
const authRoutes = require('./routes/authRoutes');
const userProfileRoutes = require('./routes/userProfileRoutes');

// Load environment variables
require('dotenv').config();

// Connect to MongoDB
connectDB();

// Initialize express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/profile', userProfileRoutes);

// Root route
app.get('/', (req, res) => {
    res.json({
        status: 'success',
        message: 'Farmora API Server is running',
    });
});

// Handle 404 routes
app.use('*', (req, res) => {
    res.status(404).json({
        status: 'error',
        message: 'Route not found',
    });
});

// Global error handler
app.use((err, req, res, next) => {
    console.error('Unhandled Error:', err);
    res.status(500).json({
        status: 'error',
        message: 'Something went wrong!',
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
