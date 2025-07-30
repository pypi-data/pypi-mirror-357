import pytest
import os
from unittest.mock import patch
from valenceai.config import API_KEY, VALENCE_DISCRETE_URL, VALENCE_ASYNCH_URL
from valenceai.exceptions import ValenceSDKException, UploadError, PredictionError
from valenceai.client import ValenceClient


class TestConfiguration:
    
    @patch.dict(os.environ, {'VALENCE_API_KEY': 'test_env_key'})
    def test_api_key_from_environment(self):
        """Test API key is read from environment variable."""
        # Need to reload the config module to pick up the new env var
        import importlib
        from valenceai import config
        importlib.reload(config)
        
        assert config.API_KEY == 'test_env_key'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_api_key_none_when_not_set(self):
        """Test API key is None when not set in environment."""
        import importlib
        from valenceai import config
        importlib.reload(config)
        
        assert config.API_KEY is None
    
    @patch.dict(os.environ, {'VALENCE_DISCRETE_URL': 'https://custom-short-url.com'})
    def test_short_audio_url_custom(self):
        """Test VALENCE_DISCRETE_URL can be customized via environment."""
        import importlib
        from valenceai import config
        importlib.reload(config)
        
        assert config.VALENCE_DISCRETE_URL == 'https://custom-short-url.com'
    
    def test_short_audio_url_default(self):
        """Test VALENCE_DISCRETE_URL has correct default value."""
        # Reset environment
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            from valenceai import config
            importlib.reload(config)
            
            expected_default = "https://xc8n2bo4f0.execute-api.us-west-2.amazonaws.com/emotionprediction"
            assert config.VALENCE_DISCRETE_URL == expected_default
    
    @patch.dict(os.environ, {'VALENCE_ASYNCH_URL': 'https://custom-long-url.com'})
    def test_long_audio_url_custom(self):
        """Test VALENCE_ASYNCH_URL can be customized via environment."""
        import importlib
        from valenceai import config
        importlib.reload(config)
        
        assert config.VALENCE_ASYNCH_URL == 'https://custom-long-url.com'
    
    def test_long_audio_url_default(self):
        """Test VALENCE_ASYNCH_URL has correct default value."""
        with patch.dict(os.environ, {}, clear=True):
            import importlib
            from valenceai import config
            importlib.reload(config)
            
            expected_default = "https://wsgol61783.execute-api.us-west-2.amazonaws.com/prod"
            assert config.VALENCE_ASYNCH_URL == expected_default


class TestExceptions:
    
    def test_valenceai_exception_inheritance(self):
        """Test ValenceSDKException inherits from Exception."""
        assert issubclass(ValenceSDKException, Exception)
    
    def test_upload_error_inheritance(self):
        """Test UploadError inherits from ValenceSDKException."""
        assert issubclass(UploadError, ValenceSDKException)
        assert issubclass(UploadError, Exception)
    
    def test_prediction_error_inheritance(self):
        """Test PredictionError inherits from ValenceSDKException."""
        assert issubclass(PredictionError, ValenceSDKException)
        assert issubclass(PredictionError, Exception)
    
    def test_valenceai_exception_with_message(self):
        """Test ValenceSDKException can be raised with message."""
        message = "Test error message"
        
        with pytest.raises(ValenceSDKException) as exc_info:
            raise ValenceSDKException(message)
        
        assert str(exc_info.value) == message
    
    def test_upload_error_with_message(self):
        """Test UploadError can be raised with message."""
        message = "Upload failed"
        
        with pytest.raises(UploadError) as exc_info:
            raise UploadError(message)
        
        assert str(exc_info.value) == message
    
    def test_prediction_error_with_message(self):
        """Test PredictionError can be raised with message."""
        message = "Prediction failed"
        
        with pytest.raises(PredictionError) as exc_info:
            raise PredictionError(message)
        
        assert str(exc_info.value) == message


class TestValenceClient:
    
    def test_client_init_with_env_key(self):
        """Test ValenceClient initialization with environment API key."""
        with patch('valenceai.client.API_KEY', 'test_api_key'):
            client = ValenceClient()
            assert client.api_key == 'test_api_key'
            assert client.headers == {"x-api-key": 'test_api_key'}
    
    def test_client_init_with_explicit_key(self):
        """Test ValenceClient initialization with explicit API key."""
        client = ValenceClient(api_key='explicit_key')
        assert client.api_key == 'explicit_key'
        assert client.headers == {"x-api-key": 'explicit_key'}
    
    def test_client_explicit_key_overrides_env(self):
        """Test explicit API key overrides environment variable."""
        with patch('valenceai.config.API_KEY', 'env_key'):
            client = ValenceClient(api_key='explicit_key')
            assert client.api_key == 'explicit_key'
    
    def test_client_init_without_api_key_raises_exception(self):
        """Test ValenceClient initialization without API key raises exception."""
        with patch('valenceai.config.API_KEY', None):
            with pytest.raises(ValenceSDKException, match="API key not provided and not set in environment"):
                ValenceClient()
    
    def test_client_init_with_empty_api_key_raises_exception(self):
        """Test ValenceClient initialization with empty API key raises exception."""
        with patch('valenceai.config.API_KEY', ''):
            with pytest.raises(ValenceSDKException, match="API key not provided and not set in environment"):
                ValenceClient()