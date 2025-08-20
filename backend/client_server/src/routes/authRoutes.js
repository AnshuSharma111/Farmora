const express = require('express');
const authController = require('../controllers/authController');
const { verifyToken } = require('../middleware/authMiddleware');

const router = express.Router();

// Auth routes
router.post('/signup', authController.signUp);
router.post('/signin', authController.signIn);
router.post('/google', authController.googleAuth);
router.post('/signout', authController.signOut);
router.get('/user', verifyToken, authController.getCurrentUser);
router.get('/verify-email', authController.verifyEmail);
router.post('/send-verification', verifyToken, authController.sendVerificationEmail);

module.exports = router;
