#!/usr/bin/env python3
"""
Script to download model weights for the AI pipeline.
This script handles downloading and setting up:
1. Whisper model for ASR
2. XLM-RoBERTa for intent classification
3. IndicTrans2 for translation
4. Mistral/Gemma for LLM
"""

import os
import argparse
import torch
from transformers import WhisperForConditionalGeneration, XLMRobertaForSequenceClassification
from pathlib import Path

# Define the model weights directory
MODELS_DIR = Path("models/weights")

def setup_directories():
    """Create necessary directories for model weights"""
    dirs = [
        MODELS_DIR / "asr",
        MODELS_DIR / "intent",
        MODELS_DIR / "translation",
        MODELS_DIR / "llm"
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

def download_whisper_model(model_size="small"):
    """Download Whisper model for ASR"""
    print(f"Downloading Whisper-{model_size} model...")
    model_id = f"openai/whisper-{model_size}"
    
    try:
        model = WhisperForConditionalGeneration.from_pretrained(model_id)
        save_path = MODELS_DIR / "asr" / f"whisper-{model_size}"
        model.save_pretrained(save_path)
        print(f"Successfully downloaded Whisper-{model_size} to {save_path}")
    except Exception as e:
        print(f"Error downloading Whisper model: {e}")

def download_xlm_roberta_model(model_size="base"):
    """Download XLM-RoBERTa model for intent classification"""
    print(f"Downloading XLM-RoBERTa-{model_size} model...")
    model_id = f"xlm-roberta-{model_size}"
    
    try:
        model = XLMRobertaForSequenceClassification.from_pretrained(model_id)
        save_path = MODELS_DIR / "intent" / f"xlm-roberta-{model_size}"
        model.save_pretrained(save_path)
        print(f"Successfully downloaded XLM-RoBERTa-{model_size} to {save_path}")
    except Exception as e:
        print(f"Error downloading XLM-RoBERTa model: {e}")

def download_indictrans_model():
    """Download IndicTrans2 model for translation"""
    print("Note: IndicTrans2 model requires manual download from:")
    print("https://github.com/AI4Bharat/IndicTrans2")
    print("Please follow their instructions and place model weights in:")
    print(f"{MODELS_DIR}/translation/indictrans2")

def download_llm_model(model_name="mistral-7b"):
    """Download LLM model (placeholder for manual download instructions)"""
    print(f"Note: {model_name} requires manual download.")
    if "mistral" in model_name.lower():
        print("Visit: https://huggingface.co/mistralai")
    elif "gemma" in model_name.lower():
        print("Visit: https://huggingface.co/google/gemma-7b")
    
    print(f"After downloading, place model weights in:")
    print(f"{MODELS_DIR}/llm/{model_name}")

def main():
    parser = argparse.ArgumentParser(description="Download model weights for Farmora AI pipeline")
    parser.add_argument("--all", action="store_true", help="Download all models")
    parser.add_argument("--whisper", action="store_true", help="Download Whisper ASR model")
    parser.add_argument("--xlmr", action="store_true", help="Download XLM-RoBERTa model")
    
    args = parser.parse_args()
    
    # Setup directories
    setup_directories()
    
    # Download models based on arguments
    if args.all or args.whisper:
        download_whisper_model()
    
    if args.all or args.xlmr:
        download_xlm_roberta_model()
    
    if args.all:
        download_indictrans_model()
        download_llm_model()
    
    print("Model setup complete!")

if __name__ == "__main__":
    main()
