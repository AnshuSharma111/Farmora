const { account, ID } = require('../utils/appwrite');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');

// Helper function to generate JWT token
const generateToken = (userId) => {
    return jwt.sign({ userId }, process.env.JWT_SECRET, {
        expiresIn: '7d'
    });
};

// Format user data for response
const formatUserResponse = (user) => {
    return {
        id: user.$id,
        email: user.email,
        name: user.name,
        isEmailVerified: user.emailVerification,
        createdAt: user.registration,
        updatedAt: user.$updatedAt || user.registration,
    };
};

exports.signUp = async (req, res) => {
    try {
        const { email, password, name } = req.body;

        if (!email || !password || !name) {
            return res.status(400).json({
                status: 'error',
                message: 'Email, password, and name are required',
            });
        }

        // Create user in AppWrite
        const user = await account.create(
            ID.unique(),
            email,
            password,
            name
        );

        // Generate JWT token
        const token = generateToken(user.$id);

        // Return success response with user data and token
        return res.status(201).json({
            status: 'success',
            data: {
                user: formatUserResponse(user),
                token,
            },
        });
    } catch (error) {
        console.error('Sign up error:', error);
        
        // Handle common errors
        if (error.code === 409) {
            return res.status(409).json({
                status: 'error',
                message: 'User with this email already exists',
            });
        }

        return res.status(500).json({
            status: 'error',
            message: error.message || 'Sign up failed',
        });
    }
};

exports.signIn = async (req, res) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({
                status: 'error',
                message: 'Email and password are required',
            });
        }

        // Create email session in AppWrite
        const session = await account.createEmailSession(email, password);
        
        // Get user details
        const user = await account.get();

        // Generate JWT token
        const token = generateToken(user.$id);

        return res.status(200).json({
            status: 'success',
            data: {
                user: formatUserResponse(user),
                token,
            },
        });
    } catch (error) {
        console.error('Sign in error:', error);
        
        // Handle common errors
        if (error.code === 401) {
            return res.status(401).json({
                status: 'error',
                message: 'Invalid credentials',
            });
        }

        return res.status(500).json({
            status: 'error',
            message: error.message || 'Sign in failed',
        });
    }
};

exports.googleAuth = async (req, res) => {
    try {
        // For a complete implementation, you would need to:
        // 1. Receive the OAuth token from the client
        // 2. Use it to authenticate with AppWrite or verify with Google
        // 3. Create/get the user account
        
        // This is a simplified placeholder - in reality, you would:
        // const { idToken } = req.body;
        // const session = await account.createOAuth2Session('google', idToken, ...);
        // const user = await account.get();

        return res.status(501).json({
            status: 'error',
            message: 'Google sign-in not fully implemented yet',
        });
    } catch (error) {
        console.error('Google auth error:', error);
        return res.status(500).json({
            status: 'error',
            message: error.message || 'Google sign-in failed',
        });
    }
};

exports.signOut = async (req, res) => {
    try {
        // Get the session ID from the request
        // In a real implementation, you might extract this from authorization header
        const { sessionId } = req.body;
        
        if (sessionId) {
            // Delete specific session
            await account.deleteSession(sessionId);
        } else {
            // Delete current session (requires cookie/header auth setup)
            await account.deleteSession('current');
        }

        return res.status(200).json({
            status: 'success',
            message: 'Signed out successfully',
        });
    } catch (error) {
        console.error('Sign out error:', error);
        return res.status(500).json({
            status: 'error',
            message: error.message || 'Sign out failed',
        });
    }
};

exports.getCurrentUser = async (req, res) => {
    try {
        // Get current user
        // Note: This requires proper session/jwt validation middleware
        const user = await account.get();

        return res.status(200).json({
            status: 'success',
            data: {
                user: formatUserResponse(user),
            },
        });
    } catch (error) {
        console.error('Get current user error:', error);
        return res.status(401).json({
            status: 'error',
            message: 'Not authenticated',
        });
    }
};

exports.verifyEmail = async (req, res) => {
    try {
        const { userId, secret } = req.query;
        
        if (!userId || !secret) {
            return res.status(400).json({
                status: 'error',
                message: 'Missing verification parameters',
            });
        }
        
        // Complete email verification
        await account.updateVerification(userId, secret);
        
        return res.status(200).json({
            status: 'success',
            message: 'Email verified successfully',
        });
    } catch (error) {
        console.error('Email verification error:', error);
        return res.status(500).json({
            status: 'error',
            message: error.message || 'Email verification failed',
        });
    }
};

exports.sendVerificationEmail = async (req, res) => {
    try {
        // Create verification URL
        // Replace with your frontend verification URL
        const redirectUrl = `${req.protocol}://${req.get('host')}/auth/verify-email`;
        
        // Send verification email
        await account.createVerification(redirectUrl);
        
        return res.status(200).json({
            status: 'success',
            message: 'Verification email sent successfully',
        });
    } catch (error) {
        console.error('Send verification email error:', error);
        return res.status(500).json({
            status: 'error',
            message: error.message || 'Failed to send verification email',
        });
    }
};
