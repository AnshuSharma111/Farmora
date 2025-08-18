#!/usr/bin/env python
"""
Test script for the Farmora processing pipeline.
This script demonstrates how to use the processing.py module
with a sample audio file.
"""

import sys
import json
from pathlib import Path
from processing import process_query

def main():
    """Run a test of the processing pipeline with a sample audio file."""
    
    # Path to sample audio file - adjust this to point to a real .wav file
    sample_audio = Path(__file__).parent.parent.parent / "assets" / "samples" / "1.wav"
    
    if not sample_audio.exists():
        print(f"Sample audio file not found: {sample_audio}")
        print("Please provide the path to a valid .wav file:")
        audio_path = input("> ")
        sample_audio = Path(audio_path)
        if not sample_audio.exists():
            print(f"Error: File not found: {audio_path}")
            sys.exit(1)
    
    # Example user context
    language_code = "hi"  # Hindi
    crops = ["Rice", "Wheat"]
    location = [28.6139, 77.2090]  # Delhi coordinates
    state = "Punjab"
    district = "Ludhiana"
    market = "Ludhiana"
    
    print(f"Testing processing pipeline with audio file: {sample_audio}")
    print(f"Language: {language_code}")
    print(f"Crops: {', '.join(crops)}")
    print(f"Location: {location}")
    
    try:
        # Process the query
        result = process_query(
            audio_path=str(sample_audio),
            language_code=language_code,
            crops=crops,
            location=location,
            state=state,
            district=district,
            market=market
        )
        
        # Display the result
        print("\n=== TRANSCRIPTION ===")
        print(f"Language: {result['transcription']['language']}")
        print(f"English: {result['transcription']['transcript_eng']}")
        print(f"Native: {result['transcription']['transcript_native']}")
        
        print("\n=== SUGGESTED TOOLS ===")
        for tool in result["analysis"]["suggested_tools"]:
            print(f"- {tool['name']}")
        
        print("\n=== KEYWORDS ===")
        print(", ".join(result["analysis"]["keywords"]))
        
        print("\n=== TOOL OUTPUTS ===")
        for tool_name, output in result["tool_outputs"].items():
            print(f"- {tool_name}: {json.dumps(output, indent=2, ensure_ascii=False)}")
        
        print("\n=== FINAL RESPONSE ===")
        print(result["response"])
        
        print(f"\nProcessing completed in {result['processing_time']:.2f} seconds")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
