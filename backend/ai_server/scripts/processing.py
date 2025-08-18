import sys
import os
import json
from typing import Dict, List, Any, Optional, Union
import time
from dotenv import load_dotenv
from pathlib import Path

# Setup path handling for imports
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent

# Import functions from other modules in the same directory
from transcribe_whisper import transcript_audio
from analyze_intent_keywords import suggest_tools, extract_keywords, call_groq_api, GROQ_MODEL
from translate import translate_text, batch_translate

# Direct imports from tools directory using relative imports
sys.path.append(str(parent_dir))
from tools.weather_api import get_weather
from tools.commodity_price_tool import get_all_commodity_prices, get_commodity_price

# Load environment variables
load_dotenv()

# Configuration
DEFAULT_STATE = "Punjab"
DEFAULT_DISTRICT = "Ludhiana"
DEFAULT_MARKET = "Ludhiana"

class ProcessingError(Exception):
    """Exception raised for errors in the processing pipeline."""
    pass

def process_query(
    audio_path: str,
    language_code: str,
    crops: List[str],
    location: List[float],
    state: str = DEFAULT_STATE,
    district: str = DEFAULT_DISTRICT,
    market: str = DEFAULT_MARKET
) -> Dict[str, Any]:
    """
    Process an audio query through the entire pipeline:
    1. Transcribe audio
    2. Analyze transcription for tool suggestions and keywords
    3. Call relevant tools based on suggestions
    4. Generate response using all gathered information
    
    Args:
        audio_path: Path to the audio file (.wav format)
        language_code: Language code (e.g., 'en', 'hi', 'bn')
        crops: List of crops the user is interested in
        location: [latitude, longitude] of the user's location
        state: State for commodity queries (default: Punjab)
        district: District for commodity queries (default: Ludhiana)
        market: Market for commodity queries (default: Ludhiana)
        
    Returns:
        Dict containing the processing results:
        - transcription: Dict with language, transcript_eng, transcript_native
        - analysis: Dict with suggested_tools and keywords
        - tool_outputs: Dict with outputs from tools that were called
        - response: Final response generated for the user
    """
    start_time = time.time()
    result = {
        "transcription": None,
        "analysis": None,
        "tool_outputs": {},
        "response": None,
        "processing_time": None
    }
    
    try:
        # Step 1: Transcribe audio
        print(f"Transcribing audio from {audio_path}...")
        result["transcription"] = transcript_audio(audio_path)
        transcript_eng = result["transcription"]["transcript_eng"]
        transcript_native = result["transcription"]["transcript_native"]
        detected_language = result["transcription"]["language"]
        
        print(f"Detected language: {detected_language}")
        print(f"English transcript: {transcript_eng}")
        
        # Step 2: Analyze the transcription
        print("Analyzing transcription...")
        # Always prioritize the detected language from transcription
        # If not provided in language_code parameter, use detected language
        analysis_lang = detected_language
        print(f"Using language code for analysis: {analysis_lang}")
        result["analysis"] = {
            "suggested_tools": suggest_tools(transcript_eng, analysis_lang),
            "keywords": extract_keywords(transcript_eng, lang_code=analysis_lang)
        }
        
        # Step 3: Call relevant tools based on suggestions
        tool_outputs = {}
        for tool in result["analysis"]["suggested_tools"]:
            tool_id = tool["id"]
            print(f"Processing with tool: {tool['name']}...")
            
            if tool_id == "weather_tool":
                try:
                    # Validate location properly
                    if not isinstance(location, list) or len(location) != 2:
                        print(f"Warning: Invalid location format: {location}")
                        print("Expected format: [latitude, longitude]")
                        # Try to recover if possible
                        if isinstance(location, (list, tuple)) and len(location) >= 2:
                            lat, lon = location[0], location[1]
                        else:
                            # Use default coordinates for Delhi
                            print("Using default location (Delhi)")
                            lat, lon = 28.6139, 77.2090
                    else:
                        lat, lon = location
                        
                    print(f"Getting weather for coordinates: {lat}, {lon}")
                    weather_data = get_weather(lat, lon)
                    tool_outputs["weather"] = weather_data
                    print(f"Weather data retrieved: {weather_data}")
                except Exception as e:
                    print(f"Error getting weather data: {e}")
                    tool_outputs["weather"] = {"error": str(e)}
                    
            elif tool_id == "market_prices" or tool_id == "mandi_info":
                try:
                    # First, validate location
                    if not isinstance(location, list) or len(location) != 2:
                        print(f"Warning: Invalid location format: {location}")
                        print("Expected format: [latitude, longitude]")
                        # Try to recover if possible
                        if isinstance(location, (list, tuple)) and len(location) >= 2:
                            lat, lon = location[0], location[1]
                        else:
                            # Use default coordinates for Delhi
                            print("Using default location (Delhi)")
                            lat, lon = 28.6139, 77.2090
                    else:
                        lat, lon = location
                    
                    # Get data for all specified crops using location
                    print(f"Getting price data for crops {crops} at location {lat}, {lon}")
                    
                    # If no crops are specified, we'll get common crops for the region
                    if not crops:
                        print("No crops specified. Using default crops.")
                        crops_to_query = ["Rice", "Wheat"]  # Default crops
                    else:
                        crops_to_query = crops
                    
                    # Get price data for all crops
                    all_prices = get_all_commodity_prices(lat, lon, crops_to_query)
                    
                    # Structure the results
                    market_results = {}
                    for crop, data in all_prices.items():
                        if "error" not in data or not data["error"]:
                            market_results[crop] = {
                                "state": data.get("state"),
                                "district": data.get("district"),
                                "market": data.get("market"),
                                "latest_prices": data.get("latest_prices", {}),
                                "data_points": len(data.get("data", []))
                            }
                        else:
                            market_results[crop] = {
                                "error": data.get("error", "Unknown error")
                            }
                    
                    tool_outputs["market"] = {
                        "crops": crops_to_query,
                        "location": f"Lat: {lat}, Lon: {lon}",
                        "results": market_results
                    }
                    print(f"Market data retrieved for {len(market_results)} crops")
                except Exception as e:
                    print(f"Error getting market data: {e}")
                    tool_outputs["market"] = {"error": str(e)}
                    
            elif tool_id == "translate_tool":
                try:
                    # Check if there are keywords that suggest target language
                    target_lang = "en"  # Default to English
                    for keyword in result["analysis"]["keywords"]:
                        if keyword.lower() in ["hindi", "हिंदी"]:
                            target_lang = "hi"
                        elif keyword.lower() in ["punjabi", "पंजाबी"]:
                            target_lang = "pa"
                        elif keyword.lower() in ["bengali", "बंगाली"]:
                            target_lang = "bn"
                        elif keyword.lower() in ["tamil", "तमिल"]:
                            target_lang = "ta"
                        # Add more language mappings as needed
                    
                    # Extract the text to translate - use the transcript
                    text_to_translate = transcript_native
                    
                    # The source language is the detected language from transcript
                    source_lang = detected_language
                    
                    # If we're translating to the same language, switch to English
                    if target_lang == source_lang:
                        target_lang = "en"
                    
                    translation_result = translate_text(
                        text_to_translate, 
                        target_lang=target_lang,
                        source_lang=source_lang
                    )
                    
                    tool_outputs["translation"] = {
                        "original_text": text_to_translate,
                        "translated_text": translation_result["translated_text"],
                        "source_language": translation_result["source_language"],
                        "target_language": translation_result["target_language"],
                        "provider": translation_result["provider"]
                    }
                    print(f"Translation from {source_lang} to {target_lang} completed")
                    
                except Exception as e:
                    print(f"Error translating text: {e}")
                    tool_outputs["translation"] = {"error": str(e)}
            
            else:
                # For other tools, just acknowledge we've received the suggestion
                tool_outputs[tool_id] = {
                    "message": f"Tool '{tool['name']}' was suggested but not implemented yet."
                }
        
        result["tool_outputs"] = tool_outputs
        
        # Step 4: Generate a response using Groq API
        print(f"Generating response in {detected_language}...")
        response = generate_response(
            transcript_eng=transcript_eng,
            transcript_native=transcript_native,
            language_code=detected_language,  # Always use detected language from audio
            crops=crops,
            location=location,
            tool_outputs=tool_outputs,
            keywords=result["analysis"]["keywords"]
        )
        
        result["response"] = response
        
    except Exception as e:
        print(f"Error in processing pipeline: {e}")
        result["error"] = str(e)
    
    # Calculate total processing time
    result["processing_time"] = time.time() - start_time
    print(f"Processing completed in {result['processing_time']:.2f} seconds")
    
    return result

def generate_response(
    transcript_eng: str,
    transcript_native: str,
    language_code: str,
    crops: List[str],
    location: List[float],
    tool_outputs: Dict[str, Any],
    keywords: List[str]
) -> str:
    """
    Generate a response using the Groq API based on all the gathered information.
    The response will be in the same language as the original query.
    
    Args:
        transcript_eng: English transcription of the query
        transcript_native: Native language transcription
        language_code: Language code provided by the user (may be overridden by detected language)
        crops: List of crops the user is interested in
        location: [latitude, longitude] of the user's location
        tool_outputs: Outputs from the tools that were called
        keywords: Keywords extracted from the query
        
    Returns:
        Generated response text in the same language as the original query
    """
    # Create a detailed prompt for Groq API
    weather_info = ""
    market_info = ""
    
    if "weather" in tool_outputs:
        weather = tool_outputs["weather"]
        if "error" not in weather:
            weather_info = f"""
Weather information for location {location}:
- Temperature: {weather.get('temperature')}°C
- Wind speed: {weather.get('windspeed')} km/h
- Wind direction: {weather.get('winddirection')}°
- Weather code: {weather.get('weathercode')}
- Is day: {"Yes" if weather.get('is_day') == 1 else "No"}
- Time: {weather.get('time')}
"""
    
    if "market" in tool_outputs:
        market_data = tool_outputs["market"]
        if "error" not in market_data:
            crops_info = market_data.get("crops", [])
            location = market_data.get("location", "Unknown")
            results = market_data.get("results", {})
            
            market_info = f"Market information for crops at {location}:\n"
            
            for crop, data in results.items():
                if "error" not in data:
                    state = data.get("state", "Unknown")
                    district = data.get("district", "Unknown")
                    market = data.get("market", "Unknown")
                    latest = data.get("latest_prices", {})
                    
                    market_info += f"""
{crop} at {market}, {district}, {state}:
- Latest price: ₹{latest.get('modal_price', 'N/A')} (Modal price)
- Price range: ₹{latest.get('min_price', 'N/A')} - ₹{latest.get('max_price', 'N/A')}
- Date: {latest.get('date', 'N/A')}
- Variety: {latest.get('variety', 'N/A')}
"""
                else:
                    market_info += f"\n{crop}: No price data available.\n"
    
    crops_str = ", ".join(crops) if crops else "No specific crop mentioned"
    
    # Add translation info if available
    translation_info = ""
    if "translation" in tool_outputs:
        translation = tool_outputs["translation"]
        if "error" not in translation:
            translation_info = f"""
Translation information:
- Original text ({translation.get('source_language')}): {translation.get('original_text')}
- Translated text ({translation.get('target_language')}): {translation.get('translated_text')}
- Provider: {translation.get('provider')}
"""
    
    # Always use the language detected from the audio for the response
    response_language = language_code
    
    # Get the language name for better prompting
    language_names = {
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
        # Add more as needed
    }
    language_name = language_names.get(response_language, response_language)
    
    prompt = f"""
You are Farmora, an AI agricultural assistant that helps farmers. Respond to the query below with helpful information.

USER'S QUERY:
Original query (English): "{transcript_eng}"
Original query (Native language): "{transcript_native}"

USER CONTEXT:
- Detected language: {response_language} ({language_name})
- Location: Latitude {location[0]}, Longitude {location[1]}
- Crops of interest: {crops_str}
- Keywords identified: {', '.join(keywords)}

AVAILABLE DATA:
{weather_info}
{market_info}
{translation_info}

INSTRUCTIONS:
1. IMPORTANT: YOU MUST respond in the SAME LANGUAGE as the user's original query ({language_name}, code: {response_language})
2. Be concise but informative, focusing on the most relevant information
3. If you don't have enough information to answer completely, acknowledge this and provide what you can
4. If the tool outputs contain errors, don't mention the errors directly but suggest the user try again or provide general information
5. Format the response in a clear, easy-to-read way suitable for mobile viewing
6. If translation was requested, include both the original and translated text in your response
7. Your response MUST be in {language_name} ({response_language}) to match the user's original language

YOUR RESPONSE (in {language_name}):
"""
    
    try:
        response = call_groq_api(prompt)
        
        # Check if response has the expected structure
        if not response or "choices" not in response:
            print(f"Warning: Unexpected API response format: {response}")
            return f"I apologize, but I encountered an issue processing your request about {crops_str}. Please try again later."
            
        if not response["choices"] or len(response["choices"]) == 0:
            print("Warning: No choices returned in API response")
            return f"I apologize, but I encountered an issue processing your request about {crops_str}. Please try again later."
            
        # Extract the message content
        message_content = response["choices"][0].get("message", {}).get("content", "")
        if not message_content:
            print("Warning: No content in API response message")
            return f"I apologize, but I encountered an issue processing your request about {crops_str}. Please try again later."
            
        return message_content.strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        # Fallback response
        return f"I apologize, but I encountered an issue processing your request about {crops_str}. Please try again later."

def main():
    """Command-line interface for the processing pipeline."""
    if len(sys.argv) < 2:
        print("Usage: python processing.py <audio_file> [language_code] [crop1,crop2,...] [lat,lon]")
        print("Examples:")
        print("  python processing.py sample.wav hi wheat,rice 30.9,75.8")
        print("  python processing.py assets/samples/1.wav en rice,wheat 28.6139,77.2090")
        print("  python processing.py assets/samples/2.wav hi rice 28.6139 77.2090")
        sys.exit(1)
        
    # Parse arguments
    audio_path = sys.argv[1]
    language_code = sys.argv[2] if len(sys.argv) > 2 else "en"
    
    # Parse crops - handle both string format and list-like format with quotes
    if len(sys.argv) > 3:
        crops_arg = sys.argv[3]
        if crops_arg.startswith('[') and crops_arg.endswith(']'):
            # Handle list-like format: ['rice', 'wheat']
            crops_str = crops_arg.strip('[]')
            crops = [c.strip().strip("'\"") for c in crops_str.split(',')]
        else:
            # Handle simple comma-separated format: rice,wheat
            crops = [c.strip() for c in crops_arg.split(',')]
    else:
        crops = ["Rice"]
    
    # Parse location - handle both comma-separated and separate arguments
    if len(sys.argv) > 5:  # If lat and lon are provided as separate arguments
        try:
            lat = float(sys.argv[4])
            lon = float(sys.argv[5])
            location = [lat, lon]
        except ValueError:
            print("Error: Latitude and longitude must be numbers")
            location = [28.6139, 77.2090]  # Default to Delhi
    elif len(sys.argv) > 4:  # If lat,lon is provided as one argument
        try:
            location_parts = sys.argv[4].split(',')
            if len(location_parts) >= 2:
                location = [float(location_parts[0]), float(location_parts[1])]
            else:
                print("Warning: Location format should be lat,lon. Using default.")
                location = [28.6139, 77.2090]  # Default to Delhi
        except ValueError:
            print("Error: Invalid location format. Using default.")
            location = [28.6139, 77.2090]  # Default to Delhi
    else:
        location = [28.6139, 77.2090]  # Default to Delhi
        
    print(f"Using location: {location}")
    print(f"Using crops: {crops}")
    print(f"Using language code: {language_code}")
    
    # Process the query
    try:
        result = process_query(audio_path, language_code, crops, location)
        print("\n--- FINAL RESPONSE ---")
        print(result["response"])
        
        # Save the complete result to a JSON file for debugging
        output_file = f"query_result_{int(time.time())}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\nComplete results saved to {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
