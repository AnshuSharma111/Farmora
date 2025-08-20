const express = require('express');
const userProfileController = require('../controllers/userProfileController');
const { verifyToken } = require('../middleware/authMiddleware');

const router = express.Router();

// All routes require authentication
router.use(verifyToken);

// Create or update user profile
router.post('/', userProfileController.createOrUpdateProfile);

// Get user profile
router.get('/', userProfileController.getProfile);

module.exports = router;
