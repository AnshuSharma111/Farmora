import os
import requests
from typing import Dict, Optional
from fastapi import HTTPException, Header

# Get configuration from environment variables
APPWRITE_ENDPOINT = os.environ.get("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
APPWRITE_PROJECT_ID = os.environ.get("APPWRITE_PROJECT_ID", "your-project-id")
APPWRITE_API_KEY = os.environ.get("APPWRITE_API_KEY", "your-api-key")

async def verify_appwrite_token(authorization: Optional[str] = Header(None)) -> Dict:
    """
    Verifies an Appwrite token and returns the user data
    This is a FastAPI dependency function that can be used with Depends()
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    
    # For development/testing without actual Appwrite
    if token == "mock_token" and os.environ.get("ENVIRONMENT") == "development":
        return {
            "userId": "mock_user_id",
            "name": "Mock User",
            "email": "mock@example.com"
        }
        
    # Verify the token with Appwrite
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Appwrite-Project": APPWRITE_PROJECT_ID,
            "X-Appwrite-Key": APPWRITE_API_KEY,
        }
        
        # Use Appwrite API to verify the JWT
        response = requests.post(
            f"{APPWRITE_ENDPOINT}/account/jwt/verify",
            headers=headers,
            json={"jwt": token}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        jwt_data = response.json()
        
        # Get user data using the JWT
        user_response = requests.get(
            f"{APPWRITE_ENDPOINT}/users/{jwt_data['userId']}",
            headers=headers
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Cannot verify user data")
            
        user_data = user_response.json()
        
        return {
            "userId": user_data["$id"],
            "name": user_data["name"],
            "email": user_data["email"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token verification failed: {str(e)}")
