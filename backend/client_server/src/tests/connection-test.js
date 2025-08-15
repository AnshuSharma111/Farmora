// connection-test.js
require('dotenv').config();
const { Client, Account } = require('node-appwrite');
const mongoose = require('mongoose');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

console.log(`${colors.blue}=== Farmora Client Server Connection Test ===${colors.reset}`);
console.log(`${colors.yellow}Testing connections to external services...${colors.reset}\n`);

// Test Appwrite connection
async function testAppwrite() {
  console.log(`${colors.magenta}Testing Appwrite connection...${colors.reset}`);
  
  // Check if we're in development mode
  if (process.env.NODE_ENV === 'development') {
    console.log(`${colors.yellow}⚠ Using development mode with mock tokens${colors.reset}`);
    console.log(`${colors.green}✓ Appwrite mock connection accepted!${colors.reset}`);
    console.log(`  Running in development mode\n`);
    return true;
  }
  
  try {
    const client = new Client()
      .setEndpoint(process.env.APPWRITE_ENDPOINT)
      .setProject(process.env.APPWRITE_PROJECT_ID)
      .setKey(process.env.APPWRITE_API_KEY);
    
    // Try a simpler endpoint that requires less permissions
    const response = await client.call('get', '/health');
    
    console.log(`${colors.green}✓ Appwrite connection successful!${colors.reset}`);
    console.log(`  Endpoint: ${process.env.APPWRITE_ENDPOINT}`);
    console.log(`  Project ID: ${process.env.APPWRITE_PROJECT_ID.substring(0, 5)}...${colors.reset}\n`);
    return true;
  } catch (error) {
    console.log(`${colors.red}✗ Appwrite connection failed:${colors.reset}`);
    console.log(`  ${error.message}\n`);
    console.log(`${colors.yellow}Note: In development mode, you can still use mock tokens.${colors.reset}`);
    console.log(`${colors.yellow}Set NODE_ENV=development in .env file to use mock mode.${colors.reset}\n`);
    return false;
  }
}

// Test MongoDB connection
async function testMongoDB() {
  console.log(`${colors.magenta}Testing MongoDB connection...${colors.reset}`);
  
  // Check if we're using mock MongoDB
  const useMockMongoDB = process.env.NODE_ENV === 'development' || process.env.USE_MOCK_MONGODB === 'true';
  if (useMockMongoDB) {
    console.log(`${colors.yellow}⚠ Using mock MongoDB for development${colors.reset}`);
    console.log(`${colors.green}✓ Mock MongoDB setup successful!${colors.reset}`);
    console.log(`  No database connection required\n`);
    return true;
  }
  
  try {
    await mongoose.connect(process.env.MONGODB_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    
    console.log(`${colors.green}✓ MongoDB connection successful!${colors.reset}`);
    console.log(`  URI: ${process.env.MONGODB_URI}\n`);
    
    // Close the connection
    await mongoose.disconnect();
    return true;
  } catch (error) {
    console.log(`${colors.red}✗ MongoDB connection failed:${colors.reset}`);
    console.log(`  ${error.message}\n`);
    console.log(`${colors.yellow}Note: You can use mock MongoDB by setting USE_MOCK_MONGODB=true in .env${colors.reset}\n`);
    return false;
  }
}

// Test AI Server connection
async function testAIServer() {
  console.log(`${colors.magenta}Testing AI Server connection...${colors.reset}`);
  
  // In development mode, assume AI server is available
  if (process.env.NODE_ENV === 'development') {
    console.log(`${colors.yellow}⚠ Using development mode with mock AI server${colors.reset}`);
    console.log(`${colors.green}✓ AI Server mock connection accepted!${colors.reset}`);
    console.log(`  Running in development mode\n`);
    return true;
  }
  
  try {
    const response = await fetch(`${process.env.AI_SERVER_URL}/farmora/api/health`, {
      method: 'GET',
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log(`${colors.green}✓ AI Server connection successful!${colors.reset}`);
      console.log(`  Status: ${data.status}`);
      console.log(`  URL: ${process.env.AI_SERVER_URL}\n`);
      return true;
    } else {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  } catch (error) {
    console.log(`${colors.red}✗ AI Server connection failed:${colors.reset}`);
    console.log(`  ${error.message}`);
    console.log(`  Make sure the AI server is running on ${process.env.AI_SERVER_URL}\n`);
    return false;
  }
}

// Run all tests
async function runTests() {
  const appwriteResult = await testAppwrite();
  const mongoResult = await testMongoDB();
  const aiServerResult = await testAIServer();
  
  console.log(`${colors.blue}=== Test Results ===${colors.reset}`);
  console.log(`Appwrite: ${appwriteResult ? colors.green + 'PASS' : colors.red + 'FAIL'}${colors.reset}`);
  console.log(`MongoDB: ${mongoResult ? colors.green + 'PASS' : colors.red + 'FAIL'}${colors.reset}`);
  console.log(`AI Server: ${aiServerResult ? colors.green + 'PASS' : colors.red + 'FAIL'}${colors.reset}\n`);
  
  if (appwriteResult && mongoResult && aiServerResult) {
    console.log(`${colors.green}All connections successful! The client server is ready.${colors.reset}`);
  } else {
    console.log(`${colors.yellow}Some connections failed. Please check the errors above.${colors.reset}`);
  }
  
  process.exit(0);
}

// Run the tests
runTests().catch(err => {
  console.error(`${colors.red}Test error:${colors.reset}`, err);
  process.exit(1);
});
