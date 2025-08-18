import sys
from typing import Dict
import torch
from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification

# Path to your fine-tuned model or use 'xlm-roberta-base' for demo
MODEL_NAME = "xlm-roberta-base"

# Example intent labels (update as per your fine-tuned model)
INTENT_LABELS = [
    "greeting",
    "weather_query",
    "crop_query",
    "pesticide_query",
    "rate_query",
    "mandi_query",
    "other"
]

def load_model_and_tokenizer(model_name: str):
    """Load XLM-RoBERTa model and tokenizer."""
    try:
        tokenizer = XLMRobertaTokenizer.from_pretrained(model_name)
        model = XLMRobertaForSequenceClassification.from_pretrained(model_name)
        return tokenizer, model
    except Exception as e:
        raise RuntimeError(f"Failed to load model/tokenizer: {e}")

def classify_intent(text: str, lang_code: str) -> Dict[str, str]:
    """
    Classifies the intent of a multilingual farm-related query.
    Args:
        text (str): Input query in any language.
        lang_code (str): Language code (e.g., 'en', 'hi').
    Returns:
        Dict[str, str]: {"intent": intent_label}
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must be a non-empty string.")
    if not isinstance(lang_code, str) or len(lang_code) < 2:
        raise ValueError("Language code must be a valid string.")

    tokenizer, model = load_model_and_tokenizer(MODEL_NAME)
    model.eval()

    # Optionally, prepend language code to help the model (if fine-tuned this way)
    input_text = f"[{lang_code}] {text}"
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        intent_idx = torch.argmax(logits, dim=1).item()

    intent = INTENT_LABELS[intent_idx] if intent_idx < len(INTENT_LABELS) else "unknown"
    return {"intent": intent}

def main():
    if len(sys.argv) != 3:
        print("Usage: python identify_intent_keyword.py <text> <lang_code>")
        sys.exit(1)
    text = sys.argv[1]
    lang_code = sys.argv[2]
    try:
        result = classify_intent(text, lang_code)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
