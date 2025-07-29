"""
Google Chat Bot Framework (gchatbot)

A Python framework for easily creating modern Google Chat bots.
This library provides a robust FastAPI-based implementation with serverless-safe
background task processing for reliable operation in environments like Google Cloud Run.
"""

# --- Modern FastAPI Implementation (Recommended) ---
from .main import GChatBot
from .parser import EventParser
from .processor import AsyncProcessor
from .response import ResponseFactory
from .types import ExtractedEventData, EventPayload, ProgressiveResponse, ResponseType

# The primary class to be used by developers is GChatBot.
# Legacy classes are included for existing projects.
__all__ = [
    # Recommended
    'GChatBot',

    # Modular components (for advanced use with the modern GChatBot)
    'EventParser',
    'AsyncProcessor',
    'ResponseFactory',
    
    # Type definitions
    'ExtractedEventData',
    'EventPayload',
    'ProgressiveResponse',
    'ResponseType',
] 