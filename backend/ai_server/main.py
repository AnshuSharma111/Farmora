from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
from auth import verify_appwrite_token

# Initialize FastAPI app
app = FastAPI(
    title="Farmora AI Server",
    description="AI server for the Farmora project that handles ML processing, intent classification, and data summarization",
    version="0.1.0",
    # Set the root path prefix for all routes
    root_path="/farmora"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define data models
class FarmerQuery(BaseModel):
    query: str
    location: Optional[str] = None
    language: Optional[str] = "en"
    user_id: Optional[str] = None

class ProcessedQuery(BaseModel):
    intent: str
    context: Dict[str, Any]
    summary: str

class FarmerResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float
    intent: Optional[str] = None

# Root endpoint
@app.get("/api")
async def root():
    return {"message": "Welcome to Farmora AI Server"}

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "ai-server"}

# Intent classification endpoint
@app.post("/api/classify_intent")
async def classify_intent(query: FarmerQuery):
    """
    Classifies the farmer's intent using a local model
    (weather, soil health, crop choice, pest control, etc.)
    """
    # TODO: Implement local intent classification model
    try:
        # Placeholder for intent classification logic
        intent = "crop_planning"  # This would be determined by the model
        return {"intent": intent, "confidence": 0.95}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent classification error: {str(e)}")

# Data retrieval and processing endpoint
@app.post("/api/process_query")
async def process_query(query: FarmerQuery):
    """
    Retrieves relevant data based on the query and intent,
    then summarizes it for efficient LLM processing
    """
    # TODO: Implement data retrieval and processing
    try:
        # Placeholder for query processing pipeline
        processed = ProcessedQuery(
            intent="crop_planning",
            context={
                "weather": {"temp_range": "28-32°C", "rainfall": "light"},
                "location": query.location or "Unknown",
                "season": "current"
            },
            summary="Query about crop planning with light rainfall expected"
        )
        return processed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing error: {str(e)}")

# LLM response generation endpoint
@app.post("/api/generate_response")
async def generate_response(processed: ProcessedQuery):
    """
    Sends the processed query to an LLM to generate
    a farmer-friendly response
    """
    # TODO: Implement LLM response generation
    try:
        # Placeholder for LLM response generation
        response = FarmerResponse(
            answer="Given next week's temperature (28–32°C) and predicted light rainfall, you can plant short-duration crops like mung beans or okra. Avoid paddy this week due to low water availability.",
            sources=["weather_api", "crop_database", "historical_rainfall"],
            confidence=0.87
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response generation error: {str(e)}")

# Main farmer query processing pipeline
@app.post("/api/ask")
async def ask(query: FarmerQuery, appwrite_user: Dict = Depends(verify_appwrite_token)):
    """
    Complete pipeline that:
    1. Classifies intent
    2. Retrieves and processes relevant data
    3. Generates a farmer-friendly response
    
    Requires authentication via Appwrite token
    """
    try:
        # Check if the user_id from the query matches the authenticated user
        # Skip this check for development environment with mock tokens
        if os.environ.get("ENVIRONMENT") != "development" and query.user_id != appwrite_user["userId"]:
            raise HTTPException(status_code=403, detail="User ID mismatch")
        
        # Step 1: Classify intent
        intent_result = await classify_intent(query)
        
        # Step 2: Process query based on intent
        processed_query = await process_query(query)
        
        # Step 3: Generate response using LLM
        final_response = await generate_response(processed_query)
        
        # Add intent to the response
        final_response.intent = processed_query.intent
        
        return final_response
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing pipeline error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
