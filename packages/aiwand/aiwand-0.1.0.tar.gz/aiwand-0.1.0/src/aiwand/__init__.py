"""
AIWand - A simple AI toolkit for text processing using OpenAI
"""

__version__ = "0.1.0"
__author__ = "Aman Kumar"

from .core import summarize, chat, generate_text
from .config import configure_api_key, get_api_key

__all__ = [
    "summarize",
    "chat", 
    "generate_text",
    "configure_api_key",
    "get_api_key",
] 