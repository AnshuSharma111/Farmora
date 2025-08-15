const express = require('express');
const router = express.Router();
const { authenticate } = require('../middlewares/auth.middleware');
const User = require('../models/user.model');

/**
 * @route GET /farmora/api/users/me
 * @desc Get current user profile
 * @access Private
 */
router.get('/me', authenticate, async (req, res, next) => {
  try {
    // Find user by Appwrite ID
    const user = await User.findOne({ appwriteId: req.appwriteUser.userId });
    
    if (!user) {
      return res.status(404).json({ message: 'User profile not found. Please sync your account first.' });
    }
    
    res.json({
      id: user._id,
      appwriteId: user.appwriteId,
      name: user.name,
      email: user.email,
      location: user.location,
      preferredLanguage: user.preferredLanguage,
      farmDetails: user.farmDetails,
      role: user.role,
      createdAt: user.createdAt,
    });
  } catch (error) {
    next(error);
  }
});

/**
 * @route PUT /farmora/api/users/me
 * @desc Update user profile
 * @access Private
 */
router.put('/me', authenticate, async (req, res, next) => {
  try {
    const { location, preferredLanguage, farmDetails } = req.body;
    
    // Find user by Appwrite ID
    let user = await User.findOne({ appwriteId: req.appwriteUser.userId });
    
    if (!user) {
      return res.status(404).json({ message: 'User profile not found. Please sync your account first.' });
    }
    
    // Update user fields
    if (location) user.location = location;
    if (preferredLanguage) user.preferredLanguage = preferredLanguage;
    if (farmDetails) user.farmDetails = { ...user.farmDetails, ...farmDetails };
    
    // Name and email should be kept in sync with Appwrite
    user.name = req.appwriteUser.name;
    user.email = req.appwriteUser.email;
    
    await user.save();
    
    res.json({
      message: 'Profile updated successfully',
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
 * @route GET /farmora/api/users/history
 * @desc Get user's query history
 * @access Private
 */
router.get('/history', authenticate, async (req, res, next) => {
  try {
    // Find user by Appwrite ID
    const user = await User.findOne({ appwriteId: req.appwriteUser.userId });
    
    if (!user) {
      return res.status(404).json({ message: 'User profile not found. Please sync your account first.' });
    }
    
    res.json({
      previousQueries: user.previousQueries || [],
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
