const { Client, Account, ID, Teams } = require('node-appwrite');
require('dotenv').config();

// Initialize Appwrite client
const client = new Client()
    .setEndpoint(process.env.APPWRITE_ENDPOINT)
    .setProject(process.env.APPWRITE_PROJECT_ID)
    .setKey(process.env.APPWRITE_API_KEY);

const account = new Account(client);

module.exports = {
    client,
    account,
    ID
};
