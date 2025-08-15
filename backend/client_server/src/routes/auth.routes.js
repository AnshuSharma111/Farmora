const express = require('express');
const router = express.Router();
const User = require('../models/user.model');
const appwriteService = require('../services/appwrite.service');
const { authenticate } = require('../middlewares/auth.middleware');

/**
 * @route POST /farmora/api/auth/sync-user
 * @desc Sync Appwrite user with our database
 * @access Private (requires Appwrite token)
 */
router.post('/sync-user', authenticate, async (req, res, next) => {
  try {
    const { location, preferredLanguage, farmDetails } = req.body;
    
    // Check if user already exists in our database
    let user = await User.findOne({ appwriteId: req.appwriteUser.userId });
    
    if (user) {
      // Update existing user
      user.name = req.appwriteUser.name;
      user.email = req.appwriteUser.email;
      user.location = location || user.location;
      user.preferredLanguage = preferredLanguage || user.preferredLanguage;
      if (farmDetails) {
        user.farmDetails = { ...user.farmDetails, ...farmDetails };
      }
    } else {
      // Create new user in our database
      user = new User({
        appwriteId: req.appwriteUser.userId,
        name: req.appwriteUser.name,
        email: req.appwriteUser.email,
        location: location || '',
        preferredLanguage: preferredLanguage || 'en',
        farmDetails: farmDetails || {},
      });
    }
    
    await user.save();
    
    res.status(201).json({
      message: 'User synchronized successfully',
      user: {
        id: user._id,
        appwriteId: user.appwriteId,
        name: user.name,
        email: user.email,
        location: user.location,
        preferredLanguage: user.preferredLanguage,
        farmDetails: user.farmDetails,
      },
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route GET /farmora/api/auth/verify
 * @desc Verify an Appwrite token
 * @access Private (requires Appwrite token)
 */
router.get('/verify', authenticate, (req, res) => {
  res.json({ 
    isValid: true, 
    user: {
      id: req.user._id,
      appwriteId: req.appwriteUser.userId,
      name: req.user.name,
      email: req.user.email,
      // Include any additional fields from your local database if needed
      location: req.user.location,
      preferredLanguage: req.user.preferredLanguage,
    } 
  });
});

module.exports = router;
