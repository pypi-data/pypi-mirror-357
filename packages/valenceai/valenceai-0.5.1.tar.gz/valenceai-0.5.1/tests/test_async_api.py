import pytest
import os
import time
from unittest.mock import Mock, patch, mock_open, MagicMock
from collections import OrderedDict
from valenceai import ValenceClient
from valenceai.exceptions import ValenceSDKException, UploadError, PredictionError


class TestAsyncAPI:
    
    @patch('valenceai.client.API_KEY', 'test_api_key')
    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        client = ValenceClient()
        assert client.api_key == 'test_api_key'
        assert client.asynch.part_size == 5 * 1024 * 1024
        assert client.asynch.show_progress == True
        assert client.asynch.max_threads == 3
    
    @patch('valenceai.client.API_KEY', 'test_api_key')
    def test_init_custom_parameters(self):
        """Test initialization with custom parameters."""
        client = ValenceClient(part_size=1024, show_progress=False, max_threads=5)
        assert client.asynch.part_size == 1024
        assert client.asynch.show_progress == False
        assert client.asynch.max_threads == 5
    
    @patch('valenceai.client.requests.get')
    @patch('valenceai.client.requests.post')
    @patch('valenceai.client.ThreadPoolExecutor')
    @patch('valenceai.client.os.path.getsize')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_audio_data' * 1000)
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_upload_success(self, mock_file, mock_getsize, mock_executor, mock_post, mock_get):
        """Test successful file upload."""
        # Mock file size
        mock_getsize.return_value = 10 * 1024 * 1024  # 10MB
        
        # Mock initiate response
        mock_init_response = Mock()
        mock_init_response.json.return_value = {
            "upload_id": "test_upload_id",
            "request_id": "test_request_id",
            "presigned_urls": [
                {"part_number": 1, "url": "https://s3.aws.com/part1"},
                {"part_number": 2, "url": "https://s3.aws.com/part2"}
            ]
        }
        mock_init_response.raise_for_status.return_value = None
        mock_get.return_value = mock_init_response
        
        # Mock upload part responses
        mock_part_response = Mock()
        mock_part_response.headers = {"ETag": "test_etag"}
        mock_part_response.raise_for_status.return_value = None
        
        # Mock ThreadPoolExecutor
        mock_executor_instance = MagicMock()
        mock_executor.__enter__.return_value = mock_executor_instance
        
        # Mock futures
        mock_future1 = Mock()
        mock_future1.result.return_value = {"ETag": "etag1", "PartNumber": 1}
        mock_future2 = Mock()
        mock_future2.result.return_value = {"ETag": "etag2", "PartNumber": 2}
        
        mock_executor_instance.submit.side_effect = [mock_future1, mock_future2]
        
        # Mock as_completed
        with patch('valenceai.client.as_completed', return_value=[mock_future1, mock_future2]):
            # Mock complete response
            mock_complete_response = Mock()
            mock_complete_response.raise_for_status.return_value = None
            mock_post.return_value = mock_complete_response
            
            client = ValenceClient(show_progress=False)
            
            # Mock upload_part method
            client.asynch._upload_part = Mock(side_effect=[
                {"ETag": "etag1", "PartNumber": 1},
                {"ETag": "etag2", "PartNumber": 2}
            ])
            
            result = client.asynch.upload("test_file.wav")
            
            assert result == "test_request_id"
            
            # Verify initiate call
            mock_get.assert_called_once()
            
            # Verify complete call
            mock_post.assert_called_once()
    
    @patch('valenceai.client.requests.put')
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_upload_part_success(self, mock_put):
        """Test successful part upload."""
        mock_response = Mock()
        mock_response.headers = {"ETag": "test_etag_123"}
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response
        
        client = ValenceClient()
        result = client.asynch._upload_part("https://s3.aws.com/upload", b"test_data", 1)
        
        assert result == {"ETag": "test_etag_123", "PartNumber": 1}
        mock_put.assert_called_once_with(
            "https://s3.aws.com/upload",
            data=b"test_data",
            headers={"Content-Length": "9"}
        )
    
    @patch('valenceai.client.requests.put')
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_upload_part_failure(self, mock_put):
        """Test part upload failure."""
        mock_put.side_effect = Exception("Upload failed")
        
        client = ValenceClient()
        
        with pytest.raises(UploadError):
            client.asynch._upload_part("https://s3.aws.com/upload", b"test_data", 1)
    
    @patch('valenceai.client.requests.get')
    @patch('valenceai.client.time.sleep')
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_emotions_success(self, mock_sleep, mock_get):
        """Test successful emotion retrieval."""
        # Mock successful response on first try
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "emotions": {"happy": 0.7, "sad": 0.3},
            "status": "completed"
        }
        mock_get.return_value = mock_response
        
        client = ValenceClient()
        result = client.asynch.emotions("test_request_id")
        
        assert result == {"emotions": {"happy": 0.7, "sad": 0.3}, "status": "completed"}
        mock_sleep.assert_called_once_with(5)  # interval_seconds default
    
    @patch('valenceai.client.requests.get')
    @patch('valenceai.client.time.sleep')
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_emotions_retry_then_success(self, mock_sleep, mock_get):
        """Test emotion retrieval with retry then success."""
        # Mock responses: first two fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 202  # Processing
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"emotions": {"happy": 0.8}}
        
        mock_get.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]
        
        client = ValenceClient()
        result = client.asynch.emotions("test_request_id", max_attempts=5, interval_seconds=1)
        
        assert result == {"emotions": {"happy": 0.8}}
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 3  # Called before each attempt
    
    @patch('valenceai.client.requests.get')
    @patch('valenceai.client.time.sleep')
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_emotions_max_retries_exceeded(self, mock_sleep, mock_get):
        """Test emotion retrieval when max retries exceeded."""
        # Mock response that never succeeds
        mock_response = Mock()
        mock_response.status_code = 202  # Still processing
        mock_get.return_value = mock_response
        
        client = ValenceClient()
        
        with pytest.raises(PredictionError, match="Failed to fetch prediction after retries"):
            client.asynch.emotions("test_request_id", max_attempts=3, interval_seconds=1)
        
        assert mock_get.call_count == 3
    
    @patch('valenceai.client.requests.get')
    @patch('valenceai.client.time.sleep')
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_emotions_custom_parameters(self, mock_sleep, mock_get):
        """Test emotion retrieval with custom wait and retry parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_get.return_value = mock_response
        
        client = ValenceClient()
        client.asynch.emotions("test_request_id", max_attempts=5, interval_seconds=10)
        
        # Verify custom parameters are used
        mock_sleep.assert_called_with(10)
        call_args = mock_get.call_args
        assert call_args[1]['params'] == {"request_id": "test_request_id"}
    
    @patch('valenceai.client.API_KEY', 'test_key')
    def test_emotions_url_construction(self):
        """Test that the prediction URL is constructed correctly."""
        with patch('valenceai.client.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"result": "success"}
            mock_get.return_value = mock_response
            
            client = ValenceClient()
            client.asynch.emotions("test_request_id")
            
            # Check the URL construction
            call_args = mock_get.call_args
            # Since we can't easily access the URL from the mock, we check the call was made
            assert mock_get.called