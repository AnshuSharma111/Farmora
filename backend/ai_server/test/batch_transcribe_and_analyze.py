import os
import json
from transcribe_whisper import transcript_audio
from analyze_intent_keywords import analyze_text

SAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../assets/samples'))
AUDIO_FILES = [
    '1.wav',
    '2.wav',
    '3.wav',
    'test_query.wav'
]

results = {}


for fname in AUDIO_FILES:
    fpath = os.path.join(SAMPLES_DIR, fname)
    print(f"Processing {fname}...")
    try:
        trans = transcript_audio(fpath)
        # Use only the English transcript for intent and keyword extraction
        analysis_eng = analyze_text(trans['transcript_eng'], 'en')
        results[fname] = {
            'language': trans['language'],
            'transcript_native': trans['transcript_native'],
            'transcript_eng': trans['transcript_eng'],
            'analysis_eng': analysis_eng
        }
    except Exception as e:
        results[fname] = {'error': str(e)}

with open('transcription_intent_keyword_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Done. Results saved to transcription_intent_keyword_results.json")
