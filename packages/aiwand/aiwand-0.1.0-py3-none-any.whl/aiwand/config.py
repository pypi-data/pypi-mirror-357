"""
Configuration module for AIWand
"""

import os
from typing import Optional, Literal, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

_api_key: Optional[str] = None
_provider: Optional[str] = None

Provider = Literal["openai", "gemini"]


def configure_api_key(api_key: str, provider: Provider = "openai") -> None:
    """
    Configure the API key and provider.
    
    Args:
        api_key (str): Your API key (OpenAI or Gemini)
        provider (str): The AI provider to use ("openai" or "gemini")
    """
    global _api_key, _provider
    _api_key = api_key
    _provider = provider


def get_api_key_and_provider() -> Tuple[str, str]:
    """
    Get the API key and provider from configuration or environment.
    Smart selection based on available keys and preferences.
    
    Returns:
        Tuple[str, str]: (api_key, provider)
        
    Raises:
        ValueError: If no API key is found
    """
    global _api_key, _provider
    
    # Check if API key was set programmatically
    if _api_key and _provider:
        return _api_key, _provider
    
    # Check what API keys are available
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    # If no keys available, raise error
    if not openai_key and not gemini_key:
        raise ValueError(
            "No API key found. Please set one using:\n"
            "1. aiwand.configure_api_key('your-api-key', 'openai') or aiwand.configure_api_key('your-api-key', 'gemini')\n"
            "2. Set OPENAI_API_KEY or GEMINI_API_KEY environment variable\n"
            "3. Create a .env file with OPENAI_API_KEY=your-key or GEMINI_API_KEY=your-key"
        )
    
    # If only one key is available, use that provider
    if openai_key and not gemini_key:
        return openai_key, "openai"
    elif gemini_key and not openai_key:
        return gemini_key, "gemini"
    
    # Both keys available - check AI_DEFAULT_PROVIDER preference
    default_provider = os.getenv("AI_DEFAULT_PROVIDER", "gemini").lower()
    
    if default_provider == "gemini" and gemini_key:
        return gemini_key, "gemini"
    elif default_provider == "openai" and openai_key:
        return openai_key, "openai"
    
    # Fallback to openai if both available
    return openai_key, "openai"


def get_api_key() -> str:
    """
    Get the API key (backward compatibility).
    
    Returns:
        str: The API key
    """
    api_key, _ = get_api_key_and_provider()
    return api_key 