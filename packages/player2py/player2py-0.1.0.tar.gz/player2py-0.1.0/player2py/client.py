"""
Main Player2 API client.
"""

import json
import requests
from typing import List, Optional, Dict, Any
from .exceptions import (
    Player2Error,
    Player2AuthError,
    Player2RateLimitError,
    Player2NotFoundError,
    Player2ConflictError,
    Player2ServiceUnavailableError,
    Player2ValidationError,
)
from .models import (
    Characters,
    ChatCompletion,
    ChatCompletionRequest,
    Health,
    Language,
    Languages,
    ListVoices,
    Message,
    SetLanguageRequest,
    SetVolumeRequest,
    SingleTextToSpeechData,
    SingleTextToSpeechRequest,
    StartSpeechToTextRequest,
    StopSpeechToTextData,
    VolumeData,
    RequestError,
)


class Player2Client:
    """
    Player2 API client.
    
    Provides a Python interface to the Player2 API for AI-powered gaming tools.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:4315",
        game_name: str = "python-client",
        timeout: int = 30,
    ):
        """
        Initialize the Player2 client.
        
        Args:
            base_url: Base URL for the Player2 API
            game_name: Name of your game for tracking purposes
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.game_name = game_name
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "player2-game-key": game_name,
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Player2 API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            **kwargs: Additional request arguments
            
        Returns:
            Response data
            
        Raises:
            Player2Error: Base exception for API errors
            Player2AuthError: Authentication error
            Player2RateLimitError: Rate limit exceeded
            Player2NotFoundError: Resource not found
            Player2ConflictError: Conflict error
            Player2ServiceUnavailableError: Service unavailable
            Player2ValidationError: Validation error
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=self.timeout,
                **kwargs
            )
            
            # Handle different status codes
            if response.status_code == 200:
                return response.json() if response.content else {}
            elif response.status_code == 401:
                raise Player2AuthError("Authentication required - please log in to Player2 App")
            elif response.status_code == 404:
                error_data = response.json() if response.content else {}
                message = error_data.get("message", "Resource not found")
                raise Player2NotFoundError(message)
            elif response.status_code == 409:
                error_data = response.json() if response.content else {}
                message = error_data.get("message", "Conflict occurred")
                raise Player2ConflictError(message)
            elif response.status_code == 429:
                raise Player2RateLimitError("Rate limit exceeded - please wait before making more requests")
            elif response.status_code == 503:
                error_data = response.json() if response.content else {}
                message = error_data.get("message", "Service unavailable")
                raise Player2ServiceUnavailableError(message)
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                message = error_data.get("message", "Invalid request")
                raise Player2ValidationError(message)
            elif response.status_code >= 500:
                raise Player2Error(f"Server error: {response.status_code}")
            else:
                raise Player2Error(f"Unexpected status code: {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise Player2Error("Request timeout")
        except requests.exceptions.ConnectionError:
            raise Player2Error(f"Connection error - make sure Player2 App is running at {self.base_url}")
        except requests.exceptions.RequestException as e:
            raise Player2Error(f"Request failed: {str(e)}")
    
    def health(self) -> Health:
        """
        Get health status of the Player2 server.
        
        Returns:
            Health information including client version
        """
        data = self._make_request("GET", "/v1/health")
        return Health(**data)
    
    def get_selected_characters(self) -> Characters:
        """
        Get selected characters from the Player2 App.
        
        Returns:
            List of selected characters
        """
        data = self._make_request("GET", "/v1/selected_characters")
        return Characters(**data)
    
    def chat_completions(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> ChatCompletion:
        """
        Create a chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters
            
        Returns:
            Chat completion response
        """
        request_data = {
            "messages": messages,
            **kwargs
        }
        data = self._make_request("POST", "/v1/chat/completions", request_data)
        return ChatCompletion(**data)
    
    def stt_start(self, timeout: int = 30) -> None:
        """
        Start speech to text recognition.
        
        Args:
            timeout: Timeout duration in seconds (1-300)
        """
        request_data = StartSpeechToTextRequest(timeout=timeout).dict()
        self._make_request("POST", "/v1/stt/start", request_data)
    
    def stt_stop(self) -> StopSpeechToTextData:
        """
        Stop speech to text recognition and get recognized text.
        
        Returns:
            Recognized text
        """
        data = self._make_request("POST", "/v1/stt/stop")
        return StopSpeechToTextData(**data)
    
    def stt_languages(self) -> Languages:
        """
        Get available languages for speech to text.
        
        Returns:
            List of available languages
        """
        data = self._make_request("GET", "/v1/stt/languages")
        return Languages(**data)
    
    def stt_get_language(self) -> Language:
        """
        Get current speech to text language.
        
        Returns:
            Current language information
        """
        data = self._make_request("GET", "/v1/stt/language")
        return Language(**data)
    
    def stt_set_language(self, code: str) -> None:
        """
        Set speech to text language.
        
        Args:
            code: Language code (e.g., "en-US")
        """
        request_data = SetLanguageRequest(code=code).dict()
        self._make_request("POST", "/v1/stt/language", request_data)
    
    def tts_voices(self) -> ListVoices:
        """
        Get available voices for text to speech.
        
        Returns:
            List of available voices
        """
        data = self._make_request("GET", "/v1/tts/voices")
        return ListVoices(**data)
    
    def tts_speak(
        self,
        text: str,
        voice_ids: List[str],
        play_in_app: bool = True,
        speed: float = 1.0,
        voice_gender: Optional[str] = None,
        voice_language: Optional[str] = None,
        audio_format: str = "mp3",
    ) -> Optional[SingleTextToSpeechData]:
        """
        Convert text to speech.
        
        Args:
            text: Text to convert to speech
            voice_ids: List of voice IDs to use
            play_in_app: Whether to play audio in the app
            speed: Speech speed (0.1-5.0)
            voice_gender: Voice gender (male, female, other)
            voice_language: Voice language code
            audio_format: Audio format (mp3, opus, flac, wav, pcm)
            
        Returns:
            Audio data if play_in_app is False, None otherwise
        """
        request_data = SingleTextToSpeechRequest(
            text=text,
            voice_ids=voice_ids,
            play_in_app=play_in_app,
            speed=speed,
            voice_gender=voice_gender,
            voice_language=voice_language,
            audio_format=audio_format,
        ).dict()
        
        data = self._make_request("POST", "/v1/tts/speak", request_data)
        
        if play_in_app:
            return None
        else:
            return SingleTextToSpeechData(**data)
    
    def tts_stop(self) -> None:
        """
        Stop current text to speech playback.
        """
        self._make_request("POST", "/v1/tts/stop")
    
    def tts_get_volume(self) -> VolumeData:
        """
        Get current audio volume.
        
        Returns:
            Current volume level (0.0-1.0)
        """
        data = self._make_request("GET", "/v1/tts/volume")
        return VolumeData(**data)
    
    def tts_set_volume(self, volume: float) -> None:
        """
        Set audio volume.
        
        Args:
            volume: Volume level (0.0-1.0)
        """
        request_data = SetVolumeRequest(volume=volume).dict()
        self._make_request("POST", "/v1/tts/volume", request_data)
    
    def close(self) -> None:
        """
        Close the client session.
        """
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 