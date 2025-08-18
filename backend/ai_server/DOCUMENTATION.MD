# Functions Created for AI Pipeline


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
Analyzes a text string in any language to extract both the predicted intent and relevant keywords using Groq's LLM API. This approach leverages the Llama 3 70B model for high-quality multilingual understanding.

**Signature:**
```python
def analyze_text(text: str, lang_code: str, top_n_keywords: int = 5) -> dict[str, object]
```

**Parameters:**
- `text` (str): The input text/query in any language.
- `lang_code` (str): The language code (e.g., 'en', 'hi').
- `top_n_keywords` (int, optional): Number of keywords to extract (default: 5).

**Returns:**
- `dict[str, object]`: A dictionary with keys:
    - `intent`: The predicted intent label (str)
    - `keywords`: List of extracted keywords (List[str])

**Raises:**
- `ValueError`: If the input is not a valid string or language code.
- `RuntimeError`: If the model fails to load or extraction fails.

**Example Usage:**
```python
from analyze_intent_keywords import analyze_text

result = analyze_text('मौसम की जानकारी चाहिए', 'hi')
print(result)
# Output:
# {
#   'intent': 'weather_query',
#   'keywords': ['मौसम', 'जानकारी']
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

## 2. Commodity Scraper
**Location:** `tools/scrape_commodity.py`

**Description:**
Scrapes commodity price and arrival data from the Agmarknet website for a given state, district, market, and commodity.

**Signature:**
```python
def scrape_commodity(
    state: str,
    commodity: str,
    district: str,
    market: str,
    price_arrival: str = "Both",
    date_from: str = None,
    date_to: str = None
) -> List[Dict[str, str]]
```

**Parameters:**
- `state` (str): The state name (e.g., "Himachal Pradesh").
- `commodity` (str): The commodity name (e.g., "Apple").
- `district` (str): The district name (e.g., "Shimla").
- `market` (str): The market name (e.g., "Shimla and Kinnaur(Nerwa)").
- `price_arrival` (str, optional): Type of data to fetch - "Price", "Arrival", or "Both" (default).
- `date_from` (str, optional): Start date in format "dd-MMM-yyyy" (e.g., "27-Jul-2025").
- `date_to` (str, optional): End date in format "dd-MMM-yyyy" (e.g., "18-Aug-2025").

**Returns:**
- `List[Dict[str, str]]`: A list of dictionaries containing the scraped data with keys such as State Name, District Name, Market Name, Variety, Group, Arrivals, Min Price, Max Price, Modal Price, Reported Date, and Grade.

**Raises:**
- `ValueError`: If provided input parameters are invalid or not found in the dropdown.
- `RuntimeError`: If navigation fails or no data table is found on the page.

**Additional Functions:**

```python
def get_latest_prices(
    data: List[Dict[str, str]], 
    commodity_variety: Optional[str] = None
) -> Dict[str, Union[str, float]]
```

**Parameters:**
- `data` (List[Dict[str, str]]): List of dictionaries containing scraped data.
- `commodity_variety` (str, optional): Optional variety of the commodity to filter by.

**Returns:**
- `Dict[str, Union[str, float]]`: Dictionary with the latest price information including variety, min_price, max_price, modal_price, date, and market.

**Example Usage:**
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