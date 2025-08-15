# Authentication Flow with Appwrite

## Setup
1. Frontend integrates Appwrite SDK
2. Backend verifies tokens with Appwrite API

## Frontend Flow
1. User signs up/logs in via frontend using Appwrite SDK
2. Appwrite issues JWT token
3. Frontend stores token in localStorage/cookies
4. Frontend includes token in Authorization header for API requests

## Backend Flow
1. Receive request with Appwrite JWT token
2. Verify token with Appwrite API
3. If valid, proceed with request
4. If invalid, return 401 Unauthorized

## Data Model
- User profiles stored in Appwrite
- Additional user data (farm details, preferences) stored in MongoDB
- Queries and responses stored in MongoDB

## Implementation Plan
1. Add Appwrite SDK to Express backend
2. Create middleware for token verification
3. Update routes to use the new middleware
4. Adjust MongoDB schema to use Appwrite user IDs
