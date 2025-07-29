"""
Unit tests for the Player2 client.
"""

import pytest
from unittest.mock import Mock, patch
from player2 import Player2Client
from player2.exceptions import Player2Error, Player2AuthError, Player2RateLimitError
from player2.models import Health, Characters, ChatCompletion


class TestPlayer2Client:
    """Test cases for Player2Client."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = Player2Client(game_name="test-game")
    
    def test_client_initialization(self):
        """Test client initialization."""
        assert self.client.base_url == "http://localhost:4315"
        assert self.client.game_name == "test-game"
        assert self.client.timeout == 30
        assert "player2-game-key" in self.client.session.headers
    
    def test_client_with_custom_url(self):
        """Test client with custom base URL."""
        client = Player2Client(
            base_url="http://127.0.0.1:4315",
            game_name="test-game"
        )
        assert client.base_url == "http://127.0.0.1:4315"
    
    @patch('player2.client.requests.Session.request')
    def test_health_success(self, mock_request):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"client_version": "1.0.0"}
        mock_request.return_value = mock_response
        
        health = self.client.health()
        
        assert isinstance(health, Health)
        assert health.client_version == "1.0.0"
        mock_request.assert_called_once()
    
    @patch('player2.client.requests.Session.request')
    def test_health_auth_error(self, mock_request):
        """Test health check with authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        with pytest.raises(Player2AuthError):
            self.client.health()
    
    @patch('player2.client.requests.Session.request')
    def test_health_rate_limit_error(self, mock_request):
        """Test health check with rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_request.return_value = mock_response
        
        with pytest.raises(Player2RateLimitError):
            self.client.health()
    
    @patch('player2.client.requests.Session.request')
    def test_get_selected_characters_success(self, mock_request):
        """Test successful get selected characters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "characters": [
                {
                    "id": "char1",
                    "name": "Test Character",
                    "short_name": "Test",
                    "greeting": "Hello!",
                    "description": "A test character",
                    "voice_ids": ["voice1"],
                    "meta": {"skin_url": "http://example.com/skin.png"}
                }
            ]
        }
        mock_request.return_value = mock_response
        
        characters = self.client.get_selected_characters()
        
        assert isinstance(characters, Characters)
        assert len(characters.characters) == 1
        assert characters.characters[0].name == "Test Character"
    
    @patch('player2.client.requests.Session.request')
    def test_chat_completions_success(self, mock_request):
        """Test successful chat completion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Hello! How can I help you?",
                        "tool_calls": None
                    }
                }
            ]
        }
        mock_request.return_value = mock_response
        
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        response = self.client.chat_completions(messages=messages)
        
        assert isinstance(response, ChatCompletion)
        assert len(response.choices) == 1
        assert response.choices[0]["message"]["content"] == "Hello! How can I help you?"
    
    @patch('player2.client.requests.Session.request')
    def test_connection_error(self, mock_request):
        """Test connection error handling."""
        mock_request.side_effect = Exception("Connection failed")
        
        with pytest.raises(Player2Error) as exc_info:
            self.client.health()
        
        assert "Connection error" in str(exc_info.value)
    
    def test_context_manager(self):
        """Test client as context manager."""
        with Player2Client(game_name="test") as client:
            assert isinstance(client, Player2Client)
            # Client should be closed after context exit
            assert client.session is not None


class TestPlayer2ClientSTT:
    """Test cases for Speech-to-Text functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = Player2Client(game_name="test-game")
    
    @patch('player2.client.requests.Session.request')
    def test_stt_start_success(self, mock_request):
        """Test successful STT start."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        
        # Should not raise an exception
        self.client.stt_start(timeout=30)
        mock_request.assert_called_once()
    
    @patch('player2.client.requests.Session.request')
    def test_stt_stop_success(self, mock_request):
        """Test successful STT stop."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"text": "Hello world"}
        mock_request.return_value = mock_response
        
        result = self.client.stt_stop()
        
        assert result.text == "Hello world"
        mock_request.assert_called_once()


class TestPlayer2ClientTTS:
    """Test cases for Text-to-Speech functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = Player2Client(game_name="test-game")
    
    @patch('player2.client.requests.Session.request')
    def test_tts_speak_success(self, mock_request):
        """Test successful TTS speak."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "base64_audio_data"}
        mock_request.return_value = mock_response
        
        result = self.client.tts_speak(
            text="Hello world",
            voice_ids=["voice1"],
            play_in_app=False
        )
        
        assert result.data == "base64_audio_data"
        mock_request.assert_called_once()
    
    @patch('player2.client.requests.Session.request')
    def test_tts_voices_success(self, mock_request):
        """Test successful TTS voices list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "voices": [
                {
                    "id": "voice1",
                    "name": "Test Voice",
                    "language": "en_US",
                    "gender": "female"
                }
            ]
        }
        mock_request.return_value = mock_response
        
        voices = self.client.tts_voices()
        
        assert len(voices.voices) == 1
        assert voices.voices[0].name == "Test Voice"
        mock_request.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__]) 