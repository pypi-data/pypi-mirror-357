"""
Configuration management for the MCP Play Sound Server.

This module handles loading, validation, and management of server configuration
from environment variables and provides sensible defaults.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set
import logging

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass


@dataclass
class ServerConfig:
    """Configuration for the MCP Play Sound Server."""
    
    # Core configuration
    custom_sound_path: Optional[str] = None
    volume_level: float = 0.8
    enable_fallback: bool = True
    audio_device: Optional[str] = None
    
    # Advanced configuration
    max_file_size_mb: int = 10
    playback_timeout_seconds: int = 30
    audio_backend: str = "auto"
    enable_audio_cache: bool = True
    cache_size_limit: int = 5
    
    # Security configuration
    allowed_audio_extensions: Set[str] = None
    restrict_to_user_home: bool = True
    
    def __post_init__(self):
        """Initialize default values that need computation."""
        if self.allowed_audio_extensions is None:
            self.allowed_audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
    
    @classmethod
    def from_environment(cls) -> 'ServerConfig':
        """Create configuration from environment variables."""
        logger.debug("Loading configuration from environment variables")
        
        # Parse environment variables with defaults
        config = cls(
            custom_sound_path=os.getenv('CUSTOM_SOUND_PATH'),
            volume_level=cls._parse_float('VOLUME_LEVEL', 0.8),
            enable_fallback=cls._parse_bool('ENABLE_FALLBACK', True),
            audio_device=os.getenv('AUDIO_DEVICE'),
            max_file_size_mb=cls._parse_int('MAX_FILE_SIZE_MB', 10),
            playback_timeout_seconds=cls._parse_int('PLAYBACK_TIMEOUT_SECONDS', 30),
            audio_backend=os.getenv('AUDIO_BACKEND', 'auto'),
            enable_audio_cache=cls._parse_bool('ENABLE_AUDIO_CACHE', True),
            cache_size_limit=cls._parse_int('CACHE_SIZE_LIMIT', 5),
            allowed_audio_extensions=cls._parse_extensions('ALLOWED_AUDIO_EXTENSIONS'),
            restrict_to_user_home=cls._parse_bool('RESTRICT_TO_USER_HOME', True),
        )
        
        logger.info(f"Configuration loaded: custom_sound={bool(config.custom_sound_path)}, "
                   f"volume={config.volume_level}, fallback={config.enable_fallback}")
        
        return config
    
    @staticmethod
    def _parse_float(env_var: str, default: float) -> float:
        """Parse float from environment variable."""
        value = os.getenv(env_var)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            raise ConfigurationError(f"{env_var} must be a valid float, got: {value}")
    
    @staticmethod
    def _parse_int(env_var: str, default: int) -> int:
        """Parse integer from environment variable."""
        value = os.getenv(env_var)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise ConfigurationError(f"{env_var} must be a valid integer, got: {value}")
    
    @staticmethod
    def _parse_bool(env_var: str, default: bool) -> bool:
        """Parse boolean from environment variable."""
        value = os.getenv(env_var)
        if value is None:
            return default
        
        value_lower = value.lower()
        if value_lower in ('true', '1', 'yes', 'on'):
            return True
        elif value_lower in ('false', '0', 'no', 'off'):
            return False
        else:
            raise ConfigurationError(f"{env_var} must be a boolean value, got: {value}")
    
    @staticmethod
    def _parse_extensions(env_var: str) -> Optional[Set[str]]:
        """Parse comma-separated file extensions."""
        value = os.getenv(env_var)
        if value is None:
            return None
        
        extensions = set()
        for ext in value.split(','):
            ext = ext.strip()
            if not ext.startswith('.'):
                ext = '.' + ext
            extensions.add(ext.lower())
        
        return extensions
    
    def validate(self) -> None:
        """Validate all configuration options."""
        logger.debug("Validating configuration")
        
        self._validate_volume_level()
        self._validate_file_paths()
        self._validate_numeric_ranges()
        self._validate_audio_backend()
        self._validate_security_settings()
        
        logger.info("Configuration validation completed successfully")
    
    def _validate_volume_level(self) -> None:
        """Validate volume level is in valid range."""
        if not 0.0 <= self.volume_level <= 1.0:
            raise ConfigurationError(
                f"VOLUME_LEVEL must be between 0.0 and 1.0, got: {self.volume_level}"
            )
    
    def _validate_file_paths(self) -> None:
        """Validate file paths and permissions."""
        if self.custom_sound_path:
            path = Path(self.custom_sound_path)
            
            # Check if file exists
            if not path.exists():
                raise ConfigurationError(
                    f"CUSTOM_SOUND_PATH file does not exist: {self.custom_sound_path}"
                )
            
            # Check if file is readable
            if not path.is_file():
                raise ConfigurationError(
                    f"CUSTOM_SOUND_PATH is not a file: {self.custom_sound_path}"
                )
            
            # Check file extension
            if path.suffix.lower() not in self.allowed_audio_extensions:
                raise ConfigurationError(
                    f"Audio file extension '{path.suffix}' not in ALLOWED_AUDIO_EXTENSIONS: "
                    f"{','.join(sorted(self.allowed_audio_extensions))}"
                )
            
            # Check file size
            file_size_mb = path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.max_file_size_mb:
                raise ConfigurationError(
                    f"Custom audio file exceeds MAX_FILE_SIZE_MB limit ({self.max_file_size_mb}MB): "
                    f"{path.name} ({file_size_mb:.1f}MB)"
                )
            
            # Check user home restriction
            if self.restrict_to_user_home:
                home_path = Path.home()
                try:
                    path.resolve().relative_to(home_path.resolve())
                except ValueError:
                    raise ConfigurationError(
                        f"CUSTOM_SOUND_PATH must be within user home directory when "
                        f"RESTRICT_TO_USER_HOME is enabled: {self.custom_sound_path}"
                    )
    
    def _validate_numeric_ranges(self) -> None:
        """Validate numeric configuration ranges."""
        if not 1 <= self.max_file_size_mb <= 100:
            raise ConfigurationError(
                f"MAX_FILE_SIZE_MB must be between 1 and 100, got: {self.max_file_size_mb}"
            )
        
        if not 1 <= self.playback_timeout_seconds <= 300:
            raise ConfigurationError(
                f"PLAYBACK_TIMEOUT_SECONDS must be between 1 and 300, got: {self.playback_timeout_seconds}"
            )
        
        if not 1 <= self.cache_size_limit <= 20:
            raise ConfigurationError(
                f"CACHE_SIZE_LIMIT must be between 1 and 20, got: {self.cache_size_limit}"
            )
    
    def _validate_audio_backend(self) -> None:
        """Validate audio backend option."""
        valid_backends = {'auto', 'simpleaudio', 'pydub', 'system'}
        if self.audio_backend not in valid_backends:
            raise ConfigurationError(
                f"AUDIO_BACKEND must be one of {valid_backends}, got: {self.audio_backend}"
            )
    
    def _validate_security_settings(self) -> None:
        """Validate security-related settings."""
        # Validate allowed extensions
        for ext in self.allowed_audio_extensions:
            if not ext.startswith('.'):
                raise ConfigurationError(
                    f"Audio extensions must start with '.', got: {ext}"
                )
            if len(ext) < 2:
                raise ConfigurationError(
                    f"Audio extensions must have at least one character after '.', got: {ext}"
                )
