# Farmora AI Server

This is the AI processing server for the Farmora application. It implements the multi-stage pipeline described in the architecture document.

## Architecture Overview

The AI server implements the following pipeline components:

1. **ASR (Automatic Speech Recognition)**
   - Uses Whisper-small for speech-to-text
   - Supports Hindi, English, and other Indian languages
   - Implements streaming via WebSockets

2. **Intent Classification & Entity Extraction**
   - Uses Groq API (Llama 3 70B) for intent classification and tool suggestion
   - Extracts keywords from queries in any language
   - Provides confidence scores for routing decisions

3. **Translation/Normalization**
   - Uses Groq API with HuggingFace fallback for high-quality translation
   - Supports all major Indian languages and many others
   - Preserves entities across translation
   - Auto-detects source language when needed

4. **Tool Integration**
   - Weather data (Open-Meteo API)
   - Commodity price data (Enhanced AGMARKNET scraping with robust features)
     - Complete database of all Indian states, districts, and markets
     - Smart geographical proximity-based market selection
     - Automatic district name normalization (e.g., Hisar/Hissar, Gurugram/Gurgaon)
     - Multiple fallback mechanisms for reliable data retrieval
     - Seasonal crop information when price data isn't available
     - Supports multi-commodity lookup in a single request
   - Translation services for multilingual support
   - Geolocation services with offline fallback
   - (Planned) Disease identification
   - (Planned) Government schemes
   - (Planned) Soil health recommendations

5. **LLM Generation**
   - Uses Groq API (Llama 3 70B) for response synthesis
   - Optimizes prompts for agricultural domain
   - Provides multilingual response capabilities

6. **Moderator**
   - Validates outputs at each step
   - Implements fallback and recovery mechanisms
   - Performs relevance checks on final responses

## Directory Structure

```
ai_server/
├── DOCUMENTATION.MD         # Detailed function documentation
├── README.md                # This file
├── requirements.txt         # Dependencies
├── scripts/                 # Core script components
│   ├── analyze_intent_keywords.py  # Intent classification and keyword extraction
│   ├── batch_transcribe_and_analyze.py  # Batch processing utilities
│   ├── identify_intent_keyword.py  # Legacy code
│   ├── keyword_extraction_keybert.py  # Legacy code
│   ├── transcribe_whisper.py  # Audio transcription with Whisper
│   ├── translate.py         # Translation functionality
│   └── processing.py        # Main pipeline integration
├── tools/                   # External data sources
│   ├── weather_api.py       # Weather data integration
│   ├── scrape_commodity.py  # Price data scraping from AGMARKNET
│   └── (future tools)       # Disease identification, government schemes, etc.
└── test/                    # Test scripts and examples
    ├── batch_transcribe_and_analyze.py  # Batch testing
    ├── test_processing.py   # End-to-end pipeline tests
    └── test_translate.py    # Translation functionality tests
```

## Setup and Installation

### Prerequisites
- Python 3.9+
- CUDA-compatible GPU recommended for inference

### Installation

1. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Download model weights:
   ```bash
   python scripts/download_models.py
   ```

5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## Docker Setup

Build and run with Docker:

```bash
docker build -t farmora-ai-server .
docker run -p 8000:8000 farmora-ai-server
```

Or use Docker Compose to run the entire stack:

```bash
docker-compose up
```

## Development

### Running Tests

```bash
pytest
```

### API Documentation

FastAPI automatically generates API documentation, available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
