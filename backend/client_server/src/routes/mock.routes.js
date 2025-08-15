// This file adds mock handlers for testing routes without databases

const express = require('express');
const router = express.Router();

// Mock health endpoint for testing
router.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'mock-client-server',
    databases: {
      mongodb: 'mock'
    },
    auth: 'appwrite'
  });
});

// Mock user data
const mockUsers = [
  {
    _id: '1',
    appwriteId: 'mock_appwrite_id_123',
    name: 'Test User',
    email: 'test@example.com',
    location: 'Tamil Nadu',
    preferredLanguage: 'en'
  }
];

// Mock authentication middleware for testing
const mockAuth = (req, res, next) => {
  // Get token from header
  const token = req.headers.authorization?.split(' ')[1];
  
  if (token) {
    // In a real app, we would verify with Appwrite
    // For testing, we'll just set a mock user
    req.appwriteUser = {
      userId: 'mock_appwrite_id_123',
      name: 'Test User',
      email: 'test@example.com'
    };
    
    req.user = mockUsers[0];
    next();
  } else {
    res.status(401).json({ message: 'Unauthorized: No token provided' });
  }
};

// Mock authentication routes
router.post('/auth/sync-user', mockAuth, (req, res) => {
  const { location, preferredLanguage, farmDetails } = req.body;
  
  res.status(201).json({
    message: 'User synchronized successfully (mock)',
    user: {
      id: '1',
      appwriteId: 'mock_appwrite_id_123',
      name: req.appwriteUser.name,
      email: req.appwriteUser.email,
      location: location || 'Tamil Nadu',
      preferredLanguage: preferredLanguage || 'en',
      farmDetails: farmDetails || {}
    }
  });
});

router.get('/auth/verify', mockAuth, (req, res) => {
  res.json({
    isValid: true,
    user: {
      id: '1',
      appwriteId: 'mock_appwrite_id_123',
      name: req.appwriteUser.name,
      email: req.appwriteUser.email,
      location: 'Tamil Nadu',
      preferredLanguage: 'en'
    }
  });
});

// Mock user routes
router.get('/users/me', mockAuth, (req, res) => {
  res.json({
    id: '1',
    appwriteId: 'mock_appwrite_id_123',
    name: req.appwriteUser.name,
    email: req.appwriteUser.email,
    location: 'Tamil Nadu',
    preferredLanguage: 'en',
    farmDetails: {
      cropTypes: ['Rice', 'Wheat'],
      farmSize: '5 acres',
      soilType: 'Clay loam'
    },
    role: 'farmer',
    createdAt: new Date().toISOString()
  });
});

router.put('/users/me', mockAuth, (req, res) => {
  const { location, preferredLanguage, farmDetails } = req.body;
  
  res.json({
    message: 'Profile updated successfully (mock)',
    user: {
      id: '1',
      appwriteId: 'mock_appwrite_id_123',
      name: req.appwriteUser.name,
      email: req.appwriteUser.email,
      location: location || 'Tamil Nadu',
      preferredLanguage: preferredLanguage || 'en',
      farmDetails: farmDetails || {
        cropTypes: ['Rice', 'Wheat'],
        farmSize: '5 acres',
        soilType: 'Clay loam'
      }
    }
  });
});

router.get('/users/history', mockAuth, (req, res) => {
  res.json({
    previousQueries: [
      {
        question: 'How do I prevent pests in rice crops?',
        answer: 'To prevent pests in rice crops, you can use integrated pest management including crop rotation, resistant varieties, and biological controls...',
        timestamp: new Date(Date.now() - 86400000).toISOString() // 1 day ago
      },
      {
        question: 'Best time to plant wheat in Tamil Nadu?',
        answer: 'The best time to plant wheat in Tamil Nadu is typically during the Rabi season from October to December...',
        timestamp: new Date(Date.now() - 172800000).toISOString() // 2 days ago
      }
    ]
  });
});

// Mock query routes
router.post('/queries/ask', mockAuth, (req, res) => {
  const { question, location } = req.body;
  
  // Mock response based on question content
  let answer, intent;
  
  if (question.toLowerCase().includes('weather')) {
    answer = 'The forecast for Tamil Nadu shows sunny conditions with temperatures ranging from 25°C to 32°C for the next three days.';
    intent = 'weather';
  } else if (question.toLowerCase().includes('soil')) {
    answer = 'For optimal soil health in Tamil Nadu, maintain pH between 6.0-7.0, ensure good drainage, and incorporate organic matter regularly.';
    intent = 'soil_health';
  } else {
    answer = 'Based on your location in Tamil Nadu, I recommend focusing on crops like rice, sugarcane, and millets which are well-suited to the local climate and soil conditions.';
    intent = 'crop_choice';
  }
  
  res.json({
    id: Date.now().toString(),
    question,
    answer,
    sources: [
      'Tamil Nadu Agricultural University',
      'Indian Meteorological Department',
      'Local farming knowledge base'
    ],
    confidence: 0.85,
    intent,
    timestamp: new Date().toISOString()
  });
});

router.get('/queries/history', mockAuth, (req, res) => {
  res.json([
    {
      _id: '1',
      userId: '1',
      appwriteId: 'mock_appwrite_id_123',
      question: 'How do I prevent pests in rice crops?',
      answer: 'To prevent pests in rice crops, you can use integrated pest management including crop rotation, resistant varieties, and biological controls...',
      intent: 'pest_control',
      location: 'Tamil Nadu',
      language: 'en',
      sources: ['Tamil Nadu Agricultural University', 'FAO Rice Knowledge Bank'],
      confidence: 0.92,
      createdAt: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
      updatedAt: new Date(Date.now() - 86400000).toISOString()
    },
    {
      _id: '2',
      userId: '1',
      appwriteId: 'mock_appwrite_id_123',
      question: 'Best time to plant wheat in Tamil Nadu?',
      answer: 'The best time to plant wheat in Tamil Nadu is typically during the Rabi season from October to December...',
      intent: 'crop_choice',
      location: 'Tamil Nadu',
      language: 'en',
      sources: ['Indian Council of Agricultural Research', 'Local farming almanac'],
      confidence: 0.89,
      createdAt: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
      updatedAt: new Date(Date.now() - 172800000).toISOString()
    }
  ]);
});

// Add the feedback endpoint
router.post('/queries/:id/feedback', mockAuth, (req, res) => {
  const { id } = req.params;
  const { helpful, comments } = req.body;
  
  res.json({
    message: 'Feedback recorded successfully (mock)',
    query: {
      _id: id,
      userId: '1',
      appwriteId: 'mock_appwrite_id_123',
      question: 'How do I prevent pests in rice crops?',
      answer: 'To prevent pests in rice crops, you can use integrated pest management including crop rotation, resistant varieties, and biological controls...',
      feedback: {
        helpful,
        comments
      },
      intent: 'pest_control',
      location: 'Tamil Nadu',
      language: 'en',
      sources: ['Tamil Nadu Agricultural University', 'FAO Rice Knowledge Bank'],
      confidence: 0.92,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
  });
});

// Export the router
module.exports = router;
