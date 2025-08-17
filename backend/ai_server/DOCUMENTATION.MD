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