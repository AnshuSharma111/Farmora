# Farmora AI Pipeline Functions & Components


## 1. transcript_audio
**Location:** `transcribe_whisper.py`

**Description:**
Transcribes a WAV audio file using the Whisper-small model. Returns a dictionary with the detected language, the native transcription, and the English translation.

**Signature:**
```python
def transcript_audio(wav_path: str) -> dict[str, str]
```

**Parameters:**
- `wav_path` (str): Path to the input `.wav` audio file.

**Returns:**
- `dict[str, str]`: A dictionary with keys:
    - `language`: Detected language code (e.g., 'en', 'hi')
    - `transcript_eng`: Transcription translated to English
    - `transcript_native`: Transcription in the native language

**Raises:**
- `ValueError`: If the input is not a valid `.wav` file path.
- `FileNotFoundError`: If the file does not exist.
- `RuntimeError`: If the model fails to load or transcription fails.

**Example Usage:**
```python
from transcribe_whisper import transcript_audio

result = transcript_audio('assets/samples/3.wav')
print(result)
# Output:
# {
#   'language': 'hi',
#   'transcript_eng': 'Hello, how are you?',
#   'transcript_native': 'नमस्ते, आप कैसे हैं?'
# }
```

## 2. analyze_text
**Location:** `analyze_intent_keywords.py`

**Description:**
Analyzes a text string in any language to suggest relevant tools and extract keywords using Groq's LLM API. This approach leverages the Llama 3 70B model for high-quality multilingual understanding.

**Signature:**
```python
def analyze_text(text: str, lang_code: str, top_n_keywords: int = 5, max_tools: int = 2) -> dict[str, object]
```

**Parameters:**
- `text` (str): The input text/query in any language.
- `lang_code` (str): The language code (e.g., 'en', 'hi').
- `top_n_keywords` (int, optional): Number of keywords to extract (default: 5).
- `max_tools` (int, optional): Maximum number of tools to suggest (default: 2).

**Returns:**
- `dict[str, object]`: A dictionary with keys:
    - `suggested_tools`: List of suggested tools to help answer the query. Each tool is a dictionary with `id`, `name`, and `description` fields.
    - `keywords`: List of extracted keywords (List[str])

**Raises:**
- `ValueError`: If the input is not a valid string or language code.
- `RuntimeError`: If the API call fails or extraction fails.

**Example Usage:**
```python
from analyze_intent_keywords import analyze_text

result = analyze_text('मौसम की जानकारी चाहिए', 'hi')
print(result)
# Output:
# {
#   'suggested_tools': [
#     {
#       'id': 'weather_tool',
#       'name': 'Weather Information Tool',
#       'description': 'Provides weather forecasts, current conditions, and historical weather data'
#     }
#   ],
#   'keywords': ['मौसम', 'जानकारी', 'चाहिए']
# }
```

# Tools

## 1. Weather API
**Location:** `tools/weather_api.py`

**Description:**
Fetches current weather data for a given latitude and longitude using the Open-Meteo API.

**Signature:**
```python
def get_weather(lat: float, lon: float) -> dict
```

**Parameters:**
- `lat` (float): Latitude of the location.
- `lon` (float): Longitude of the location.

**Returns:**
- `dict`: Dictionary containing current weather data as returned by the API (e.g., temperature, windspeed, etc.)

**Raises:**
- `Exception`: If the API call fails or returns an error, or if no weather data is found.

**Example Usage:**
```python
from tools.weather_api import get_weather

weather = get_weather(28.6139, 77.2090)  # Example: New Delhi coordinates
print(weather)
# Output (example):
# {
#   'temperature': 34.2,
#   'windspeed': 5.1,
#   'winddirection': 120,
#   'weathercode': 1,
#   'is_day': 1,
#   'time': '2025-08-18T12:00'
# }
```

## 2. Commodity Price Tool
**Location:** `tools/commodity_price_tool.py`

**Description:**
Provides comprehensive commodity price data based on geographical location. Features robust error handling, fallback mechanisms, and seasonal crop information. This is an enhanced version that replaces the previous scrape_commodity tool.

### 2.1 Main Functions

**Get Price for a Single Commodity:**
```python
def get_commodity_price(
    lat: float, 
    lon: float, 
    commodity: str, 
    debug: bool = False
) -> Dict[str, Any]
```

**Get Prices for Multiple Commodities:**
```python
def get_all_commodity_prices(
    lat: float, 
    lon: float, 
    commodities: List[str], 
    debug: bool = False
) -> Dict[str, Dict[str, Any]]
```

**Parameters:**
- `lat` (float): Latitude coordinate (e.g., 30.7463)
- `lon` (float): Longitude coordinate (e.g., 76.6469)
- `commodity` (str): Commodity name to look up (e.g., "Rice", "Wheat")
- `commodities` (List[str]): List of commodity names to look up
- `debug` (bool, optional): Whether to enable debug mode with screenshots and verbose output

**Returns from get_commodity_price:**
- Dictionary with:
  - `state`: Determined state name
  - `district`: Determined district name
  - `market`: Market name used
  - `data_points`: Number of records found
  - `latest_prices`: Dictionary with price info (min_price, max_price, modal_price, date, variety)
  - `seasonal_info`: Dictionary with seasonal information (if available)
  - `error`: Error message (only present if an error occurred)

**Returns from get_all_commodity_prices:**
- Dictionary mapping each commodity name to its price data results (same format as above)

**Special Features:**
- Intelligent market selection based on geographical proximity
- Multiple fallback mechanisms for markets and date ranges
- District name normalization (Hisar/Hissar, Gurugram/Gurgaon)
- Seasonal crop information when price data isn't available

### 2.2 Helper Functions

**Find Nearest Location:**
```python
def find_nearest_location(lat: float, lon: float) -> Dict[str, Any]
```
Returns the nearest district and state based on coordinates.

**Get Crop Seasons:**
```python
def get_crop_seasons(commodity: str) -> Dict[str, str]
```
Returns seasonal information for a crop including growing season, harvesting period, and expected next harvest.

**Scrape Commodity:**
```python
def scrape_commodity(
    state: str,
    district: str,
    market: str,
    commodity: str,
    price_arrival: str = "Both",
    date_from: str = None,
    date_to: str = None,
    debug: bool = False
) -> List[Dict[str, str]]
```
Low-level function that handles the actual web scraping. Parameters similar to the original scrape_commodity but with improved robustness.

**Example Usage for Commodity Price Tool:**
```python
from tools.commodity_price_tool import get_commodity_price, get_all_commodity_prices

# Get price for a single commodity
lat = 30.7463  # Example: Coordinates near Chandigarh
lon = 76.6469
result = get_commodity_price(lat, lon, "Rice")

if "error" not in result:
    print(f"Found price data for Rice in {result['market']}")
    print(f"Latest price: ₹{result['latest_prices']['modal_price']}")
    print(f"Variety: {result['latest_prices']['variety']}")
else:
    print(f"Error: {result['error']}")
    if "seasonal_info" in result:
        print(f"Growing Season: {result['seasonal_info']['growing_season']}")

# Get prices for multiple commodities
commodities = ["Rice", "Wheat", "Potato"]
results = get_all_commodity_prices(lat, lon, commodities)

for commodity, data in results.items():
    if "error" not in data:
        print(f"{commodity}: ₹{data['latest_prices']['modal_price']} in {data['market']}")
    else:
        print(f"{commodity}: {data['error']}")
```

For more details, see the comprehensive documentation in `docs/COMMODITY_PRICE_TOOL.md`.

**Example Usage for Legacy Scraper:**
```python
from tools.scrape_commodity import scrape_commodity, get_latest_prices

# Get all commodity data
results = scrape_commodity(
    "Himachal Pradesh",
    "Apple",
    "Shimla",
    "Shimla and Kinnaur(Nerwa)"
)

# Get latest prices for a specific variety
latest = get_latest_prices(results, "Royal Delicious")
print(latest)
# Output (example):
# {
#   'variety': 'Royal Delicious',
#   'min_price': 2000.0,
#   'max_price': 9000.0,
#   'modal_price': 6000.0,
#   'date': '14 Aug 2025',
#   'market': 'Shimla and Kinnaur(Nerwa)'
# }
```

## 3. process_query
**Location:** `processing.py`

**Description:**
Processes an audio query through the entire pipeline, including transcription, intent analysis, tool invocation, and response generation. This function integrates all the components of the AI server into a complete end-to-end solution.

**Signature:**
```python
def process_query(
    audio_path: str,
    language_code: str,
    crops: List[str],
    location: List[float],
    state: str = DEFAULT_STATE,
    district: str = DEFAULT_DISTRICT,
    market: str = DEFAULT_MARKET
) -> Dict[str, Any]
```

**Parameters:**
- `audio_path` (str): Path to the audio file (.wav format)
- `language_code` (str): Language code (e.g., 'en', 'hi', 'bn')
- `crops` (List[str]): List of crops the user is interested in
- `location` (List[float]): [latitude, longitude] of the user's location
- `state` (str, optional): State for commodity queries (default: Punjab)
- `district` (str, optional): District for commodity queries (default: Ludhiana)
- `market` (str, optional): Market for commodity queries (default: Ludhiana)

**Returns:**
- `Dict[str, Any]`: A dictionary containing the processing results:
  - `transcription`: Dict with language, transcript_eng, transcript_native
  - `analysis`: Dict with suggested_tools and keywords
  - `tool_outputs`: Dict with outputs from tools that were called
  - `response`: Final response generated for the user
  - `processing_time`: Time taken to process the query in seconds

**Raises:**
- Various exceptions may be raised during processing, which are caught and included in the result as an "error" field.

**Example Usage:**
```python
from processing import process_query

result = process_query(
    audio_path="sample.wav",
    language_code="hi",
    crops=["Rice", "Wheat"],
    location=[28.6139, 77.2090]  # Delhi coordinates
)

# Display results
print(f"Response: {result['response']}")
print(f"Processing time: {result['processing_time']} seconds")
```

# Translation Functions

## 1. translate_text
**Location:** `scripts/translate.py`

**Description:**
Translates text from one language to another using Groq API (primary) with fallback to Hugging Face translation models. The function supports auto-detection of source language when needed.

**Signature:**
```python
def translate_text(
    text: str, 
    target_lang: str = DEFAULT_TARGET_LANG, 
    source_lang: str = DEFAULT_SOURCE_LANG,
    use_groq: bool = True
) -> Dict[str, Any]
```

**Parameters:**
- `text` (str): The text to translate
- `target_lang` (str, optional): The target language code (e.g., 'en', 'hi'). Default is 'en'.
- `source_lang` (str, optional): The source language code, or 'auto' for auto-detection. Default is 'auto'.
- `use_groq` (bool, optional): Whether to use Groq API (True) or start with Hugging Face (False). Default is True.

**Returns:**
- `Dict[str, Any]`: A dictionary containing:
  - `translated_text`: The translated text
  - `detected_language`: The detected source language (if source_lang was 'auto')
  - `source_language`: The source language used
  - `target_language`: The target language used
  - `provider`: The translation provider used ('groq' or 'huggingface')

**Raises:**
- `ValueError`: If input text is empty or language codes are invalid
- `RuntimeError`: If translation fails with both providers

**Example Usage:**
```python
from scripts.translate import translate_text

# Basic translation with auto-detection
result = translate_text("नमस्ते, आप कैसे हैं?", target_lang="en")
print(f"Translated: {result['translated_text']}")  # Output: "Hello, how are you?"

# Specific language pair
result = translate_text("Hello, how are you?", target_lang="hi", source_lang="en")
print(f"Translated: {result['translated_text']}")  # Output: "नमस्ते, आप कैसे हैं?"
```

## 2. batch_translate
**Location:** `scripts/translate.py`

**Description:**
Translates multiple texts from one language to another in batch mode.

**Signature:**
```python
def batch_translate(
    texts: list[str], 
    target_lang: str = DEFAULT_TARGET_LANG, 
    source_lang: str = DEFAULT_SOURCE_LANG
) -> list[Dict[str, Any]]
```

**Parameters:**
- `texts` (list[str]): List of texts to translate
- `target_lang` (str, optional): The target language code. Default is 'en'.
- `source_lang` (str, optional): The source language code, or 'auto' for auto-detection. Default is 'auto'.

**Returns:**
- `list[Dict[str, Any]]`: List of dictionaries, each containing translation results for one text

**Example Usage:**
```python
from scripts.translate import batch_translate

results = batch_translate(
    ["Hello, how are you?", "What is the weather today?"],
    target_lang="hi"
)

for result in results:
    print(f"Original (detected as {result['detected_language']}): {result['text']}")
    print(f"Translated: {result['translated_text']}")
```

# Complete Pipeline Flow

The Farmora AI Server pipeline consists of the following steps:

1. **Audio Transcription** (`transcribe_whisper.py`)
   - Converts audio input to text in both native language and English
   - Detects the language if not specified

2. **Intent and Keyword Analysis** (`analyze_intent_keywords.py`)
   - Suggests relevant tools based on the query content
   - Extracts important keywords from the query

3. **Tool Execution**
   - Weather data retrieval (`weather_api.py`) if weather information is requested
   - Commodity price data retrieval (`scrape_commodity.py`) if market information is requested
   - Text translation (`translate.py`) for translating between languages

4. **Response Generation** (`processing.py`)
   - Uses Groq API to generate a natural language response
   - Integrates information from tools and original query
   - Automatically responds in the same language as the original query
   - Uses language detection to match user's language

The complete pipeline is implemented in the `process_query` function in `processing.py`.## 13. Geolocation Utilities
**Location:** `tools/geo_utils.py`

**Description:**
Provides utilities for working with geographical coordinates, including reverse geocoding and finding nearby markets. Features offline fallback when API is unavailable.

### 13.1 get_state_district
**Signature:**
```python
def get_state_district(lat: float, lon: float) -> Tuple[str, Optional[str]]
```

**Parameters:**
- `lat` (float): Latitude coordinate
- `lon` (float): Longitude coordinate

**Returns:**
- `Tuple[str, Optional[str]]`: A tuple containing (state_name, district_name) where district_name may be None if not found

**Raises:**
- `RuntimeError`: If the API request fails or no state is found

**Example Usage:**
```python
from tools.geo_utils import get_state_district

state, district = get_state_district(30.7463, 76.6469)
# Returns: ("Punjab", "Mohali")
```

### 13.2 get_nearest_markets
**Signature:**
```python
def get_nearest_markets(state: str, district: str, commodity: str) -> List[str]
```

**Parameters:**
- `state` (str): State name
- `district` (str): District name
- `commodity` (str): Commodity name

**Returns:**
- `List[str]`: List of market names in the district

**Example Usage:**
```python
from tools.geo_utils import get_nearest_markets

markets = get_nearest_markets("Punjab", "Mohali", "rice")
# Returns: ["Sri Har Gobindpur", "Kharar", "Mohali"]
```

### 13.3 normalize_district_name
**Signature:**
```python
def normalize_district_name(district: str) -> str
```

**Parameters:**
- `district` (str): District name to normalize

**Returns:**
- `str`: Normalized district name with common suffixes removed and standard naming applied

**Example Usage:**
```python
from tools.geo_utils import normalize_district_name

clean_name = normalize_district_name("Kharar Tahsil")
# Returns: "Mohali"

clean_name = normalize_district_name("SAS Nagar")
# Returns: "Mohali"
```
