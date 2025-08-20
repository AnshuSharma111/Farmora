const jwt = require('jsonwebtoken');
const { account } = require('../utils/appwrite');

exports.verifyToken = async (req, res, next) => {
    try {
        // Get token from header
        const authHeader = req.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return res.status(401).json({
                status: 'error',
                message: 'Authorization token required',
            });
        }

        const token = authHeader.split(' ')[1];

        // Verify token
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        
        // Check if user exists in AppWrite
        try {
            // Try to get user from AppWrite
            // This will throw an error if the user doesn't exist or session is invalid
            await account.get();
            
            // Set user ID in request
            req.userId = decoded.userId;
            next();
        } catch (error) {
            throw new Error('User not found or session invalid');
        }
    } catch (error) {
        console.error('Auth middleware error:', error);
        return res.status(401).json({
            status: 'error',
            message: 'Not authorized',
        });
    }
};
