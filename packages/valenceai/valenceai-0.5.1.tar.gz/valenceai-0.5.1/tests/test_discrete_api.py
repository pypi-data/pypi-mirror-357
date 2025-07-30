import pytest
import os
from unittest.mock import Mock, patch, mock_open
from valenceai import ValenceClient
from valenceai.exceptions import ValenceSDKException


class TestDiscreteAPI:
    
    def test_init_with_env_var(self):
        """Test initialization with API key from environment variable."""
        with patch('valenceai.client.API_KEY', 'test_api_key'):
            client = ValenceClient()
            assert client.api_key == 'test_api_key'
            assert client.headers == {"x-api-key": 'test_api_key'}
            assert hasattr(client, 'discrete')
            assert hasattr(client, 'asynch')
    
    def test_init_with_explicit_key(self):
        """Test initialization with explicitly provided API key."""
        client = ValenceClient(api_key='explicit_key')
        assert client.api_key == 'explicit_key'
        assert client.headers == {"x-api-key": 'explicit_key'}
    
    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key_raises_exception(self):
        """Test that initialization without API key raises exception."""
        with pytest.raises(ValenceSDKException, match="API key not provided"):
            ValenceClient()
    
    @patch('valenceai.client.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data')
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_discrete_emotions_success(self, mock_file, mock_post):
        """Test successful emotion prediction."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "emotions": {"happy": 0.8, "sad": 0.2},
            "dominant_emotion": "happy"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = ValenceClient()
        result = client.discrete.emotions("test_file.wav", model="7emotions")
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check URL and headers
        assert call_args[1]['headers'] == {"x-api-key": 'test_key'}
        assert call_args[1]['params'] == {"model": "7emotions"}
        assert 'files' in call_args[1]
        
        # Check response
        assert result == {"emotions": {"happy": 0.8, "sad": 0.2}, "dominant_emotion": "happy"}
    
    @patch('valenceai.client.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data')
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_discrete_emotions_default_model(self, mock_file, mock_post):
        """Test emotion prediction with default model."""
        mock_response = Mock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = ValenceClient()
        client.discrete.emotions("test_file.wav")
        
        # Check that default model is used
        call_args = mock_post.call_args
        assert call_args[1]['params'] == {"model": "4emotions"}
    
    @patch('valenceai.client.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data')
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_discrete_emotions_http_error(self, mock_file, mock_post):
        """Test emotion prediction with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 500 Error")
        mock_post.return_value = mock_response
        
        client = ValenceClient()
        
        with pytest.raises(Exception, match="HTTP 500 Error"):
            client.discrete.emotions("test_file.wav")
    
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_discrete_emotions_file_not_found(self):
        """Test emotion prediction with non-existent file."""
        client = ValenceClient()
        
        with pytest.raises(FileNotFoundError):
            client.discrete.emotions("non_existent_file.wav")
    
    @patch('valenceai.client.requests.post')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data')
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_discrete_emotions_custom_model(self, mock_file, mock_post):
        """Test emotion prediction with custom model parameter."""
        mock_response = Mock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        client = ValenceClient()
        client.discrete.emotions("test_file.wav", model="7emotions")
        
        # Verify custom model parameter
        call_args = mock_post.call_args
        assert call_args[1]['params'] == {"model": "7emotions"}