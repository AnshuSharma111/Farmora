const User = require('../models/user.model');
const appwriteService = require('../services/appwrite.service');

/**
 * Authentication middleware to verify Appwrite JWT tokens
 */
const authenticate = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ 
        message: 'Authentication required. No token provided.' 
      });
    }
    
    const token = authHeader.split(' ')[1];
    
    if (!token) {
      return res.status(401).json({ 
        message: 'Authentication required. Invalid token format.' 
      });
    }
    
    // Verify the token with Appwrite
    const userData = await appwriteService.verifyToken(token);
    
    if (!userData) {
      return res.status(401).json({ message: 'Invalid or expired token.' });
    }
    
    // Optionally find the user in your MongoDB if you're storing additional data
    // This step can be removed if you don't need local user data
    let user = null;
    try {
      user = await User.findOne({ appwriteId: userData.userId });
    } catch (err) {
      console.log('MongoDB error or not configured, continuing with Appwrite user data');
    }
    
    // Add user object and token to the request
    // If no MongoDB user exists, use the Appwrite user data
    req.user = user || {
      _id: userData.userId,
      appwriteId: userData.userId,
      name: userData.name,
      email: userData.email,
      // Default values for any other fields your app expects
      location: '',
      preferredLanguage: 'en',
    };
    
    req.appwriteUser = userData;
    req.token = token;
    next();
  } catch (error) {
    next(error);
  }
};

module.exports = {
  authenticate
};
