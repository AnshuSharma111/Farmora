const UserProfile = require('../models/userProfile');

// Create or update a user profile
exports.createOrUpdateProfile = async (req, res) => {
  try {
    const userId = req.userId; // This comes from the auth middleware
    const { language, location, district, crops } = req.body;
    
    // Validate inputs
    if (!language || !location || !district || !crops) {
      return res.status(400).json({
        status: 'error',
        message: 'Missing required fields: language, location, district, crops',
      });
    }
    
    // Validate location format
    if (!Array.isArray(location) || location.length !== 2 || 
        typeof location[0] !== 'number' || typeof location[1] !== 'number') {
      return res.status(400).json({
        status: 'error',
        message: 'Location must be an array with [latitude, longitude]',
      });
    }
    
    // Validate crops format
    if (!Array.isArray(crops) || crops.length === 0) {
      return res.status(400).json({
        status: 'error',
        message: 'Crops must be a non-empty array',
      });
    }

    // Find existing profile or create new one
    let profile = await UserProfile.findOne({ userId });
    
    if (profile) {
      // Update existing profile
      profile.language = language;
      profile.location = location;
      profile.district = district;
      profile.crops = crops;
      
      await profile.save();
    } else {
      // Create new profile
      profile = await UserProfile.create({
        userId,
        language,
        location,
        district,
        crops,
      });
    }

    return res.status(200).json({
      status: 'success',
      data: {
        profile,
      },
    });
  } catch (error) {
    console.error('Create/update profile error:', error);
    return res.status(500).json({
      status: 'error',
      message: error.message || 'Error saving user profile',
    });
  }
};

// Get a user profile
exports.getProfile = async (req, res) => {
  try {
    const userId = req.userId; // This comes from the auth middleware
    
    const profile = await UserProfile.findOne({ userId });
    
    if (!profile) {
      return res.status(404).json({
        status: 'error',
        message: 'User profile not found',
      });
    }

    return res.status(200).json({
      status: 'success',
      data: {
        language: profile.language,
        location: profile.location,
        district: profile.district,
        crops: profile.crops,
      },
    });
  } catch (error) {
    console.error('Get profile error:', error);
    return res.status(500).json({
      status: 'error',
      message: error.message || 'Error retrieving user profile',
    });
  }
};
