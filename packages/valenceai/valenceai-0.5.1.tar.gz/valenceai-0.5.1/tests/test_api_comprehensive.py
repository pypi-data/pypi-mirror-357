import pytest
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from valenceai import ValenceClient
from valenceai.exceptions import ValenceSDKException, UploadError, PredictionError


class TestComprehensiveAPI:
    """Comprehensive tests for both API classes."""
    
    def test_discrete_api_full_workflow(self):
        """Test complete discrete audio workflow."""
        with patch('valenceai.client.requests.post') as mock_post:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(b'fake_audio_content')
                temp_file_path = temp_file.name
            
            try:
                # Mock successful API response
                mock_response = Mock()
                mock_response.json.return_value = {
                    "predictions": [
                        {"emotion": "happy", "confidence": 0.85},
                        {"emotion": "excited", "confidence": 0.65}
                    ],
                    "dominant_emotion": "happy",
                    "model_version": "7emotions"
                }
                mock_response.raise_for_status.return_value = None
                mock_post.return_value = mock_response
                
                # Test the API
                client = ValenceClient(api_key='test_api_key')
                result = client.discrete.emotions(temp_file_path, model="7emotions")
                
                # Verify request
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                
                # Verify URL is called (we can't easily check the exact URL from the mock)
                # The URL should be the first positional argument
                
                # Verify headers
                assert call_args[1]['headers']['x-api-key'] == 'test_api_key'
                
                # Verify params
                assert call_args[1]['params']['model'] == '7emotions'
                
                # Verify files parameter exists
                assert 'files' in call_args[1]
                
                # Verify response
                assert result['dominant_emotion'] == 'happy'
                assert len(result['predictions']) == 2
                
            finally:
                # Clean up temp file
                os.unlink(temp_file_path)
    
    def test_async_api_upload_workflow(self):
        """Test AsyncAPI upload workflow with mocked dependencies."""
        with patch('valenceai.long_audio.requests.get') as mock_get, \
             patch('valenceai.long_audio.requests.post') as mock_post, \
             patch('valenceai.long_audio.ThreadPoolExecutor') as mock_executor, \
             patch('valenceai.long_audio.os.path.getsize') as mock_getsize:
            
            # Mock file size
            mock_getsize.return_value = 10 * 1024 * 1024  # 10MB
            
            # Mock initiate upload response
            mock_init_response = Mock()
            mock_init_response.json.return_value = {
                "upload_id": "upload_123",
                "request_id": "request_456",
                "presigned_urls": [
                    {"part_number": 1, "url": "https://s3.aws.com/part1"},
                    {"part_number": 2, "url": "https://s3.aws.com/part2"}
                ]
            }
            mock_init_response.raise_for_status.return_value = None
            mock_get.return_value = mock_init_response
            
            # Mock complete upload response
            mock_complete_response = Mock()
            mock_complete_response.raise_for_status.return_value = None
            mock_post.return_value = mock_complete_response
            
            # Mock ThreadPoolExecutor
            mock_executor_instance = Mock()
            mock_executor.__enter__.return_value = mock_executor_instance
            
            # Create temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(b'fake_large_audio_content' * 1000)
                temp_file_path = temp_file.name
            
            try:
                client = ValenceClient(api_key='test_key', show_progress=False)
                
                # Mock the upload_part method to avoid actual HTTP calls
                client.asynch._upload_part = Mock(side_effect=[
                    {"ETag": "etag1", "PartNumber": 1},
                    {"ETag": "etag2", "PartNumber": 2}
                ])
                
                # Mock as_completed to return our futures
                with patch('valenceai.long_audio.as_completed') as mock_completed:
                    mock_future1 = Mock()
                    mock_future1.result.return_value = {"ETag": "etag1", "PartNumber": 1}
                    mock_future2 = Mock()
                    mock_future2.result.return_value = {"ETag": "etag2", "PartNumber": 2}
                    
                    mock_completed.return_value = [mock_future1, mock_future2]
                    mock_executor_instance.submit.side_effect = [mock_future1, mock_future2]
                    
                    # Test upload
                    request_id = client.asynch.upload(temp_file_path)
                    
                    # Verify result
                    assert request_id == "request_456"
                    
                    # Verify initiate call was made
                    mock_get.assert_called_once()
                    init_call_args = mock_get.call_args
                    assert 'part_count' in init_call_args[1]['params']
                    assert init_call_args[1]['headers']['x-api-key'] == 'test_key'
                    
                    # Verify complete call was made
                    mock_post.assert_called_once()
                    complete_call_args = mock_post.call_args
                    payload = complete_call_args[1]['json']
                    assert payload['request_id'] == 'request_456'
                    assert payload['upload_id'] == 'upload_123'
                    assert len(payload['parts']) == 2
                    
            finally:
                os.unlink(temp_file_path)
    
    def test_async_api_get_emotions_workflow(self):
        """Test AsyncAPI get_emotions workflow."""
        with patch('valenceai.long_audio.requests.get') as mock_get, \
             patch('valenceai.long_audio.time.sleep') as mock_sleep:
            
            # Mock responses: processing, then success
            mock_processing = Mock()
            mock_processing.status_code = 202
            
            mock_success = Mock()
            mock_success.status_code = 200
            mock_success.json.return_value = {
                "status": "completed",
                "results": {
                    "emotions": [
                        {"timestamp": 0.0, "emotion": "happy", "confidence": 0.8},
                        {"timestamp": 5.0, "emotion": "calm", "confidence": 0.7},
                        {"timestamp": 10.0, "emotion": "excited", "confidence": 0.9}
                    ],
                    "summary": {
                        "dominant_emotion": "excited",
                        "average_confidence": 0.8
                    }
                }
            }
            
            # First call returns processing, second returns success
            mock_get.side_effect = [mock_processing, mock_success]
            
            client = ValenceClient(api_key='test_key')
            result = client.asynch.emotions("request_456", max_attempts=5, interval_seconds=1)
            
            # Verify we got the expected result
            assert result['status'] == 'completed'
            assert len(result['results']['emotions']) == 3
            assert result['results']['summary']['dominant_emotion'] == 'excited'
            
            # Verify polling behavior
            assert mock_get.call_count == 2
            assert mock_sleep.call_count == 2  # Called before each attempt
            
            # Verify request parameters
            for call in mock_get.call_args_list:
                assert call[1]['headers']['x-api-key'] == 'test_key'
                assert call[1]['params']['request_id'] == 'request_456'
    
    def test_error_handling_scenarios(self):
        """Test various error scenarios."""
        
        # Test invalid API key
        with pytest.raises(ValenceSDKException):
            ValenceClient(api_key=None)
        
        with pytest.raises(ValenceSDKException):
            ValenceClient(api_key="")
        
        # Test network errors in DiscreteAPI
        with patch('valenceai.short_audio.requests.post') as mock_post:
            mock_post.side_effect = ConnectionError("Network error")
            
            with tempfile.NamedTemporaryFile(suffix='.wav') as temp_file:
                temp_file.write(b'audio')
                temp_file.flush()
                
                client = ValenceClient(api_key='test_key')
                with pytest.raises(ConnectionError):
                    client.discrete.emotions(temp_file.name)
        
        # Test upload error in AsyncAPI
        with patch('valenceai.long_audio.requests.put') as mock_put:
            mock_put.side_effect = Exception("S3 upload failed")
            
            client = ValenceClient(api_key='test_key')
            with pytest.raises(UploadError):
                client.asynch._upload_part("https://s3.aws.com/test", b"data", 1)
        
        # Test prediction timeout in AsyncAPI
        with patch('valenceai.long_audio.requests.get') as mock_get, \
             patch('valenceai.long_audio.time.sleep'):
            
            # Always return processing status
            mock_response = Mock()
            mock_response.status_code = 202
            mock_get.return_value = mock_response
            
            client = ValenceClient(api_key='test_key')
            with pytest.raises(PredictionError, match="Failed to fetch prediction after retries"):
                client.asynch.emotions("request_id", max_attempts=2, interval_seconds=0.1)
    
    def test_configuration_integration(self):
        """Test that configuration values are used correctly."""
        
        # Test URL configuration
        client = ValenceClient(api_key='test_key')
        # The VALENCE_DISCRETE_URL should be accessible via the config
        from valenceai.config import VALENCE_DISCRETE_URL, VALENCE_ASYNCH_URL
        
        # Verify URLs are set
        assert VALENCE_DISCRETE_URL is not None
        assert VALENCE_ASYNCH_URL is not None
        assert 'amazonaws.com' in VALENCE_DISCRETE_URL
        assert 'amazonaws.com' in VALENCE_ASYNCH_URL
    
    def test_logger_integration(self):
        """Test that logger is working correctly."""
        from valenceai.logger import get_logger
        
        logger = get_logger()
        assert logger.name == "valenceai"
        
        # Test that logger methods exist and are callable
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'debug')
    
    def test_package_imports(self):
        """Test that package imports work correctly."""
        # Test that we can import the main classes
        from valenceai import ValenceClient
        
        # Test that classes are properly exported
        assert ValenceClient.__name__ == 'ValenceClient'
        
        # Test client has nested attributes
        client = ValenceClient(api_key='test')
        assert hasattr(client, 'discrete')
        assert hasattr(client, 'asynch')
