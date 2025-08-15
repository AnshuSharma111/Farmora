require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const mongoose = require('mongoose');

const authRoutes = require('./routes/auth.routes');
const userRoutes = require('./routes/user.routes');
const queryRoutes = require('./routes/query.routes');
const { errorHandler } = require('./middlewares/error.middleware');

// Initialize Appwrite service
const appwriteService = require('./services/appwrite.service');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 5001; // Changed from 5000 to 5001 to avoid conflicts

// For development, we'll skip MongoDB connection
const useMockMongoDB = true; // Set to true for development without MongoDB

if (!useMockMongoDB) {
  // Connect to MongoDB (using environment variables in a real setup)
  mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/farmora', {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
    .then(() => console.log('Connected to MongoDB'))
    .catch((err) => console.error('MongoDB connection error:', err));
} else {
  console.log('Using mock MongoDB for development - database operations will not persist');
  // We'll handle the routes without actual DB operations
}

// Apply basic security middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Add request logging
app.use(morgan('dev'));

// Apply rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per window
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// Basic root route
app.get('/farmora/api', (req, res) => {
  res.json({ message: 'Welcome to Farmora Client Server API' });
});

// Import mock routes for development without databases
const mockRoutes = require('./routes/mock.routes');

// Use mock routes for testing or real routes for production
if (useMockMongoDB) {
  console.log('Using mock routes for testing');
  app.use('/farmora/api', mockRoutes);
} else {
  // Health check endpoint
  app.get('/farmora/api/health', (req, res) => {
    res.json({ status: 'healthy', service: 'client-server' });
  });

  // Register route groups
  app.use('/farmora/api/auth', authRoutes);
  app.use('/farmora/api/users', userRoutes);
  app.use('/farmora/api/queries', queryRoutes);
}

// Error handling middleware
app.use(errorHandler);

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;
