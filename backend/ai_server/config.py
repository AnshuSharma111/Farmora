import os
import logging
from pathlib import Path

# Base directories
ROOT_DIR = Path(__file__).parent.absolute()
MODELS_DIR = ROOT_DIR / "models"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(ROOT_DIR / "farmora_ai.log")
    ]
)

logger = logging.getLogger("farmora_ai")

class AppConfig:
    """Configuration for the Farmora AI Server"""
    
    # Server settings
    PORT = int(os.getenv("PORT", 8000))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"
    
    # Authentication
    APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
    APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID", "")
    APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY", "")
    
    # Model paths
    ASR_MODEL_PATH = MODELS_DIR / "asr" / "whisper-small"
    INTENT_MODEL_PATH = MODELS_DIR / "intent" / "xlm-roberta-base"
    TRANSLATION_MODEL_PATH = MODELS_DIR / "translation" / "indictrans2"
    LLM_MODEL_PATH = MODELS_DIR / "llm" / "mistral-7b"
    
    # API keys for external services
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    
    # Performance settings
    ASR_CONFIDENCE_THRESHOLD = float(os.getenv("ASR_CONFIDENCE_THRESHOLD", 0.7))
    INTENT_CONFIDENCE_THRESHOLD = float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", 0.6))
    TRANSLATION_LATENCY_THRESHOLD = int(os.getenv("TRANSLATION_LATENCY_THRESHOLD", 200))
    
    # Use mock responses for development/testing
    USE_MOCK_RESPONSES = os.getenv("USE_MOCK_RESPONSES", "False").lower() in ("true", "1", "t")
    
    # Hardware settings
    @classmethod
    def use_gpu(cls):
        """Check if GPU should be used"""
        try:
            import torch
            return (os.getenv("USE_GPU", "True").lower() in ("true", "1", "t") and 
                    torch.cuda.is_available())
        except ImportError:
            return False
    
    @classmethod
    def get_device(cls):
        """Get the appropriate device for model inference"""
        try:
            import torch
            if cls.use_gpu():
                return torch.device("cuda")
            return torch.device("cpu")
        except ImportError:
            return "cpu"


config = AppConfig()
