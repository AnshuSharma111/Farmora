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
INTENT_LABELS = [
    "greeting",
    "weather_query",
    "crop_query",
    "pesticide_query",
    "rate_query",
    "mandi_query",
    "price_query",
    "storage_query",
    "other"
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

# --- INTENT CLASSIFICATION ---
def classify_intent(text: str, lang_code: str) -> str:
    """
    Classifies the intent of the given text using Groq API.
    
    Args:
        text: The input text to classify
        lang_code: The language code of the input text
        
    Returns:
        The classified intent as a string
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must be a non-empty string.")
    if not isinstance(lang_code, str) or len(lang_code) < 2:
        raise ValueError("Language code must be a valid string.")
    
    prompt = f"""
You are an expert in agricultural domain intent classification. 
Given a query in the language code [{lang_code}], identify the intent from these categories: {", ".join(INTENT_LABELS)}

Query: {text}

Analyze the query and respond with ONLY ONE intent category from the list above. Do not include any explanation.
"""
    
    try:
        response = call_groq_api(prompt)
        intent_response = response["choices"][0]["message"]["content"].strip().lower()
        
        # Match the response to one of our intent labels
        for label in INTENT_LABELS:
            if label in intent_response:
                return label
        
        return "other"
    except Exception as e:
        raise RuntimeError(f"Intent classification failed: {e}")

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
        
        # Limit to top_n
        return keywords[:top_n]
    except Exception as e:
        raise RuntimeError(f"Keyword extraction failed: {e}")

# --- MAIN INTEGRATION ---
def analyze_text(text: str, lang_code: str, top_n_keywords: int = 5) -> Dict[str, object]:
    """
    Analyzes text to extract intent and keywords using Groq API.
    
    Args:
        text: The input text to analyze
        lang_code: The language code of the input text
        top_n_keywords: The maximum number of keywords to extract
        
    Returns:
        A dictionary containing the intent and keywords
    """
    intent = classify_intent(text, lang_code)
    keywords = extract_keywords(text, top_n=top_n_keywords, lang_code=lang_code)
    return {"intent": intent, "keywords": keywords}

def main():
    if len(sys.argv) < 3:
        print("Usage: python analyze_intent_keywords.py <text> <lang_code> [top_n_keywords]")
        sys.exit(1)
    text = sys.argv[1]
    lang_code = sys.argv[2]
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    # Check for API key
    if not GROQ_API_KEY:
        print("Error: GROQ_API_KEY environment variable not set")
        print("Please set the GROQ_API_KEY in a .env file or environment variables")
        sys.exit(1)
        
    try:
        print(f"Analyzing text in language: {lang_code}")
        start_time = time.time()
        
        result = analyze_text(text, lang_code, top_n)
        
        elapsed_time = time.time() - start_time
        print(f"Analysis completed in {elapsed_time:.2f} seconds")
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
