const Redis = require('ioredis');
const { promisify } = require('util');

// Mock Redis client for development
const useMockRedis = true; // Set to true for development without Redis

let redisClient;

if (useMockRedis) {
  console.log('Using mock Redis client for development');
  
  // Create a simple in-memory store
  const inMemoryStore = new Map();
  
  // Mock Redis client
  redisClient = {
    set: (key, value) => {
      inMemoryStore.set(key, value);
      return Promise.resolve('OK');
    },
    get: (key) => {
      return Promise.resolve(inMemoryStore.get(key) || null);
    },
    del: (key) => {
      inMemoryStore.delete(key);
      return Promise.resolve(1);
    },
    expire: (key, seconds) => {
      // Simple expiration simulation
      setTimeout(() => {
        inMemoryStore.delete(key);
      }, seconds * 1000);
      return Promise.resolve(1);
    },
    sadd: (key, value) => {
      const set = inMemoryStore.get(key) || new Set();
      set.add(value);
      inMemoryStore.set(key, set);
      return Promise.resolve(1);
    },
    srem: (key, value) => {
      const set = inMemoryStore.get(key);
      if (set) {
        set.delete(value);
      }
      return Promise.resolve(1);
    },
    smembers: (key) => {
      const set = inMemoryStore.get(key);
      return Promise.resolve(set ? Array.from(set) : []);
    },
    on: (event, callback) => {
      // No-op for mock
      return redisClient;
    }
  };
} else {
  // Initialize real Redis client
  try {
    redisClient = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

    redisClient.on('connect', () => {
      console.log('Redis client connected');
    });

    redisClient.on('error', (err) => {
      console.error('Redis client error:', err);
    });
  } catch (error) {
    console.error('Failed to initialize Redis client:', error);
    process.exit(1);
  }
}

/**
 * Redis service for token management and caching
 */
class RedisService {
  constructor(client) {
    this.client = client;
  }

  /**
   * Store a refresh token in Redis with expiration
   * @param {string} userId - User ID associated with the token
   * @param {string} tokenId - Unique identifier for the token
   * @param {string} token - Refresh token
   * @param {number} expiryInSeconds - Token expiry in seconds
   */
  async storeRefreshToken(userId, tokenId, token, expiryInSeconds) {
    const key = `refresh_token:${tokenId}`;
    await this.client.set(key, token);
    await this.client.expire(key, expiryInSeconds);
    
    // Associate token with user (for multi-device logout)
    await this.client.sadd(`user_tokens:${userId}`, tokenId);
  }

  /**
   * Check if a refresh token exists and is valid
   * @param {string} tokenId - Unique identifier for the token
   * @returns {Promise<string|null>} - Returns the token or null if not found
   */
  async getRefreshToken(tokenId) {
    return await this.client.get(`refresh_token:${tokenId}`);
  }

  /**
   * Delete a refresh token (logout for a single device)
   * @param {string} userId - User ID associated with the token
   * @param {string} tokenId - Unique identifier for the token
   */
  async deleteRefreshToken(userId, tokenId) {
    await this.client.del(`refresh_token:${tokenId}`);
    await this.client.srem(`user_tokens:${userId}`, tokenId);
  }

  /**
   * Revoke all refresh tokens for a user (logout from all devices)
   * @param {string} userId - User ID
   */
  async revokeAllUserTokens(userId) {
    const tokenIds = await this.client.smembers(`user_tokens:${userId}`);
    
    if (tokenIds && tokenIds.length) {
      const deletePromises = tokenIds.map(id => this.client.del(`refresh_token:${id}`));
      await Promise.all(deletePromises);
    }
    
    await this.client.del(`user_tokens:${userId}`);
  }

  /**
   * Add an access token to the blacklist
   * @param {string} token - JWT token
   * @param {number} expiryInSeconds - Token expiry in seconds
   */
  async blacklistToken(token, expiryInSeconds) {
    const key = `blacklist:${token}`;
    await this.client.set(key, '1');
    await this.client.expire(key, expiryInSeconds);
  }

  /**
   * Check if a token is blacklisted
   * @param {string} token - JWT token
   * @returns {Promise<boolean>} - True if token is blacklisted
   */
  async isTokenBlacklisted(token) {
    const result = await this.client.get(`blacklist:${token}`);
    return !!result;
  }

  /**
   * Store data with an expiration time
   * @param {string} key - Cache key
   * @param {any} data - Data to store (will be JSON stringified)
   * @param {number} expiryInSeconds - Expiry time in seconds
   */
  async cache(key, data, expiryInSeconds) {
    await this.client.set(key, JSON.stringify(data));
    
    if (expiryInSeconds) {
      await this.client.expire(key, expiryInSeconds);
    }
  }

  /**
   * Retrieve cached data
   * @param {string} key - Cache key
   * @returns {Promise<any>} - Parsed data or null if not found
   */
  async getCached(key) {
    const data = await this.client.get(key);
    
    if (!data) return null;
    
    try {
      return JSON.parse(data);
    } catch (error) {
      return data;
    }
  }

  /**
   * Delete cached data
   * @param {string} key - Cache key
   */
  async deleteCached(key) {
    await this.client.del(key);
  }
}

// Create and export the service instance
const redisService = new RedisService(redisClient);
module.exports = redisService;
