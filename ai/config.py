"""
ai/config.py - Secure configuration with environment variables
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# ---------------------------------------------------------
# 🔐 1. Load environment variables
# ---------------------------------------------------------


# Switch between "local", "openai", or "hybrid"
AI_MODE = os.getenv("AI_MODE", "hybrid")



# ---------------------------------------------------------
# 🤖 2. Model Configuration - UPDATED WITH CURRENT PRODUCTION MODELS
# ---------------------------------------------------------

@dataclass
class ModelConfig:
    # Groq Configuration from environment
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_base_url: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    ai_mode: str = os.getenv("AI_MODE", "groq")
    
    # Model settings
    groq_chat_model: str = "llama-3.1-8b-instant"
    groq_diagnosis_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.7
    
    # Local fallback
    local_model_path: str = "models/local/llama-3-8b"
    
    # Safety limits
    max_tokens_conversation: int = 800
    max_tokens_diagnosis: int = 1500

config = ModelConfig()

def get_groq_client():
    """Safely create Groq client with environment validation"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment variables.\n"
            "Please create a .env file with your API key.\n"
            "See .env.example for template."
        )
    
    from openai import OpenAI
    return OpenAI(
        api_key=api_key,
        base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    )

def select_model(task_type: str) -> str:
    """Determine which model to use based on configuration"""
    ai_mode = os.getenv("AI_MODE", "groq")
    
    if ai_mode == "groq":
        return "groq"
    elif ai_mode == "local":
        return "local"
    elif ai_mode == "hybrid":
        if task_type in ["conversation", "diagnosis"]:
            return "groq"
        elif task_type in ["pattern_analysis", "emotion_analysis"]:
            return "local"
    
    return "groq"  # Default fallback

def validate_environment():
    """Validate that required environment variables are set"""
    required = ['GROQ_API_KEY']
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        raise EnvironmentError(
            f"Missing environment variables: {', '.join(missing)}\n"
            "Please set these in your .env file"
        )
    
    return True