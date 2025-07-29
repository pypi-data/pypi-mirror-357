"""
Tests for audio player functionality.
"""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from notification_sound_windows.audio_player import (
    AudioPlayer, 
    AFPlayBackend, 
    SimpleAudioBackend,
    PlaybackStatus, 
    PlaybackResult
)
from notification_sound_windows.config import ServerConfig


class TestAFPlayBackend:
    """Test AFPlay backend functionality."""
    
    def test_is_available_macos(self):
        """Test AFPlay availability detection on macOS."""
        backend = AFPlayBackend()
        
        with patch('sys.platform', 'darwin'), \
             patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            assert backend.is_available() is True
            
            mock_run.return_value.returncode = 1
            assert backend.is_available() is False
    
    def test_is_available_non_macos(self):
        """Test AFPlay availability on non-macOS platforms."""
        backend = AFPlayBackend()
        
        with patch('sys.platform', 'linux'):
            assert backend.is_available() is False
    
    @pytest.mark.asyncio
    async def test_play_file_not_found(self):
        """Test playing non-existent file."""
        backend = AFPlayBackend()
        non_existent_path = Path("/non/existent/file.wav")
        
        result = await backend.play(non_existent_path)
        
        assert result.status == PlaybackStatus.FILE_NOT_FOUND
        assert "not found" in result.message.lower()
        assert result.backend_used == "afplay"
    
    @pytest.mark.asyncio
    async def test_play_success(self):
        """Test successful audio playback."""
        backend = AFPlayBackend()
        test_file = Path("test.wav")

        with patch('pathlib.Path.exists', return_value=True), \
             patch('asyncio.create_subprocess_exec') as mock_subprocess:

            # Mock successful process
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            result = await backend.play(test_file)

            assert result.status == PlaybackStatus.SUCCESS
            assert result.backend_used == "afplay"
            assert "successfully" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_play_timeout(self):
        """Test playback timeout."""
        backend = AFPlayBackend()
        test_file = Path("test.wav")

        with patch('pathlib.Path.exists', return_value=True), \
             patch('asyncio.create_subprocess_exec') as mock_subprocess:

            # Mock process that times out
            mock_process = AsyncMock()
            mock_process.communicate.side_effect = asyncio.TimeoutError()
            mock_process.kill = AsyncMock()
            mock_process.wait = AsyncMock()
            mock_subprocess.return_value = mock_process

            result = await backend.play(test_file, timeout=1)

            assert result.status == PlaybackStatus.TIMEOUT
            assert result.backend_used == "afplay"
            mock_process.kill.assert_called_once()


class TestSimpleAudioBackend:
    """Test SimpleAudio backend functionality."""
    
    def test_is_available_with_simpleaudio(self):
        """Test availability when simpleaudio is installed."""
        backend = SimpleAudioBackend()
        
        with patch('builtins.__import__') as mock_import:
            mock_import.return_value = Mock()
            assert backend.is_available() is True
    
    def test_is_available_without_simpleaudio(self):
        """Test availability when simpleaudio is not installed."""
        backend = SimpleAudioBackend()
        
        with patch('builtins.__import__', side_effect=ImportError()):
            assert backend.is_available() is False
    
    @pytest.mark.asyncio
    async def test_play_file_not_found(self):
        """Test playing non-existent file."""
        backend = SimpleAudioBackend()
        non_existent_path = Path("/non/existent/file.wav")
        
        result = await backend.play(non_existent_path)
        
        assert result.status == PlaybackStatus.FILE_NOT_FOUND
        assert "not found" in result.message.lower()
        assert result.backend_used == "simpleaudio"


class TestAudioPlayer:
    """Test AudioPlayer functionality."""
    
    def test_init_with_backends(self):
        """Test AudioPlayer initialization with available backends."""
        config = ServerConfig()
        
        with patch.object(AFPlayBackend, 'is_available', return_value=True), \
             patch.object(SimpleAudioBackend, 'is_available', return_value=True):
            
            player = AudioPlayer(config)
            
            assert len(player.backends) == 2
            assert any(b.name == "afplay" for b in player.backends)
            assert any(b.name == "simpleaudio" for b in player.backends)
    
    def test_init_no_backends(self):
        """Test AudioPlayer initialization with no available backends."""
        config = ServerConfig()
        
        with patch.object(AFPlayBackend, 'is_available', return_value=False), \
             patch.object(SimpleAudioBackend, 'is_available', return_value=False):
            
            player = AudioPlayer(config)
            
            assert len(player.backends) == 0
    
    def test_get_default_sound_path(self):
        """Test default sound path detection."""
        config = ServerConfig()
        player = AudioPlayer(config)
        
        # The path should end with the expected structure
        assert str(player._default_sound_path).endswith("assets/notification.wav")
    
    @pytest.mark.asyncio
    async def test_play_notification_default(self):
        """Test playing default notification sound."""
        config = ServerConfig()
        
        with patch.object(AFPlayBackend, 'is_available', return_value=True):
            player = AudioPlayer(config)
            
            # Mock the backend play method
            mock_result = PlaybackResult(
                status=PlaybackStatus.SUCCESS,
                message="Test success",
                backend_used="afplay"
            )
            
            with patch.object(player.backends[0], 'play', return_value=mock_result):
                result = await player.play_notification()
                
                assert result.status == PlaybackStatus.SUCCESS
                assert result.backend_used == "afplay"
    
    @pytest.mark.asyncio
    async def test_play_notification_with_fallback(self):
        """Test playing notification with fallback to default sound."""
        config = ServerConfig(enable_fallback=True)
        
        with patch.object(AFPlayBackend, 'is_available', return_value=True):
            player = AudioPlayer(config)
            
            # Mock custom file failure and default file success
            failed_result = PlaybackResult(
                status=PlaybackStatus.FAILED,
                message="Custom file failed",
                backend_used="afplay"
            )
            
            success_result = PlaybackResult(
                status=PlaybackStatus.SUCCESS,
                message="Default file played",
                backend_used="afplay"
            )
            
            with patch.object(player.backends[0], 'play', side_effect=[failed_result, success_result]):
                result = await player.play_notification("/custom/path.wav")
                
                assert result.status == PlaybackStatus.FALLBACK_USED
                assert result.fallback_used is True
                assert "Custom audio failed" in result.message
    
    @pytest.mark.asyncio
    async def test_play_notification_no_backends(self):
        """Test playing notification with no available backends."""
        config = ServerConfig()
        
        with patch.object(AFPlayBackend, 'is_available', return_value=False), \
             patch.object(SimpleAudioBackend, 'is_available', return_value=False):
            
            player = AudioPlayer(config)
            result = await player.play_notification()
            
            assert result.status == PlaybackStatus.FAILED
            assert "No audio backends available" in result.message
    
    @pytest.mark.asyncio
    async def test_play_with_multiple_backends_fallback(self):
        """Test trying multiple backends when first fails."""
        config = ServerConfig()
        
        with patch.object(AFPlayBackend, 'is_available', return_value=True), \
             patch.object(SimpleAudioBackend, 'is_available', return_value=True):
            
            player = AudioPlayer(config)
            
            # First backend fails, second succeeds
            failed_result = PlaybackResult(
                status=PlaybackStatus.FAILED,
                message="First backend failed",
                backend_used="afplay"
            )
            
            success_result = PlaybackResult(
                status=PlaybackStatus.SUCCESS,
                message="Second backend succeeded",
                backend_used="simpleaudio"
            )
            
            with patch.object(player.backends[0], 'play', return_value=failed_result), \
                 patch.object(player.backends[1], 'play', return_value=success_result):
                
                result = await player._play_with_backends(Path("test.wav"))
                
                assert result.status == PlaybackStatus.SUCCESS
                assert result.backend_used == "simpleaudio"
