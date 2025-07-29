"""
Pydantic models for Player2 API requests and responses.
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class CharacterMeta(BaseModel):
    """Character metadata."""
    skin_url: Optional[str] = None


class CharacterMinecraftMeta(BaseModel):
    """Minecraft-specific character metadata."""
    type: str = Field(..., example="Minecraft")
    skin_url: str


class Character(BaseModel):
    """Character model."""
    id: str
    name: str
    short_name: str
    greeting: str
    description: str
    voice_ids: List[str]
    meta: Optional[Union[CharacterMeta, CharacterMinecraftMeta]] = None


class Characters(BaseModel):
    """Characters response model."""
    characters: List[Character]


class Message(BaseModel):
    """Chat message model."""
    role: str
    content: str


class FunctionCall(BaseModel):
    """Function call model."""
    name: str
    arguments: str


class ToolCall(BaseModel):
    """Tool call model."""
    id: Optional[str] = None
    type: Optional[str] = None
    function: FunctionCall


class ResponseMessage(BaseModel):
    """Response message model."""
    content: str
    tool_calls: Optional[List[ToolCall]] = None


class ChatCompletion(BaseModel):
    """Chat completion response model."""
    choices: List[Dict[str, ResponseMessage]]


class ChatCompletionRequest(BaseModel):
    """Chat completion request model."""
    messages: List[Message]


class Health(BaseModel):
    """Health response model."""
    client_version: str


class LanguageInfo(BaseModel):
    """Language information model."""
    name: str
    code: str


class Languages(BaseModel):
    """Languages response model."""
    languages: List[LanguageInfo]


class Language(BaseModel):
    """Language model."""
    code: str
    name: str


class SetLanguageRequest(BaseModel):
    """Set language request model."""
    code: str = Field(..., example="en-US")


class StartSpeechToTextRequest(BaseModel):
    """Start speech to text request model."""
    timeout: int = Field(..., ge=1, le=300)


class StopSpeechToTextData(BaseModel):
    """Stop speech to text response model."""
    text: str


class Voice(BaseModel):
    """Voice model."""
    id: str
    name: str
    language: str
    gender: str


class ListVoices(BaseModel):
    """List voices response model."""
    voices: List[Voice]


class SingleTextToSpeechRequest(BaseModel):
    """Text to speech request model."""
    text: str
    voice_ids: List[str]
    play_in_app: bool = True
    speed: float = Field(1.0, ge=0.1, le=5.0)
    voice_gender: Optional[str] = Field(None, regex="^(male|female|other)$")
    voice_language: Optional[str] = Field(
        None, 
        regex="^(en_US|en_GB|ja_JP|zh_CN|es_ES|fr_FR|hi_IN|it_IT|pt_BR)$"
    )
    audio_format: str = Field("mp3", regex="^(mp3|opus|flac|wav|pcm)$")


class SingleTextToSpeechData(BaseModel):
    """Text to speech response model."""
    data: str


class SetVolumeRequest(BaseModel):
    """Set volume request model."""
    volume: float = Field(..., ge=0.0, le=1.0)


class VolumeData(BaseModel):
    """Volume data model."""
    volume: float = Field(..., ge=0.0, le=1.0)


class RequestError(BaseModel):
    """Error response model."""
    message: str 