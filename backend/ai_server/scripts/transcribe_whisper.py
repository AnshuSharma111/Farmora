import sys
import json
import whisper

# Usage: python transcribe_whisper.py <path_to_wav_file>
def main():
    if len(sys.argv) != 2:
        print("Usage: python transcribe_whisper.py <path_to_wav_file>")
        sys.exit(1)

    wav_path = sys.argv[1]
    model = whisper.load_model("small")

    # Transcribe in native language
    result_native = model.transcribe(wav_path, task="transcribe")
    language = result_native.get("language", "unknown")
    transcript_native = result_native.get("text", "")

    # Translate to English
    result_eng = model.transcribe(wav_path, task="translate")
    transcript_eng = result_eng.get("text", "")

    output = {
        "language": language,
        "transcript_eng": transcript_eng,
        "transcript_native": transcript_native
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
