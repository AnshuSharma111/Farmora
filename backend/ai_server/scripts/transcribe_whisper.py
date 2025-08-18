import sys
import json
import whisper
from typing import Dict
from pathlib import Path

def transcript_audio(wav_path: str) -> Dict[str, str]:
    """
    Transcribes a WAV audio file using Whisper-small model.
    Returns a dict with keys: language, transcript_eng, transcript_native.
    Raises ValueError or RuntimeError on error.
    """
    # Check input file
    if not isinstance(wav_path, str) or not wav_path.lower().endswith('.wav'):
        raise ValueError("Input must be a path to a .wav file.")
    audio_file = Path(wav_path)
    if not audio_file.exists() or not audio_file.is_file():
        raise FileNotFoundError(f"File not found: {wav_path}")

    # Load model
    try:
        model = whisper.load_model("small")
    except Exception as e:
        raise RuntimeError(f"Failed to load Whisper model: {e}")
    if model is None:
        raise RuntimeError("Whisper model did not load properly.")

    # Transcribe in native language
    try:
        result_native = model.transcribe(str(audio_file), task="transcribe")
        language = result_native.get("language", "unknown")
        transcript_native = result_native.get("text", "")
    except Exception as e:
        raise RuntimeError(f"Native transcription failed: {e}")

    # Translate to English
    try:
        result_eng = model.transcribe(str(audio_file), task="translate")
        transcript_eng = result_eng.get("text", "")
    except Exception as e:
        raise RuntimeError(f"English translation failed: {e}")

    return {
        "language": language,
        "transcript_eng": transcript_eng,
        "transcript_native": transcript_native
    }

def main():
    if len(sys.argv) != 2:
        print("Usage: python transcribe_whisper.py <path_to_wav_file>")
        sys.exit(1)
    wav_path = sys.argv[1]
    try:
        output = transcript_audio(wav_path)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
