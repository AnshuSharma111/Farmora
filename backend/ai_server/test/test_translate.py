"""
Test script for demonstrating the translation functionality.

This script provides examples of using the translate.py module to 
translate text between different languages.
"""

import os
import sys
from pathlib import Path
import json

# Add parent directory to path for imports
script_dir = Path(__file__).resolve().parent
parent_dir = script_dir.parent
sys.path.append(str(parent_dir))

from scripts.translate import translate_text, batch_translate

def test_basic_translation():
    """Test basic translation with language auto-detection."""
    # English to Hindi
    result = translate_text(
        "Hello, I am a farmer. I want to know about the weather.",
        target_lang="hi"
    )
    
    print("\n=== BASIC TRANSLATION (EN -> HI) ===")
    print(f"Source language: {result['source_language']}")
    print(f"Target language: {result['target_language']}")
    print(f"Provider: {result['provider']}")
    print(f"Original: Hello, I am a farmer. I want to know about the weather.")
    print(f"Translated: {result['translated_text']}")
    
    # Hindi to English
    result = translate_text(
        "नमस्ते, मैं एक किसान हूँ। मुझे मौसम के बारे में जानना है।",
        target_lang="en"
    )
    
    print("\n=== BASIC TRANSLATION (HI -> EN) ===")
    print(f"Source language: {result['source_language']}")
    print(f"Target language: {result['target_language']}")
    print(f"Provider: {result['provider']}")
    print(f"Original: नमस्ते, मैं एक किसान हूँ। मुझे मौसम के बारे में जानना है।")
    print(f"Translated: {result['translated_text']}")

def test_specific_language_pair():
    """Test translation with specific source and target languages."""
    result = translate_text(
        "How is the crop quality this season?",
        target_lang="ta",  # Tamil
        source_lang="en"   # English
    )
    
    print("\n=== SPECIFIC LANGUAGE PAIR (EN -> TA) ===")
    print(f"Source language: {result['source_language']}")
    print(f"Target language: {result['target_language']}")
    print(f"Provider: {result['provider']}")
    print(f"Original: How is the crop quality this season?")
    print(f"Translated: {result['translated_text']}")

def test_batch_translation():
    """Test batch translation of multiple texts."""
    texts = [
        "What are the current market prices?",
        "Is there a chance of rain tomorrow?",
        "How do I protect my crops from pests?"
    ]
    
    results = batch_translate(
        texts,
        target_lang="hi"  # Hindi
    )
    
    print("\n=== BATCH TRANSLATION (EN -> HI) ===")
    for i, result in enumerate(results):
        print(f"\nText {i+1}:")
        print(f"Source language: {result['source_language']}")
        print(f"Target language: {result['target_language']}")
        print(f"Provider: {result['provider']}")
        print(f"Original: {texts[i]}")
        print(f"Translated: {result['translated_text']}")

def test_huggingface_fallback():
    """Test fallback to Hugging Face when requested."""
    try:
        result = translate_text(
            "I need information about rice cultivation.",
            target_lang="bn",  # Bengali
            source_lang="en",  # English
            use_groq=False     # Force use of Hugging Face
        )
        
        print("\n=== HUGGING FACE TRANSLATION (EN -> BN) ===")
        print(f"Source language: {result['source_language']}")
        print(f"Target language: {result['target_language']}")
        print(f"Provider: {result['provider']}")
        print(f"Original: I need information about rice cultivation.")
        print(f"Translated: {result['translated_text']}")
    except Exception as e:
        print(f"\nHugging Face fallback test failed: {e}")
        print("This may be due to missing API key or connectivity issues.")

if __name__ == "__main__":
    print("=== TRANSLATION FUNCTIONALITY TESTS ===")
    print("This script demonstrates various ways to use the translation module.")
    
    try:
        test_basic_translation()
        test_specific_language_pair()
        test_batch_translation()
        test_huggingface_fallback()
    except Exception as e:
        print(f"\nError during testing: {e}")
        print("Make sure you have set up the required API keys and environment variables.")
