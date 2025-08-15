import os
import requests
import time
import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict, Optional, List, Any

# Load environment variables
load_dotenv()

# ANSI color codes for terminal output
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'

print(f"{Colors.BLUE}=== Farmora AI Server Connection Test ==={Colors.RESET}")
print(f"{Colors.YELLOW}Testing connections to external services...{Colors.RESET}\n")

# Test Appwrite connection
def test_appwrite():
    print(f"{Colors.MAGENTA}Testing Appwrite connection...{Colors.RESET}")
    
    appwrite_endpoint = os.getenv("APPWRITE_ENDPOINT")
    appwrite_project_id = os.getenv("APPWRITE_PROJECT_ID")
    appwrite_api_key = os.getenv("APPWRITE_API_KEY")
    
    if os.getenv("ENVIRONMENT") == "development" and (not appwrite_api_key or appwrite_api_key == "your-api-key"):
        print(f"{Colors.YELLOW}⚠ Using development mode with mock tokens{Colors.RESET}")
        print(f"{Colors.GREEN}✓ Appwrite mock connection accepted!{Colors.RESET}")
        print(f"  Running in development mode\n")
        return True
    
    headers = {
        "X-Appwrite-Project": appwrite_project_id,
        "X-Appwrite-Key": appwrite_api_key,
    }
    
    try:
        # Try a simpler endpoint that requires less permissions
        response = requests.get(
            f"{appwrite_endpoint}/health",
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            print(f"{Colors.GREEN}✓ Appwrite connection successful!{Colors.RESET}")
            print(f"  Endpoint: {appwrite_endpoint}")
            print(f"  Project ID: {appwrite_project_id[:5]}...\n")
            return True
        else:
            raise Exception(f"Status code: {response.status_code}, Message: {response.text}")
            
    except Exception as e:
        print(f"{Colors.RED}✗ Appwrite connection failed:{Colors.RESET}")
        print(f"  {str(e)}\n")
        print(f"{Colors.YELLOW}Note: In development mode, you can still use mock tokens.{Colors.RESET}")
        print(f"{Colors.YELLOW}Set ENVIRONMENT=development in .env file to use mock mode.{Colors.RESET}\n")
        return False

# Test OpenAI connection if configured
def test_openai():
    print(f"{Colors.MAGENTA}Testing OpenAI connection (if configured)...{Colors.RESET}")
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key or openai_api_key == "your_openai_key_here":
        print(f"{Colors.YELLOW}⚠ OpenAI API key not configured, skipping test{Colors.RESET}\n")
        return None
        
    try:
        # Make a simple request to the OpenAI API
        headers = {
            "Authorization": f"Bearer {openai_api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"{Colors.GREEN}✓ OpenAI connection successful!{Colors.RESET}")
            print(f"  Found {len(response.json().get('data', []))} models\n")
            return True
        else:
            raise Exception(f"Status code: {response.status_code}, Message: {response.text}")
            
    except Exception as e:
        print(f"{Colors.RED}✗ OpenAI connection failed:{Colors.RESET}")
        print(f"  {str(e)}\n")
        return False

# Create a test FastAPI instance
app = FastAPI(title="Farmora AI Server Test")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/farmora/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ai-server",
        "timestamp": time.time()
    }

# Run all tests
def run_tests():
    appwrite_result = test_appwrite()
    openai_result = test_openai()
    
    print(f"{Colors.BLUE}=== Test Results ==={Colors.RESET}")
    print(f"Appwrite: {Colors.GREEN + 'PASS' if appwrite_result else Colors.RED + 'FAIL'}{Colors.RESET}")
    
    if openai_result is not None:
        print(f"OpenAI: {Colors.GREEN + 'PASS' if openai_result else Colors.RED + 'FAIL'}{Colors.RESET}")
    else:
        print(f"OpenAI: {Colors.YELLOW}SKIPPED{Colors.RESET}")
    
    print(f"\nStarting test server on port 8000...")
    print(f"Access the health check at: http://localhost:8000/farmora/api/health")
    print(f"{Colors.YELLOW}Press CTRL+C to stop the server{Colors.RESET}\n")

if __name__ == "__main__":
    run_tests()
    # Start a test server
    uvicorn.run(app, host="0.0.0.0", port=8000)
