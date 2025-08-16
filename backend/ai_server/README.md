# Farmora AI Server

This is the AI processing server for the Farmora application. It implements the multi-stage pipeline described in the architecture document.

## Architecture Overview

The AI server implements the following pipeline components:

1. **ASR (Automatic Speech Recognition)**
   - Uses Whisper-small for speech-to-text
   - Supports Hindi, English, and other Indian languages
   - Implements streaming via WebSockets

2. **Intent Classification & Entity Extraction**
   - Uses XLM-RoBERTa for multi-label classification
   - Extracts crop names, location mentions, and other entities
   - Provides confidence scores for routing decisions

3. **Translation/Normalization**
   - Uses IndicTrans2 for cross-lingual capabilities
   - Selectively translates based on tool requirements
   - Preserves entities across translation

4. **Tool Integration**
   - Weather data (Open-Meteo API)
   - Market prices (AGMARKNET API)
   - Disease identification
   - Government schemes
   - Soil health recommendations

5. **LLM Generation**
   - Uses Mistral/Gemma models for response synthesis
   - Implements fallback to API LLMs for complex queries
   - Optimizes prompts for agricultural domain

6. **Moderator**
   - Validates outputs at each step
   - Implements fallback and recovery mechanisms
   - Performs relevance checks on final responses

## Directory Structure

```
ai_server/
├── main.py                  # FastAPI application entry point
├── auth.py                  # Authentication with Appwrite
├── config.py                # Configuration management
├── monitoring/              # Logging and monitoring components
├── models/                  # ML model wrappers
│   ├── asr/                 # Speech recognition (Whisper)
│   ├── intent/              # Intent classification (XLM-R)
│   ├── translation/         # Translation models (IndicTrans2)
│   └── llm/                 # Language models (Mistral/Gemma)
├── pipeline/                # Pipeline orchestration
│   ├── moderator.py         # Validation and recovery logic
│   ├── router.py            # Request routing logic
│   └── streaming.py         # Streaming implementation
├── tools/                   # External data sources
│   ├── weather.py           # Weather data integration
│   ├── markets.py           # Price data integration
│   ├── diseases.py          # Disease identification
│   ├── schemes.py           # Government scheme lookup
│   └── soil.py              # Soil health recommendations
├── schemas/                 # Data models and schemas
├── utils/                   # Utility functions
└── tests/                   # Test suite
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
