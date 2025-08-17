import sys
import json
from typing import Dict, List
import torch
from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

# --- CONFIG ---
MODEL_NAME = "xlm-roberta-base"  # Update to your fine-tuned model if available
INTENT_LABELS = [
    "greeting",
    "weather_query",
    "crop_query",
    "pesticide_query",
    "rate_query",
    "mandi_query",
    "price_query",
    "storage_query",
    "other"
]
KEYBERT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# --- INTENT CLASSIFICATION ---
def load_intent_model_and_tokenizer(model_name: str):
    try:
        tokenizer = XLMRobertaTokenizer.from_pretrained(model_name)
        model = XLMRobertaForSequenceClassification.from_pretrained(model_name)
        return tokenizer, model
    except Exception as e:
        raise RuntimeError(f"Failed to load intent model/tokenizer: {e}")

def classify_intent(text: str, lang_code: str) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must be a non-empty string.")
    if not isinstance(lang_code, str) or len(lang_code) < 2:
        raise ValueError("Language code must be a valid string.")
    tokenizer, model = load_intent_model_and_tokenizer(MODEL_NAME)
    model.eval()
    input_text = f"[{lang_code}] {text}"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        intent_idx = torch.argmax(logits, dim=1).item()
    return INTENT_LABELS[intent_idx] if intent_idx < len(INTENT_LABELS) else "unknown"

# --- KEYWORD EXTRACTION ---
def extract_keywords(text: str, top_n: int = 5, model_name: str = KEYBERT_MODEL) -> List[str]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must be a non-empty string.")
    try:
        model = SentenceTransformer(model_name)
        kw_model = KeyBERT(model)
        keywords = kw_model.extract_keywords(text, top_n=top_n, stop_words=None)
        return [kw[0] for kw in keywords]
    except Exception as e:
        raise RuntimeError(f"Keyword extraction failed: {e}")

# --- MAIN INTEGRATION ---
def analyze_text(text: str, lang_code: str, top_n_keywords: int = 5) -> Dict[str, object]:
    intent = classify_intent(text, lang_code)
    keywords = extract_keywords(text, top_n=top_n_keywords)
    return {"intent": intent, "keywords": keywords}

def main():
    if len(sys.argv) < 3:
        print("Usage: python analyze_intent_keywords.py <text> <lang_code> [top_n_keywords]")
        sys.exit(1)
    text = sys.argv[1]
    lang_code = sys.argv[2]
    top_n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    try:
        result = analyze_text(text, lang_code, top_n)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
