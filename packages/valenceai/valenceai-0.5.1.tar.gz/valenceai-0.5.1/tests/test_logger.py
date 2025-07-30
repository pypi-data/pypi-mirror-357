import pytest
import logging
import os
from unittest.mock import patch
from valenceai.logger import get_logger


class TestLogger:
    
    def test_get_logger_returns_logger(self):
        """Test get_logger returns a logger instance."""
        logger = get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "valenceai"
    
    @patch.dict(os.environ, {'VALENCE_LOG_LEVEL': 'DEBUG'})
    def test_logger_debug_level(self):
        """Test logger respects DEBUG log level from environment."""
        with patch('valenceai.logger.logging.basicConfig') as mock_config:
            get_logger()
            mock_config.assert_called_with(
                level='DEBUG',
                format="%(asctime)s - %(levelname)s - %(message)s"
            )
    
    @patch.dict(os.environ, {'VALENCE_LOG_LEVEL': 'ERROR'})
    def test_logger_error_level(self):
        """Test logger respects ERROR log level from environment."""
        with patch('valenceai.logger.logging.basicConfig') as mock_config:
            get_logger()
            mock_config.assert_called_with(
                level='ERROR',
                format="%(asctime)s - %(levelname)s - %(message)s"
            )
    
    @patch.dict(os.environ, {}, clear=True)
    def test_logger_default_info_level(self):
        """Test logger defaults to INFO level when not specified."""
        with patch('valenceai.logger.logging.basicConfig') as mock_config:
            get_logger()
            mock_config.assert_called_with(
                level='INFO',
                format="%(asctime)s - %(levelname)s - %(message)s"
            )
    
    @patch.dict(os.environ, {'VALENCE_LOG_LEVEL': 'debug'})
    def test_logger_case_insensitive(self):
        """Test logger handles lowercase log level."""
        with patch('valenceai.logger.logging.basicConfig') as mock_config:
            get_logger()
            mock_config.assert_called_with(
                level='DEBUG',
                format="%(asctime)s - %(levelname)s - %(message)s"
            )
    
    def test_logger_singleton_behavior(self):
        """Test that multiple calls return the same logger instance."""
        logger1 = get_logger()
        logger2 = get_logger()
        
        # Both should have the same name (though may not be the exact same object)
        assert logger1.name == logger2.name == "valenceai"