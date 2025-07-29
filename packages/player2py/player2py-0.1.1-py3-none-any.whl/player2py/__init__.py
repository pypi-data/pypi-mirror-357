"""
Player2 Python Client

A Python client for the Player2 API - AI powered gaming tools.
"""

from .client import Player2Client
from .exceptions import Player2Error, Player2AuthError, Player2RateLimitError
from .models import (
    Character,
    ChatCompletion,
    ChatCompletionRequest,
    Health,
    Language,
    LanguageInfo,
    Languages,
    ListVoices,
    Message,
    ResponseMessage,
    SetLanguageRequest,
    SetVolumeRequest,
    SingleTextToSpeechData,
    SingleTextToSpeechRequest,
    StartSpeechToTextRequest,
    StopSpeechToTextData,
    Voice,
    VolumeData,
)

__version__ = "0.1.0"
__author__ = "Alex Mueller"

__all__ = [
    "Player2Client",
    "Player2Error",
    "Player2AuthError", 
    "Player2RateLimitError",
    "Character",
    "ChatCompletion",
    "ChatCompletionRequest",
    "Health",
    "Language",
    "LanguageInfo",
    "Languages",
    "ListVoices",
    "Message",
    "ResponseMessage",
    "SetLanguageRequest",
    "SetVolumeRequest",
    "SingleTextToSpeechData",
    "SingleTextToSpeechRequest",
    "StartSpeechToTextRequest",
    "StopSpeechToTextData",
    "Voice",
    "VolumeData",
] 