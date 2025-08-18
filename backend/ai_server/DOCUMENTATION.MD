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
Analyzes a text string in any language to extract both the predicted intent (using XLM-RoBERTa) and relevant keywords (using KeyBERT with a multilingual model).

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