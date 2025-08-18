"""
Translation module for Farmora AI Server.

This module provides functions to translate text between different languages.
It primarily uses the Groq API for translation, with a fallback to
Hugging Face's translation models when necessary.
"""

import os
import sys
from typing import Optional, Dict, Any
import requests
from pathlib import Path
from dotenv import load_dotenv
import json

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))
from scripts.analyze_intent_keywords import call_groq_api, GROQ_MODEL

# Load environment variables
load_dotenv()

# Constants
DEFAULT_SOURCE_LANG = "auto"  # Auto-detect source language
DEFAULT_TARGET_LANG = "en"    # English as default target
HF_API_KEY = os.getenv("HF_API_KEY")  # For fallback to Hugging Face
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/nllb-200-distilled-600M"
LANGUAGE_NAMES = {
    # ISO 639-1 language codes mapped to names
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "pa": "Punjabi",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "or": "Odia",
    "as": "Assamese",
    # Add more languages as needed
}

def translate_text(
    text: str, 
    target_lang: str = DEFAULT_TARGET_LANG, 
    source_lang: str = DEFAULT_SOURCE_LANG,
    use_groq: bool = True
) -> Dict[str, Any]:
    """
    Translate text from one language to another.
    
    Args:
        text: The text to translate
        target_lang: The target language code (e.g., 'en', 'hi')
        source_lang: The source language code, or 'auto' for auto-detection
        use_groq: Whether to use Groq API (True) or Hugging Face (False)
        
    Returns:
        Dictionary containing:
        - translated_text: The translated text
        - detected_language: The detected source language (if source_lang was 'auto')
        - source_language: The source language used
        - target_language: The target language used
        - provider: The translation provider used ('groq' or 'huggingface')
    """
    if not text or not isinstance(text, str) or not text.strip():
        raise ValueError("Input text cannot be empty")
        
    if not target_lang or not isinstance(target_lang, str):
        raise ValueError("Target language code must be a valid string")
        
    # Convert language codes to names for better prompting
    source_lang_name = LANGUAGE_NAMES.get(source_lang, source_lang) if source_lang != "auto" else "auto-detected language"
    target_lang_name = LANGUAGE_NAMES.get(target_lang, target_lang)
    
    result = {
        "translated_text": "",
        "detected_language": None if source_lang != "auto" else "",
        "source_language": source_lang,
        "target_language": target_lang,
        "provider": ""
    }
    
    # Try Groq API first if requested
    if use_groq:
        try:
            result = _translate_with_groq(text, target_lang, source_lang, source_lang_name, target_lang_name)
            return result
        except Exception as e:
            print(f"Groq translation failed: {e}. Falling back to Hugging Face.")
    
    # Fallback to Hugging Face
    try:
        result = _translate_with_huggingface(text, target_lang, source_lang)
        return result
    except Exception as e:
        raise RuntimeError(f"Translation failed with both providers. Error: {e}")

def _translate_with_groq(
    text: str, 
    target_lang: str, 
    source_lang: str,
    source_lang_name: str,
    target_lang_name: str
) -> Dict[str, Any]:
    """
    Translate text using the Groq API.
    
    Args:
        text: The text to translate
        target_lang: The target language code
        source_lang: The source language code
        source_lang_name: The source language name
        target_lang_name: The target language name
        
    Returns:
        Dictionary with translation results
    """
    # Construct a prompt for the translation task
    prompt = f"""
You are a professional translator. Please translate the following text from {source_lang_name} to {target_lang_name}.
If the source language is set to 'auto-detected language', first determine what language the text is in, then translate.

Text to translate:
{text}

Translate the text completely and accurately. Provide ONLY the translated text without any comments, explanations, or additional text.
"""
    
    # Call the Groq API
    response = call_groq_api(prompt)
    
    # Extract the translation from the response
    translated_text = response["choices"][0]["message"]["content"].strip()
    
    # Build the result
    result = {
        "translated_text": translated_text,
        "detected_language": None if source_lang != "auto" else _detect_language_groq(text),
        "source_language": source_lang,
        "target_language": target_lang,
        "provider": "groq"
    }
    
    return result

def _detect_language_groq(text: str) -> str:
    """
    Detect the language of the input text using Groq API.
    
    Args:
        text: The text to detect language for
        
    Returns:
        Detected language code
    """
    prompt = f"""
You are a language detection expert. Identify the language of the following text:
"{text}"
Respond with ONLY the ISO 639-1 two-letter language code (e.g., 'en' for English, 'hi' for Hindi).
"""
    
    # Call the Groq API
    response = call_groq_api(prompt)
    
    # Extract the language code from the response
    language_code = response["choices"][0]["message"]["content"].strip().lower()
    
    # Ensure it's just the language code (remove any quotes or extra text)
    language_code = language_code.replace('"', '').replace("'", "")
    if len(language_code) > 2 and language_code in LANGUAGE_NAMES.values():
        # Try to convert language name back to code if that's what we got
        for code, name in LANGUAGE_NAMES.items():
            if name.lower() == language_code.lower():
                return code
    
    return language_code[:2]  # Just to be safe, take only the first two characters

def _translate_with_huggingface(
    text: str, 
    target_lang: str, 
    source_lang: str
) -> Dict[str, Any]:
    """
    Translate text using Hugging Face's translation API.
    
    Args:
        text: The text to translate
        target_lang: The target language code
        source_lang: The source language code
        
    Returns:
        Dictionary with translation results
    """
    headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}
    
    # For NLLB model, we need to convert language codes to FLORES format
    # Example: 'en' becomes 'eng_Latn'
    flores_codes = {
        "en": "eng_Latn",
        "hi": "hin_Deva",
        "bn": "ben_Beng",
        "pa": "pan_Guru",
        "ta": "tam_Taml",
        "te": "tel_Telu",
        "mr": "mar_Deva",
        "gu": "guj_Gujr",
        "kn": "kan_Knda",
        "ml": "mal_Mlym",
        # Add more mappings as needed
    }
    
    # If source_lang is 'auto', we need to detect it first
    if source_lang == "auto":
        detected_lang = _detect_language_hf(text)
        source_flores = flores_codes.get(detected_lang, "eng_Latn")  # Default to English if not found
    else:
        detected_lang = source_lang
        source_flores = flores_codes.get(source_lang, "eng_Latn")
    
    target_flores = flores_codes.get(target_lang, "eng_Latn")
    
    # Prepare the payload for the translation request
    payload = {
        "inputs": text,
        "parameters": {
            "src_lang": source_flores,
            "tgt_lang": target_flores
        }
    }
    
    # Make the API request
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    
    # Parse the response
    output = response.json()
    translated_text = output[0]["translation_text"] if isinstance(output, list) else output["translation_text"]
    
    # Build the result
    result = {
        "translated_text": translated_text,
        "detected_language": detected_lang if source_lang == "auto" else None,
        "source_language": detected_lang if source_lang == "auto" else source_lang,
        "target_language": target_lang,
        "provider": "huggingface"
    }
    
    return result

def _detect_language_hf(text: str) -> str:
    """
    Detect the language of the input text using Hugging Face's language detection model.
    
    Args:
        text: The text to detect language for
        
    Returns:
        Detected language code
    """
    # Use the language identification model
    hf_lang_detect_url = "https://api-inference.huggingface.co/models/papluca/xlm-roberta-base-language-detection"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"} if HF_API_KEY else {}
    
    response = requests.post(hf_lang_detect_url, headers=headers, json={"inputs": text})
    response.raise_for_status()
    
    # Parse the response
    output = response.json()
    
    # Get the language with the highest confidence
    if isinstance(output, list) and len(output) > 0 and isinstance(output[0], list):
        # Find the prediction with highest score
        best_prediction = max(output[0], key=lambda x: x["score"])
        return best_prediction["label"].split('_')[0]  # Convert 'en_XX' to 'en'
    
    return "en"  # Default to English if detection fails

def batch_translate(
    texts: list[str], 
    target_lang: str = DEFAULT_TARGET_LANG, 
    source_lang: str = DEFAULT_SOURCE_LANG
) -> list[Dict[str, Any]]:
    """
    Translate multiple texts from one language to another.
    
    Args:
        texts: List of texts to translate
        target_lang: The target language code
        source_lang: The source language code, or 'auto' for auto-detection
        
    Returns:
        List of dictionaries, each containing translation results for one text
    """
    results = []
    for text in texts:
        try:
            result = translate_text(text, target_lang, source_lang)
            results.append(result)
        except Exception as e:
            results.append({
                "error": str(e),
                "text": text,
                "source_language": source_lang,
                "target_language": target_lang
            })
    
    return results

def main():
    """Command-line interface for translation function."""
    if len(sys.argv) < 3:
        print("Usage: python translate.py <text> <target_lang> [source_lang]")
        print("Example: python translate.py 'Hello world' hi en")
        sys.exit(1)
    
    text = sys.argv[1]
    target_lang = sys.argv[2]
    source_lang = sys.argv[3] if len(sys.argv) > 3 else "auto"
    
    try:
        # First try with Groq
        print(f"Translating from {source_lang} to {target_lang}...")
        result = translate_text(text, target_lang, source_lang)
        
        print("\n--- TRANSLATION RESULT ---")
        if result["detected_language"]:
            print(f"Detected language: {result['detected_language']}")
        print(f"From: {result['source_language']}")
        print(f"To: {result['target_language']}")
        print(f"Provider: {result['provider']}")
        print(f"\nOriginal: {text}")
        print(f"Translated: {result['translated_text']}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
