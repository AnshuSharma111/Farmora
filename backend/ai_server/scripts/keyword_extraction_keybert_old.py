import sys
from typing import List
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

def extract_keywords(text: str, top_n: int = 5, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2") -> List[str]:
    """
    Extracts keywords from text using KeyBERT with a multilingual model.
    Args:
        text (str): Input text in any language.
        top_n (int): Number of keywords to return.
        model_name (str): SentenceTransformer model name.
    Returns:
        List[str]: List of extracted keywords.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must be a non-empty string.")
    try:
        model = SentenceTransformer(model_name)
        kw_model = KeyBERT(model)
        keywords = kw_model.extract_keywords(text, top_n=top_n, stop_words=None)
        return [kw[0] for kw in keywords]
    except Exception as e:
        raise RuntimeError(f"Keyword extraction failed: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python keyword_extraction_keybert.py <text> [top_n]")
        sys.exit(1)
    text = sys.argv[1]
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    try:
        keywords = extract_keywords(text, top_n=top_n)
        print(keywords)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
