import pytest
import os
from unittest.mock import Mock, patch, mock_open
from valenceai import ValenceClient
from valenceai.exceptions import ValenceSDKException, UploadError, PredictionError


class TestIntegrationAPI:
    """Integration tests for the main API classes with mocked external dependencies."""
    
    def test_discrete_api_predict_emotion_success(self):
        """Test discrete API emotion prediction with mocked response."""
        with patch('valenceai.client.requests.post') as mock_post, \
             patch('builtins.open', mock_open(read_data=b'fake_audio_data')):
            
            # Mock successful response
            mock_response = Mock()
            mock_response.json.return_value = {
                "emotions": {"happy": 0.8, "sad": 0.2},
                "dominant_emotion": "happy"
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            # Test with explicit API key
            client = ValenceClient(api_key='test_key')
            result = client.discrete.emotions("test_file.wav", model="7emotions")
            
            # Verify the request was made correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            
            # Check headers and params
            assert call_args[1]['headers'] == {"x-api-key": 'test_key'}
            assert call_args[1]['params'] == {"model": "7emotions"}
            assert 'files' in call_args[1]
            
            # Check response
            assert result == {"emotions": {"happy": 0.8, "sad": 0.2}, "dominant_emotion": "happy"}
    
    def test_discrete_api_default_model(self):
        """Test discrete API with default model parameter."""
        with patch('valenceai.client.requests.post') as mock_post, \
             patch('builtins.open', mock_open(read_data=b'fake_audio_data')):
            
            mock_response = Mock()
            mock_response.json.return_value = {"result": "success"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response
            
            client = ValenceClient(api_key='test_key')
            client.discrete.emotions("test_file.wav")
            
            # Check that default model is used
            call_args = mock_post.call_args
            assert call_args[1]['params'] == {"model": "4emotions"}
    
    def test_async_api_initialization(self):
        """Test async API initialization with custom parameters."""
        client = ValenceClient(api_key='test_key', part_size=1024, show_progress=False, max_threads=5)
        
        assert client.api_key == 'test_key'
        assert client.asynch.part_size == 1024
        assert client.asynch.show_progress == False
        assert client.asynch.max_threads == 5
        assert client.headers == {"x-api-key": 'test_key'}
    
    def test_async_api_upload_part_success(self):
        """Test async API upload_part method."""
        with patch('valenceai.client.requests.put') as mock_put:
            mock_response = Mock()
            mock_response.headers = {"ETag": "test_etag_123"}
            mock_response.raise_for_status.return_value = None
            mock_put.return_value = mock_response
            
            client = ValenceClient(api_key='test_key')
            result = client.asynch._upload_part("https://s3.aws.com/upload", b"test_data", 1)
            
            assert result == {"ETag": "test_etag_123", "PartNumber": 1}
            mock_put.assert_called_once_with(
                "https://s3.aws.com/upload",
                data=b"test_data",
                headers={"Content-Length": "9"}
            )
    
    def test_async_api_upload_part_failure(self):
        """Test async API upload_part failure."""
        with patch('valenceai.client.requests.put') as mock_put:
            mock_put.side_effect = Exception("Upload failed")
            
            client = ValenceClient(api_key='test_key')
            
            with pytest.raises(UploadError):
                client.asynch._upload_part("https://s3.aws.com/upload", b"test_data", 1)
    
    def test_async_api_get_emotions_success(self):
        """Test async API emotions method success."""
        with patch('valenceai.client.requests.get') as mock_get, \
             patch('valenceai.client.time.sleep'):
            
            # Mock successful response on first try
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "emotions": {"happy": 0.7, "sad": 0.3},
                "status": "completed"
            }
            mock_get.return_value = mock_response
            
            client = ValenceClient(api_key='test_key')
            result = client.asynch.emotions("test_request_id")
            
            assert result == {"emotions": {"happy": 0.7, "sad": 0.3}, "status": "completed"}
            
            # Verify correct URL and parameters
            call_args = mock_get.call_args
            assert call_args[1]['headers'] == {"x-api-key": 'test_key'}
            assert call_args[1]['params'] == {"request_id": "test_request_id"}
    
    def test_async_api_get_emotions_retry_exhausted(self):
        """Test async API emotions when retries are exhausted."""
        with patch('valenceai.client.requests.get') as mock_get, \
             patch('valenceai.client.time.sleep'):
            
            # Mock response that never succeeds
            mock_response = Mock()
            mock_response.status_code = 202  # Still processing
            mock_get.return_value = mock_response
            
            client = ValenceClient(api_key='test_key')
            
            with pytest.raises(PredictionError, match="Failed to fetch prediction after retries"):
                client.asynch.emotions("test_request_id", max_attempts=2, interval_seconds=0.1)
            
            assert mock_get.call_count == 2
    
    def test_api_key_validation(self):
        """Test that API key validation works correctly."""
        # Test missing API key
        with pytest.raises(ValenceSDKException, match="API key not provided"):
            ValenceClient()
        
        # Test empty API key
        with pytest.raises(ValenceSDKException, match="API key not provided"):
            ValenceClient(api_key="")
        
        # Test valid API key
        client = ValenceClient(api_key="valid_key")
        
        assert client.api_key == "valid_key"
    
    def test_file_not_found_error(self):
        """Test file not found error in discrete API."""
        client = ValenceClient(api_key='test_key')
        
        with pytest.raises(FileNotFoundError):
            client.discrete.emotions("non_existent_file.wav")
    
    def test_http_error_handling(self):
        """Test HTTP error handling in discrete API."""
        with patch('valenceai.client.requests.post') as mock_post, \
             patch('builtins.open', mock_open(read_data=b'fake_audio_data')):
            
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("HTTP 500 Error")
            mock_post.return_value = mock_response
            
            client = ValenceClient(api_key='test_key')
            
            with pytest.raises(Exception, match="HTTP 500 Error"):
                client.discrete.emotions("test_file.wav")