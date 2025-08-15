# Appwrite Authentication Integration Summary

## Overview of Changes

We've integrated Appwrite authentication into both the client server (Express) and AI server (FastAPI), replacing the previous custom JWT implementation. Here's a summary of the changes:

## Client Server (Express) Changes

1. **New Files**:
   - `services/appwrite.service.js`: Handles token verification with Appwrite
   - `docs/appwrite-auth.md`: Documentation for the Appwrite authentication flow

2. **Updated Files**:
   - `models/user.model.js`: Added `appwriteId` field, removed password-related functionality
   - `middlewares/auth.middleware.js`: Updated to verify tokens with Appwrite
   - `routes/auth.routes.js`: Simplified to handle only token verification and user synchronization
   - `routes/user.routes.js`: Updated to query users by Appwrite ID
   - `routes/query.routes.js`: Updated to include Appwrite ID in queries
   - `models/query.model.js`: Added `appwriteId` field
   - `routes/mock.routes.js`: Updated mock routes for testing without Appwrite
   - `index.js`: Removed Redis service, added Appwrite service
   - `.env.example`: Updated with Appwrite configuration

3. **Removed Dependencies**:
   - `jsonwebtoken`: No longer needed as Appwrite handles JWT
   - `bcrypt`: No longer needed as Appwrite handles password hashing
   - `redis`: No longer needed for token blacklisting

## AI Server (FastAPI) Changes

1. **New Files**:
   - `auth.py`: Implements Appwrite token verification for FastAPI

2. **Updated Files**:
   - `main.py`: Added token verification to endpoints
   - `requirements.txt`: Added `python-jose` for JWT handling
   - `.env.example`: Added Appwrite configuration

## Authentication Flow

1. **Frontend**:
   - User signs up/logs in directly with Appwrite SDK
   - Frontend obtains a JWT token from Appwrite
   - Frontend includes token in all API requests

2. **Backend - Client Server**:
   - Verifies token with Appwrite API
   - Uses `appwriteId` to identify users in the database
   - New user profiles are created on first login via `/farmora/api/auth/sync-user`

3. **Backend - AI Server**:
   - Verifies token with Appwrite API
   - Uses `appwriteId` from token to identify users

## API Endpoints

1. **Client Server Authentication**:
   - `/farmora/api/auth/sync-user`: Synchronizes Appwrite user with our database
   - `/farmora/api/auth/verify`: Verifies an Appwrite token

2. **User Management**:
   - `/farmora/api/users/me`: Get/update user profile
   - `/farmora/api/users/history`: Get user query history

3. **Query Processing**:
   - `/farmora/api/queries/ask`: Process a query (requires token)
   - `/farmora/api/queries/history`: Get query history
   - `/farmora/api/queries/:id/feedback`: Add feedback to a query

## Testing

For development and testing without Appwrite:
1. Set `ENVIRONMENT=development` in environment variables
2. The mock routes in the client server provide test endpoints
3. The AI server accepts a `mock_token` when in development mode

## Next Steps

1. Set up proper error handling for Appwrite API failures
2. Add automatic token refresh handling
3. Implement role-based access control if needed
4. Add proper logging for authentication events
