# Farmora Server

Backend server for Farmora application with AppWrite authentication integration.

## Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Create a `.env` file with your AppWrite and MongoDB configuration:
   ```
   APPWRITE_ENDPOINT=https://nyc.cloud.appwrite.io/v1
   APPWRITE_PROJECT_ID=your-project-id
   APPWRITE_API_KEY=your-secret-api-key
   PORT=3000
   JWT_SECRET=your-jwt-secret-key
   MONGODB_URI=mongodb+srv://username:password@cluster0.mongodb.net/farmora?retryWrites=true&w=majority
   ```

3. Start the server:
   ```
   npm start
   ```
   
   Or for development:
   ```
   npm run dev
   ```

## API Endpoints

### Authentication

- **POST /api/auth/signup**
  - Register a new user
  - Body: `{ "email": "user@example.com", "password": "password", "name": "User Name" }`

- **POST /api/auth/signin**
  - Login a user
  - Body: `{ "email": "user@example.com", "password": "password" }`

- **POST /api/auth/google**
  - Sign in with Google (not fully implemented)
  - Body: `{ "idToken": "google-id-token" }`

- **POST /api/auth/signout**
  - Sign out current user
  - Optional Body: `{ "sessionId": "specific-session-id" }`

- **GET /api/auth/user**
  - Get current user data
  - Header: `Authorization: Bearer your-jwt-token`

- **GET /api/auth/verify-email**
  - Verify email address
  - Query params: `userId` and `secret`

- **POST /api/auth/send-verification**
  - Send verification email
  - Header: `Authorization: Bearer your-jwt-token`

### User Profile

- **POST /api/profile**
  - Create or update user profile
  - Header: `Authorization: Bearer your-jwt-token`
  - Body:
    ```json
    {
      "language": "hindi",
      "location": [28.6139, 77.2090],
      "district": "New Delhi",
      "crops": ["wheat", "rice", "cotton"]
    }
    ```

- **GET /api/profile**
  - Get user profile
  - Header: `Authorization: Bearer your-jwt-token`
  - Response:
    ```json
    {
      "status": "success",
      "data": {
        "language": "hindi",
        "location": [28.6139, 77.2090],
        "district": "New Delhi",
        "crops": ["wheat", "rice", "cotton"]
      }
    }
    ```

## Integration with Android App

This server provides backend endpoints that complement the AppWrite authentication used in the Farmora Android app. The Android app makes direct calls to AppWrite services, while this server offers additional functionality and security layers.
