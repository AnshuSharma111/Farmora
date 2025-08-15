const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const redisService = require('./redis.service');

/**
 * Service for JWT token generation and validation
 */
class TokenService {
  /**
   * Generate JWT access token
   * @param {Object} payload - Token payload
   * @returns {string} - JWT token
   */
  generateAccessToken(payload) {
    return jwt.sign(
      payload,
      process.env.JWT_SECRET || 'farmora-secret-key',
      { expiresIn: process.env.JWT_ACCESS_EXPIRES || '1h' }
    );
  }

  /**
   * Generate JWT refresh token
   * @param {Object} payload - Token payload
   * @returns {Object} - Object containing token and token ID
   */
  generateRefreshToken(payload) {
    // Add a unique ID to the token to enable revocation
    const jti = crypto.randomBytes(16).toString('hex');
    
    const token = jwt.sign(
      { ...payload, jti },
      process.env.JWT_REFRESH_SECRET || 'farmora-refresh-secret-key',
      { expiresIn: process.env.JWT_REFRESH_EXPIRES || '7d' }
    );
    
    return { token, jti };
  }

  /**
   * Verify access token
   * @param {string} token - JWT token
   * @returns {Object|null} - Decoded token payload or null if invalid
   */
  verifyAccessToken(token) {
    try {
      return jwt.verify(token, process.env.JWT_SECRET || 'farmora-secret-key');
    } catch (error) {
      return null;
    }
  }

  /**
   * Verify refresh token
   * @param {string} token - JWT refresh token
   * @returns {Object|null} - Decoded token payload or null if invalid
   */
  verifyRefreshToken(token) {
    try {
      return jwt.verify(token, process.env.JWT_REFRESH_SECRET || 'farmora-refresh-secret-key');
    } catch (error) {
      return null;
    }
  }

  /**
   * Create and store tokens for a user
   * @param {string} userId - User ID
   * @returns {Object} - Object with access and refresh tokens
   */
  async createTokens(userId) {
    // Create access token
    const accessToken = this.generateAccessToken({ userId });
    
    // Create refresh token
    const { token: refreshToken, jti } = this.generateRefreshToken({ userId });
    
    // Calculate expiry for refresh token storage
    const refreshExpiry = parseInt(process.env.JWT_REFRESH_EXPIRES || '7d') * 24 * 60 * 60;
    
    // Store refresh token in Redis
    await redisService.storeRefreshToken(
      userId, 
      jti, 
      refreshToken, 
      refreshExpiry
    );
    
    return {
      accessToken,
      refreshToken
    };
  }

  /**
   * Refresh the access token using a refresh token
   * @param {string} refreshToken - Refresh token
   * @returns {Object|null} - New tokens or null if refresh token is invalid
   */
  async refreshAccessToken(refreshToken) {
    // Verify refresh token
    const decoded = this.verifyRefreshToken(refreshToken);
    
    if (!decoded || !decoded.jti) {
      return null;
    }
    
    // Check if token exists in Redis
    const storedToken = await redisService.getRefreshToken(decoded.jti);
    if (!storedToken || storedToken !== refreshToken) {
      return null;
    }
    
    // Generate new access token
    const accessToken = this.generateAccessToken({ userId: decoded.userId });
    
    return {
      accessToken,
      refreshToken // Return the same refresh token
    };
  }

  /**
   * Revoke a refresh token (logout)
   * @param {string} refreshToken - Refresh token
   */
  async revokeRefreshToken(refreshToken) {
    const decoded = this.verifyRefreshToken(refreshToken);
    
    if (decoded && decoded.jti) {
      await redisService.deleteRefreshToken(decoded.userId, decoded.jti);
    }
  }

  /**
   * Logout from all devices
   * @param {string} userId - User ID
   */
  async revokeAllUserTokens(userId) {
    await redisService.revokeAllUserTokens(userId);
  }

  /**
   * Blacklist an access token (for logout)
   * @param {string} token - Access token
   */
  async blacklistAccessToken(token) {
    try {
      const decoded = this.verifyAccessToken(token);
      if (decoded) {
        // Extract expiration time from token
        const exp = decoded.exp;
        const now = Math.floor(Date.now() / 1000);
        const ttl = exp - now;
        
        if (ttl > 0) {
          await redisService.blacklistToken(token, ttl);
        }
      }
    } catch (error) {
      console.error('Error blacklisting token:', error);
    }
  }
}

// Create and export service instance
const tokenService = new TokenService();
module.exports = tokenService;
