"""
Tests for configuration management.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from notification_sound_windows.config import ServerConfig, ConfigurationError


class TestServerConfig:
    """Test ServerConfig functionality."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ServerConfig()
        
        assert config.custom_sound_path is None
        assert config.volume_level == 0.8
        assert config.enable_fallback is True
        assert config.max_file_size_mb == 10
        assert config.playback_timeout_seconds == 30
        assert config.audio_backend == "auto"
        assert config.enable_audio_cache is True
        assert config.cache_size_limit == 5
        assert config.restrict_to_user_home is True
        assert '.wav' in config.allowed_audio_extensions
        assert '.mp3' in config.allowed_audio_extensions
    
    def test_from_environment_defaults(self):
        """Test loading from environment with no variables set."""
        with patch.dict(os.environ, {}, clear=True):
            config = ServerConfig.from_environment()
            
            assert config.custom_sound_path is None
            assert config.volume_level == 0.8
            assert config.enable_fallback is True
    
    def test_from_environment_custom_values(self):
        """Test loading custom values from environment."""
        env_vars = {
            'VOLUME_LEVEL': '0.5',
            'ENABLE_FALLBACK': 'false',
            'MAX_FILE_SIZE_MB': '20',
            'PLAYBACK_TIMEOUT_SECONDS': '60',
            'AUDIO_BACKEND': 'simpleaudio',
            'ENABLE_AUDIO_CACHE': 'false',
            'CACHE_SIZE_LIMIT': '10',
            'RESTRICT_TO_USER_HOME': 'false',
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = ServerConfig.from_environment()
            
            assert config.volume_level == 0.5
            assert config.enable_fallback is False
            assert config.max_file_size_mb == 20
            assert config.playback_timeout_seconds == 60
            assert config.audio_backend == 'simpleaudio'
            assert config.enable_audio_cache is False
            assert config.cache_size_limit == 10
            assert config.restrict_to_user_home is False
    
    def test_parse_bool_values(self):
        """Test boolean parsing from environment variables."""
        # Test true values
        for true_val in ['true', '1', 'yes', 'on', 'TRUE', 'Yes', 'ON']:
            assert ServerConfig._parse_bool('TEST', None) is None  # Default when not set
            with patch.dict(os.environ, {'TEST_VAR': true_val}):
                assert ServerConfig._parse_bool('TEST_VAR', False) is True
        
        # Test false values
        for false_val in ['false', '0', 'no', 'off', 'FALSE', 'No', 'OFF']:
            with patch.dict(os.environ, {'TEST_VAR': false_val}):
                assert ServerConfig._parse_bool('TEST_VAR', True) is False
    
    def test_parse_bool_invalid(self):
        """Test invalid boolean values raise errors."""
        with patch.dict(os.environ, {'TEST_VAR': 'invalid'}):
            with pytest.raises(ConfigurationError, match="must be a boolean value"):
                ServerConfig._parse_bool('TEST_VAR', False)
    
    def test_parse_float_invalid(self):
        """Test invalid float values raise errors."""
        with patch.dict(os.environ, {'TEST_VAR': 'not_a_float'}):
            with pytest.raises(ConfigurationError, match="must be a valid float"):
                ServerConfig._parse_float('TEST_VAR', 0.5)
    
    def test_parse_int_invalid(self):
        """Test invalid integer values raise errors."""
        with patch.dict(os.environ, {'TEST_VAR': 'not_an_int'}):
            with pytest.raises(ConfigurationError, match="must be a valid integer"):
                ServerConfig._parse_int('TEST_VAR', 10)
    
    def test_parse_extensions(self):
        """Test parsing file extensions."""
        with patch.dict(os.environ, {'TEST_VAR': 'wav,mp3,.flac,ogg'}):
            extensions = ServerConfig._parse_extensions('TEST_VAR')
            expected = {'.wav', '.mp3', '.flac', '.ogg'}
            assert extensions == expected
    
    def test_validate_volume_level(self):
        """Test volume level validation."""
        # Valid volume levels
        for volume in [0.0, 0.5, 1.0]:
            config = ServerConfig(volume_level=volume)
            config._validate_volume_level()  # Should not raise
        
        # Invalid volume levels
        for volume in [-0.1, 1.1, 2.0]:
            config = ServerConfig(volume_level=volume)
            with pytest.raises(ConfigurationError, match="VOLUME_LEVEL must be between 0.0 and 1.0"):
                config._validate_volume_level()
    
    def test_validate_numeric_ranges(self):
        """Test numeric range validation."""
        # Test max_file_size_mb
        config = ServerConfig(max_file_size_mb=0)
        with pytest.raises(ConfigurationError, match="MAX_FILE_SIZE_MB must be between 1 and 100"):
            config._validate_numeric_ranges()
        
        config = ServerConfig(max_file_size_mb=101)
        with pytest.raises(ConfigurationError, match="MAX_FILE_SIZE_MB must be between 1 and 100"):
            config._validate_numeric_ranges()
        
        # Test playback_timeout_seconds
        config = ServerConfig(playback_timeout_seconds=0)
        with pytest.raises(ConfigurationError, match="PLAYBACK_TIMEOUT_SECONDS must be between 1 and 300"):
            config._validate_numeric_ranges()
        
        config = ServerConfig(playback_timeout_seconds=301)
        with pytest.raises(ConfigurationError, match="PLAYBACK_TIMEOUT_SECONDS must be between 1 and 300"):
            config._validate_numeric_ranges()
    
    def test_validate_audio_backend(self):
        """Test audio backend validation."""
        # Valid backends
        for backend in ['auto', 'simpleaudio', 'pydub', 'system']:
            config = ServerConfig(audio_backend=backend)
            config._validate_audio_backend()  # Should not raise
        
        # Invalid backend
        config = ServerConfig(audio_backend='invalid')
        with pytest.raises(ConfigurationError, match="AUDIO_BACKEND must be one of"):
            config._validate_audio_backend()
    
    def test_validate_security_settings(self):
        """Test security settings validation."""
        # Invalid extension (no dot)
        config = ServerConfig(allowed_audio_extensions={'wav'})
        with pytest.raises(ConfigurationError, match="Audio extensions must start with"):
            config._validate_security_settings()
        
        # Invalid extension (too short)
        config = ServerConfig(allowed_audio_extensions={'.'})
        with pytest.raises(ConfigurationError, match="Audio extensions must have at least one character"):
            config._validate_security_settings()
    
    def test_full_validation(self):
        """Test complete configuration validation."""
        config = ServerConfig.from_environment()
        config.validate()  # Should not raise with default values
