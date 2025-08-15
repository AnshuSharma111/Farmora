const express = require('express');
const router = express.Router();
const axios = require('axios');
const { authenticate } = require('../middlewares/auth.middleware');
const Query = require('../models/query.model');
const User = require('../models/user.model');

// Environment variables (would be in .env in a real application)
const AI_SERVER_URL = process.env.AI_SERVER_URL || 'http://localhost:8000';

/**
 * @route POST /farmora/api/queries/ask
 * @desc Process a farmer query and get AI response
 * @access Private
 */
router.post('/ask', authenticate, async (req, res, next) => {
  try {
    const { question, location } = req.body;
    
    // Find user in our database
    const user = await User.findOne({ appwriteId: req.appwriteUser.userId });
    if (!user) {
      return res.status(404).json({ message: 'User profile not found. Please sync your account first.' });
    }
    
    // Create a new query object
    const query = new Query({
      userId: user._id,
      appwriteId: req.appwriteUser.userId,
      question,
      location: location || user.location,
      language: user.preferredLanguage || 'en',
    });
    
    // Call the AI server to process the query
    const aiResponse = await axios.post(`${AI_SERVER_URL}/farmora/api/ask`, {
      query: question,
      location: location || user.location,
      language: user.preferredLanguage || 'en',
      user_id: req.appwriteUser.userId, // Use Appwrite ID for consistent identification
    });
    
    // Update the query with AI response
    query.answer = aiResponse.data.answer;
    query.sources = aiResponse.data.sources;
    query.confidence = aiResponse.data.confidence;
    query.intent = aiResponse.data.intent || 'general';
    
    // Save the query to the database
    await query.save();
    
    // Add to user's previous queries
    await User.findByIdAndUpdate(user._id, {
      $push: {
        previousQueries: {
          question,
          answer: aiResponse.data.answer,
          timestamp: Date.now(),
        },
      },
    });
    
    res.json({
      id: query._id,
      question: query.question,
      answer: query.answer,
      sources: query.sources,
      confidence: query.confidence,
      intent: query.intent,
      timestamp: query.createdAt,
    });
  } catch (error) {
    console.error('Error processing query:', error.message);
    next(error);
  }
});

/**
 * @route GET /farmora/api/queries/history
 * @desc Get user's query history
 * @access Private
 */
router.get('/history', authenticate, async (req, res, next) => {
  try {
    // Find user in our database
    const user = await User.findOne({ appwriteId: req.appwriteUser.userId });
    if (!user) {
      return res.status(404).json({ message: 'User profile not found. Please sync your account first.' });
    }
    
    // Find queries for this user
    const queries = await Query.find({ userId: user._id })
      .sort({ createdAt: -1 })
      .limit(20);
    
    res.json(queries);
  } catch (error) {
    next(error);
  }
});

/**
 * @route POST /farmora/api/queries/:id/feedback
 * @desc Add feedback to a query
 * @access Private
 */
router.post('/:id/feedback', authenticate, async (req, res, next) => {
  try {
    const { id } = req.params;
    const { helpful, comments } = req.body;
    
    // Find user in our database
    const user = await User.findOne({ appwriteId: req.appwriteUser.userId });
    if (!user) {
      return res.status(404).json({ message: 'User profile not found. Please sync your account first.' });
    }
    
    // Update the query with feedback
    const query = await Query.findOneAndUpdate(
      { _id: id, userId: user._id },
      {
        feedback: {
          helpful,
          comments,
        },
      },
      { new: true }
    );
    
    if (!query) {
      return res.status(404).json({ message: 'Query not found' });
    }
    
    res.json({
      message: 'Feedback recorded successfully',
      query,
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
