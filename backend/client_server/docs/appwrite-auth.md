# Farmora API Documentation - Appwrite Authentication

## Overview

Farmora's backend now uses [Appwrite](https://appwrite.io/) for authentication. This document outlines how authentication works and how to integrate with the API.

## Authentication Flow

1. **Frontend Authentication**:
   - Users sign up and log in directly through the Appwrite SDK in the frontend
   - The frontend obtains a JWT token from Appwrite
   - The frontend includes this token in all API requests to the backend

2. **Backend Verification**:
   - The backend verifies the JWT token using Appwrite's server SDK
   - Each request first passes through the `auth.middleware.js` which validates the token
   - The middleware adds user information to the request object for use in route handlers

## API Authentication Headers

For all authenticated requests, include the Appwrite JWT token in the Authorization header:

```
Authorization: Bearer YOUR_APPWRITE_JWT_TOKEN
```

## User Synchronization

When a user authenticates through Appwrite, you need to synchronize their profile with our backend:

### POST /farmora/api/auth/sync-user

Synchronizes user data from Appwrite with our database. Call this after successful login/signup or when user profile changes in Appwrite.

**Request Headers:**
```
Authorization: Bearer YOUR_APPWRITE_JWT_TOKEN
```

**Request Body:**
```json
{
  "location": "Tamil Nadu",
  "preferredLanguage": "en",
  "farmDetails": {
    "cropTypes": ["Rice", "Wheat"],
    "farmSize": "5 acres",
    "soilType": "Clay loam"
  }
}
```

**Response (201):**
```json
{
  "message": "User synchronized successfully",
  "user": {
    "id": "mongodb_id",
    "appwriteId": "appwrite_user_id",
    "name": "User Name",
    "email": "user@example.com",
    "location": "Tamil Nadu",
    "preferredLanguage": "en",
    "farmDetails": {
      "cropTypes": ["Rice", "Wheat"],
      "farmSize": "5 acres",
      "soilType": "Clay loam"
    }
  }
}
```

## Token Verification

To verify if a token is valid:

### GET /farmora/api/auth/verify

**Request Headers:**
```
Authorization: Bearer YOUR_APPWRITE_JWT_TOKEN
```

**Response (200):**
```json
{
  "isValid": true,
  "user": {
    "id": "mongodb_id",
    "appwriteId": "appwrite_user_id",
    "name": "User Name",
    "email": "user@example.com",
    "location": "Tamil Nadu",
    "preferredLanguage": "en"
  }
}
```

## Appwrite Project Setup

To set up Appwrite for the Farmora project:

1. Create an Appwrite project
2. Set up a web platform in the Appwrite console
3. Create an API key with the necessary permissions
4. Configure environment variables in the backend:
   - `APPWRITE_ENDPOINT`
   - `APPWRITE_PROJECT_ID`
   - `APPWRITE_API_KEY`

## Error Responses

**Unauthorized (401):**
```json
{
  "message": "Unauthorized: Invalid or expired token"
}
```

**User Not Found (404):**
```json
{
  "message": "User profile not found. Please sync your account first."
}
```

## Frontend Implementation Guide

In your frontend code:

1. Use the Appwrite Web SDK to handle authentication
2. After successful authentication, call the `/farmora/api/auth/sync-user` endpoint
3. Store the Appwrite JWT token securely and include it in all API requests
4. Implement token refresh logic using Appwrite's SDK

Example frontend authentication with Appwrite:

```javascript
import { Client, Account } from 'appwrite';

// Initialize Appwrite Client
const client = new Client()
  .setEndpoint('https://cloud.appwrite.io/v1')
  .setProject('YOUR_APPWRITE_PROJECT_ID');

const account = new Account(client);

// Sign up a user
async function signUp(email, password, name) {
  try {
    await account.create('unique()', email, password, name);
    return await login(email, password);
  } catch (error) {
    console.error('Sign up error:', error);
    throw error;
  }
}

// Log in a user
async function login(email, password) {
  try {
    const session = await account.createEmailSession(email, password);
    const jwt = await account.createJWT();
    
    // Sync with backend
    await syncUserWithBackend(jwt.jwt);
    
    return {
      token: jwt.jwt,
      userId: session.userId
    };
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

// Sync user with backend
async function syncUserWithBackend(token) {
  const response = await fetch('http://localhost:5001/farmora/api/auth/sync-user', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      location: 'User Location',
      preferredLanguage: 'en'
    })
  });
  
  return await response.json();
}
```
