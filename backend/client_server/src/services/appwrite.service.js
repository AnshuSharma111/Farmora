const { Client, Account } = require('node-appwrite');

class AppwriteService {
  constructor() {
    // Initialize the Appwrite client
    this.client = new Client();
    
    // Set the endpoint and project ID from environment variables
    this.client
      .setEndpoint(process.env.APPWRITE_ENDPOINT || 'https://cloud.appwrite.io/v1')
      .setProject(process.env.APPWRITE_PROJECT_ID || '');
      
    // Initialize the account module
    this.account = new Account(this.client);
  }

  /**
   * Verify a JWT token from Appwrite
   * @param {string} token - The JWT token to verify
   * @returns {Promise<object|null>} - The user data if token is valid, null otherwise
   */
  async verifyToken(token) {
    try {
      // Use the Appwrite SDK to verify the token and get session info
      // This is a session-based check, could also use JWT verification
      const session = await this.account.getSession('current', token);
      
      if (!session) {
        return null;
      }

      // Get the user associated with this session
      const user = await this.account.get();
      
      return {
        userId: user.$id,
        email: user.email,
        name: user.name,
        // Add any other user fields you need
        sessionId: session.$id
      };
    } catch (error) {
      console.error('Error verifying token with Appwrite:', error);
      return null;
    }
  }

  /**
   * Get user data from Appwrite
   * @param {string} userId - The user ID
   * @returns {Promise<object|null>} - The user data if found, null otherwise
   */
  async getUserData(userId) {
    try {
      // This would require admin privileges in a real implementation
      // For this example, we're assuming the current session user is being queried
      const user = await this.account.get();
      
      if (user.$id !== userId) {
        // In a real app with admin privileges, you could fetch any user
        // For now, we only allow getting the current user's data
        return null;
      }
      
      return {
        userId: user.$id,
        email: user.email,
        name: user.name,
        // Additional data would be here
      };
    } catch (error) {
      console.error('Error fetching user data from Appwrite:', error);
      return null;
    }
  }
}

// Create and export a singleton instance
const appwriteService = new AppwriteService();
module.exports = appwriteService;
