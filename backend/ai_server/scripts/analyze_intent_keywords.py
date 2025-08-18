import sys
import json
import os
import time
from typing import Dict, List, Any, Optional
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIG ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama3-70b-8192"  # Using Llama 3 70B model for high-quality multilingual understanding
AVAILABLE_TOOLS = [
    {
        "id": "weather_tool",
        "name": "Weather Information Tool",
        "description": "Provides weather forecasts, current conditions, and historical weather data"
    },
    {
        "id": "crop_advisor",
        "name": "Crop Advisory Tool",
        "description": "Offers advice on crop selection, planting times, and cultivation practices"
    },
    {
        "id": "pest_control",
        "name": "Pest Management Tool",
        "description": "Information on identifying and treating crop pests and diseases"
    },
    {
        "id": "market_prices",
        "name": "Market Price Tool",
        "description": "Current and historical crop prices in various markets"
    },
    {
        "id": "mandi_info",
        "name": "Mandi Information Tool",
        "description": "Details about local mandis, their operating hours, and available facilities"
    },
    {
        "id": "storage_advisor",
        "name": "Storage Advisory Tool",
        "description": "Best practices for crop storage and preservation"
    },
    {
        "id": "general_assistant",
        "name": "General Assistance",
        "description": "Basic information and conversation for general queries"
    }
]

# --- GROQ API INTEGRATION ---
def call_groq_api(prompt: str, model: str = GROQ_MODEL, temperature: float = 0.2) -> Dict[str, Any]:
    """
    Makes a call to the Groq API with the given prompt.
    
    Args:
        prompt: The prompt to send to the API
        model: The model to use (default: llama3-70b-8192)
        temperature: Controls randomness (0.0-1.0)
        
    Returns:
        The API response as a dictionary
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set")
        
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {e}")

# --- TOOL SUGGESTION ---
def suggest_tools(text: str, lang_code: str, max_tools: int = 2) -> List[Dict[str, str]]:
    """
    Suggests relevant tools to help answer the given query using Groq API.
    
    Args:
        text: The input text to analyze
        lang_code: The language code of the input text
        max_tools: Maximum number of tools to suggest
        
    Returns:
        A list of suggested tools, each as a dictionary with id, name, and description
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must be a non-empty string.")
    if not isinstance(lang_code, str) or len(lang_code) < 2:
        raise ValueError("Language code must be a valid string.")
    
    # Extract just the tool IDs for the prompt
    tool_ids = [tool["id"] for tool in AVAILABLE_TOOLS]
    tool_descriptions = [f"{tool['id']}: {tool['description']}" for tool in AVAILABLE_TOOLS]
    
    prompt = f"""
You are an expert agricultural assistant that helps farmers by suggesting the most helpful tools for their queries.

These are the tools you have available:
{chr(10).join(tool_descriptions)}

For the following query in language code [{lang_code}], suggest the {max_tools} most relevant tools from the list above that will best help answer the query.

Query: {text}

Respond with ONLY the tool IDs in a comma-separated list, ordered by relevance. Do not include any explanation or other text.
"""
    
    try:
        response = call_groq_api(prompt)
        tools_response = response["choices"][0]["message"]["content"].strip().lower()
        
        # Parse the comma-separated response
        suggested_tool_ids = [tool_id.strip() for tool_id in tools_response.split(',')]
        
        # Match the response to our available tools and return the full tool info
        suggested_tools = []
        for tool_id in suggested_tool_ids[:max_tools]:  # Limit to max_tools
            for tool in AVAILABLE_TOOLS:
                if tool_id in tool["id"].lower():
                    suggested_tools.append(tool)
                    break
        
        # If no tools matched or the response was invalid, return the general assistant
        if not suggested_tools:
            for tool in AVAILABLE_TOOLS:
                if tool["id"] == "general_assistant":
                    suggested_tools.append(tool)
                    break
        
        return suggested_tools
    except Exception as e:
        raise RuntimeError(f"Tool suggestion failed: {e}")

# --- KEYWORD EXTRACTION ---
def extract_keywords(text: str, top_n: int = 5, lang_code: Optional[str] = None) -> List[str]:
    """
    Extracts keywords from the given text using Groq API.
    
    Args:
        text: The input text to extract keywords from
        top_n: The maximum number of keywords to extract
        lang_code: Optional language code to help with extraction
        
    Returns:
        A list of extracted keywords
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must be a non-empty string.")
    
    lang_info = f"in language code [{lang_code}]" if lang_code else ""
    
    prompt = f"""
You are an expert keyword extractor for agricultural domain text.
Extract exactly {top_n} important keywords or key phrases from the following text {lang_info}. 
For non-English text, extract keywords in the original language.

Text: {text}

Respond with ONLY the keywords, one per line, with no additional text, explanation, or numbering.
"""
    
    try:
        response = call_groq_api(prompt)
        keywords_text = response["choices"][0]["message"]["content"].strip()
        
        # Split by newlines and clean up
        keywords = [kw.strip() for kw in keywords_text.split('\n') if kw.strip()]
        
        # Limit to top_n (ensure top_n is an integer)
        if not isinstance(top_n, int):
            top_n = 5  # Default to 5 keywords if top_n is not an integer
            
        return keywords[:top_n]
    except Exception as e:
        raise RuntimeError(f"Keyword extraction failed: {e}")

# --- MAIN INTEGRATION ---
def analyze_text(text: str, lang_code: str, top_n_keywords: int = 5, max_tools: int = 2) -> Dict[str, object]:
    """
    Analyzes text to extract suggested tools and keywords using Groq API.
    
    Args:
        text: The input text to analyze
        lang_code: The language code of the input text
        top_n_keywords: The maximum number of keywords to extract
        max_tools: Maximum number of tools to suggest
        
    Returns:
        A dictionary containing the suggested tools and keywords
    """
    tools = suggest_tools(text, lang_code, max_tools=max_tools)
    keywords = extract_keywords(text, top_n=top_n_keywords, lang_code=lang_code)
    return {"suggested_tools": tools, "keywords": keywords}

def main():
    if len(sys.argv) < 3:
        print("Usage: python analyze_intent_keywords.py <text> <lang_code> [top_n_keywords] [max_tools]")
        sys.exit(1)
    text = sys.argv[1]
    lang_code = sys.argv[2]
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    max_tools = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    
    # Check for API key
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY environment variable not set")
        print("Please set the GROQ_API_KEY in a .env file or environment variables")
        sys.exit(1)
        
    try:
        print(f"Analyzing text in language: {lang_code}")
        start_time = time.time()
        
        result = analyze_text(text, lang_code, top_n, max_tools)
        
        elapsed_time = time.time() - start_time
        print(f"Analysis completed in {elapsed_time:.2f} seconds")
        
        # Format the output for better readability
        print("\nSuggested Tools:")
        for i, tool in enumerate(result["suggested_tools"], 1):
            print(f"{i}. {tool['name']}: {tool['description']} (ID: {tool['id']})")
        
        print("\nExtracted Keywords:")
        for i, keyword in enumerate(result["keywords"], 1):
            print(f"{i}. {keyword}")
            
        print("\nComplete JSON Result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
