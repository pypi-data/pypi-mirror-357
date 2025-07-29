"""
Audio playback functionality for the MCP Play Sound Server.

This module provides audio playback capabilities with multiple backend support,
fallback mechanisms, and comprehensive error handling.
"""

import logging
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Union
import asyncio
import concurrent.futures

logger = logging.getLogger(__name__)


class PlaybackStatus(Enum):
    """Status of audio playback operation."""
    SUCCESS = "success"
    FAILED = "failed"
    FALLBACK_USED = "fallback_used"
    TIMEOUT = "timeout"
    FILE_NOT_FOUND = "file_not_found"
    UNSUPPORTED_FORMAT = "unsupported_format"


@dataclass
class PlaybackResult:
    """Result of an audio playback operation."""
    status: PlaybackStatus
    message: str
    duration_ms: Optional[int] = None
    backend_used: Optional[str] = None
    fallback_used: bool = False


class AudioBackend:
    """Base class for audio backends."""
    
    def __init__(self, name: str):
        self.name = name
    
    async def play(self, file_path: Path, volume: float = 1.0, timeout: int = 30) -> PlaybackResult:
        """Play audio file asynchronously."""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if this backend is available on the current system."""
        raise NotImplementedError


class AFPlayBackend(AudioBackend):
    """macOS afplay backend for audio playback."""

    def __init__(self, audio_device: Optional[str] = None):
        super().__init__("afplay")
        self.audio_device = audio_device
    
    def is_available(self) -> bool:
        """Check if afplay is available (macOS only)."""
        if sys.platform != "darwin":
            return False
        
        try:
            result = subprocess.run(
                ["which", "afplay"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    async def play(self, file_path: Path, volume: float = 1.0, timeout: int = 30) -> PlaybackResult:
        """Play audio using afplay with optional device switching."""
        if not file_path.exists():
            return PlaybackResult(
                status=PlaybackStatus.FILE_NOT_FOUND,
                message=f"Audio file not found: {file_path}",
                backend_used=self.name
            )

        try:
            # Handle device switching if specified
            original_device = None
            device_switched = False

            if self.audio_device and self.audio_device.strip():
                if self.audio_device.lower() in ["default", "system default", "default system output device"]:
                    # Use system default - no switching needed
                    logger.info("Using system default audio device (explicitly configured)")
                else:
                    # Try to switch to specific device
                    original_device = await self._get_current_audio_device()
                    logger.info(f"Attempting to switch from '{original_device}' to '{self.audio_device}'")
                    switch_result = await self._switch_audio_device(self.audio_device)
                    if switch_result:
                        device_switched = True
                        logger.info(f"Successfully switched to '{self.audio_device}'")
                    else:
                        logger.warning(f"Could not switch to '{self.audio_device}', using current device '{original_device}'")
            else:
                # No audio device configured - use current default
                logger.info("No AUDIO_DEVICE configured, using current system default")

            # Build afplay command with volume control
            cmd = ["afplay"]
            if volume != 1.0:
                cmd.extend(["-v", str(volume)])
            cmd.append(str(file_path))

            logger.debug(f"Executing afplay command: {' '.join(cmd)}")

            # Run afplay asynchronously with timeout
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return PlaybackResult(
                    status=PlaybackStatus.TIMEOUT,
                    message=f"Audio playback timed out after {timeout} seconds",
                    backend_used=self.name
                )

            # Restore original audio device if we switched
            if device_switched and original_device:
                await self._switch_audio_device(original_device)

            if process.returncode == 0:
                if self.audio_device and self.audio_device.strip():
                    if self.audio_device.lower() in ["default", "system default", "default system output device"]:
                        device_msg = " (via system default device)"
                    else:
                        device_msg = f" (via {self.audio_device})"
                else:
                    device_msg = " (via current system default)"

                return PlaybackResult(
                    status=PlaybackStatus.SUCCESS,
                    message=f"Audio played successfully{device_msg}",
                    backend_used=self.name
                )
            else:
                error_msg = stderr.decode() if stderr else "Unknown afplay error"
                return PlaybackResult(
                    status=PlaybackStatus.FAILED,
                    message=f"afplay failed: {error_msg}",
                    backend_used=self.name
                )

        except Exception as e:
            logger.error(f"Error playing audio with afplay: {e}")
            # Restore original audio device if we switched and there was an error
            if device_switched and original_device:
                try:
                    await self._switch_audio_device(original_device)
                except:
                    pass  # Don't fail if we can't restore
            return PlaybackResult(
                status=PlaybackStatus.FAILED,
                message=f"afplay error: {str(e)}",
                backend_used=self.name
            )

    async def _get_current_audio_device(self) -> Optional[str]:
        """Get the current audio output device using SwitchAudioSource."""
        try:
            # Use SwitchAudioSource to get current device (same as working setup script)
            process = await asyncio.create_subprocess_exec(
                "SwitchAudioSource", "-c",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                current_device = stdout.decode().strip()
                logger.debug(f"Current audio device: {current_device}")
                return current_device
        except Exception as e:
            logger.debug(f"Could not get current audio device: {e}")
        return None

    async def _switch_audio_device(self, device_name: str) -> bool:
        """Switch to the specified audio output device using SwitchAudioSource."""
        try:
            # Use SwitchAudioSource (same as working setup script)
            process = await asyncio.create_subprocess_exec(
                "SwitchAudioSource", "-s", device_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                logger.info(f"Successfully switched audio device to: {device_name} (via SwitchAudioSource)")
                return True
            else:
                error_msg = stderr.decode().strip() if stderr else "Unknown error"
                logger.warning(f"Failed to switch audio device to {device_name}: {error_msg}")
                return False

        except FileNotFoundError:
            logger.error("SwitchAudioSource not found. Please install with: brew install switchaudio-osx")
            return False
        except Exception as e:
            logger.error(f"Error switching audio device to {device_name}: {e}")
            return False

    @staticmethod
    async def get_available_audio_devices() -> list:
        """Get list of available audio output devices on macOS."""
        devices = []
        try:
            # Use system_profiler to get audio devices
            process = await asyncio.create_subprocess_exec(
                "system_profiler", "SPAudioDataType",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                output = stdout.decode()
                lines = output.split('\n')

                current_device = None
                in_devices_section = False

                for line in lines:
                    stripped = line.strip()

                    # Check if we're in the Devices section
                    if stripped == "Devices:":
                        in_devices_section = True
                        continue

                    if not in_devices_section:
                        continue

                    # Device names end with ':' and are not indented much
                    if (stripped.endswith(':') and
                        not stripped.startswith(('Input', 'Output', 'Current', 'Manufacturer', 'Transport', 'Default')) and
                        len(line) - len(line.lstrip()) <= 8):  # Not too deeply indented

                        # Save previous device if it was an output device
                        if current_device and current_device.get("is_output"):
                            devices.append(current_device)

                        # Start new device
                        device_name = stripped.rstrip(':').strip()
                        if device_name and device_name != "Devices":
                            current_device = {"name": device_name, "is_output": False, "is_default": False}

                    elif current_device:
                        # Check for output device indicators
                        if "Output Channels:" in stripped:
                            current_device["is_output"] = True
                        elif "Default Output Device: Yes" in stripped:
                            current_device["is_default"] = True
                            current_device["is_output"] = True
                        elif "Default System Output Device: Yes" in stripped:
                            current_device["is_default"] = True
                            current_device["is_output"] = True

                # Add the last device if it's an output device
                if current_device and current_device.get("is_output"):
                    devices.append(current_device)

        except Exception as e:
            logger.error(f"Error getting audio devices: {e}")

        return devices


class SimpleAudioBackend(AudioBackend):
    """SimpleAudio backend for cross-platform audio playback."""
    
    def __init__(self):
        super().__init__("simpleaudio")
        self._simpleaudio = None
    
    def is_available(self) -> bool:
        """Check if simpleaudio is available."""
        try:
            import simpleaudio
            self._simpleaudio = simpleaudio
            return True
        except ImportError:
            return False
    
    async def play(self, file_path: Path, volume: float = 1.0, timeout: int = 30) -> PlaybackResult:
        """Play audio using simpleaudio."""
        if not self._simpleaudio:
            if not self.is_available():
                return PlaybackResult(
                    status=PlaybackStatus.FAILED,
                    message="simpleaudio not available",
                    backend_used=self.name
                )
        
        if not file_path.exists():
            return PlaybackResult(
                status=PlaybackStatus.FILE_NOT_FOUND,
                message=f"Audio file not found: {file_path}",
                backend_used=self.name
            )
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await asyncio.wait_for(
                    loop.run_in_executor(executor, self._play_sync, file_path, volume),
                    timeout=timeout
                )
            return result
            
        except asyncio.TimeoutError:
            return PlaybackResult(
                status=PlaybackStatus.TIMEOUT,
                message=f"Audio playback timed out after {timeout} seconds",
                backend_used=self.name
            )
        except Exception as e:
            logger.error(f"Error playing audio with simpleaudio: {e}")
            return PlaybackResult(
                status=PlaybackStatus.FAILED,
                message=f"simpleaudio error: {str(e)}",
                backend_used=self.name
            )
    
    def _play_sync(self, file_path: Path, volume: float) -> PlaybackResult:
        """Synchronous audio playback for thread execution."""
        try:
            # Load and play WAV file
            wave_obj = self._simpleaudio.WaveObject.from_wave_file(str(file_path))
            play_obj = wave_obj.play()
            play_obj.wait_done()
            
            return PlaybackResult(
                status=PlaybackStatus.SUCCESS,
                message="Audio played successfully",
                backend_used=self.name
            )
        except Exception as e:
            return PlaybackResult(
                status=PlaybackStatus.FAILED,
                message=f"simpleaudio playback error: {str(e)}",
                backend_used=self.name
            )


class WinSoundBackend(AudioBackend):
    """Windows winsound backend for audio playback."""
    
    def __init__(self):
        super().__init__("winsound")
    
    def is_available(self) -> bool:
        """Check if winsound is available (Windows only)."""
        if sys.platform != "win32":
            return False
        
        try:
            import winsound
            return True
        except ImportError:
            return False
    
    async def play(self, file_path: Path, volume: float = 1.0, timeout: int = 30) -> PlaybackResult:
        """Play audio using Windows winsound."""
        if not file_path.exists():
            return PlaybackResult(
                status=PlaybackStatus.FILE_NOT_FOUND,
                message=f"Audio file not found: {file_path}",
                backend_used=self.name
            )

        try:
            import winsound
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await asyncio.wait_for(
                    loop.run_in_executor(executor, self._play_sync, file_path, winsound),
                    timeout=timeout
                )
            return result
            
        except asyncio.TimeoutError:
            return PlaybackResult(
                status=PlaybackStatus.TIMEOUT,
                message=f"Audio playback timed out after {timeout} seconds",
                backend_used=self.name
            )
        except Exception as e:
            logger.error(f"Error playing audio with winsound: {e}")
            return PlaybackResult(
                status=PlaybackStatus.FAILED,
                message=f"winsound error: {str(e)}",
                backend_used=self.name
            )
    
    def _play_sync(self, file_path: Path, winsound) -> PlaybackResult:
        """Synchronous audio playback for thread execution."""
        try:
            # Use winsound to play the WAV file
            # winsound.SND_FILENAME flag indicates file path is provided
            # winsound.SND_ASYNC would be non-blocking, but we want blocking behavior
            winsound.PlaySound(str(file_path), winsound.SND_FILENAME)
            
            return PlaybackResult(
                status=PlaybackStatus.SUCCESS,
                message="Audio played successfully",
                backend_used=self.name
            )
        except Exception as e:
            return PlaybackResult(
                status=PlaybackStatus.FAILED,
                message=f"winsound playback error: {str(e)}",
                backend_used=self.name
            )


class AudioPlayer:
    """Main audio player with multiple backend support and fallback."""
    
    def __init__(self, config):
        """Initialize audio player with configuration."""
        self.config = config
        self.backends = []
        self._setup_backends()
        self._default_sound_path = self._get_default_sound_path()        
        logger.info(f"AudioPlayer initialized with {len(self.backends)} available backends")
    
    def _setup_backends(self) -> None:
        """Set up available audio backends based on configuration and platform."""
        # Always try AFPlay first on macOS (most reliable)
        afplay = AFPlayBackend(audio_device=getattr(self.config, 'audio_device', None))
        if afplay.is_available():
            self.backends.append(afplay)
            device_info = f" (device: {self.config.audio_device})" if getattr(self.config, 'audio_device', None) else ""
            logger.debug(f"AFPlay backend available{device_info}")

        # Try WinSound first on Windows (built-in, most reliable)
        winsound = WinSoundBackend()
        if winsound.is_available():
            self.backends.append(winsound)
            logger.debug("WinSound backend available")

        # Add SimpleAudio as cross-platform fallback
        simpleaudio = SimpleAudioBackend()
        if simpleaudio.is_available():
            self.backends.append(simpleaudio)
            logger.debug("SimpleAudio backend available")

        if not self.backends:
            logger.warning("No audio backends available!")
    
    def _get_default_sound_path(self) -> Path:
        """Get path to default notification sound."""
        # Default sound should be bundled with the package
        package_dir = Path(__file__).parent
        default_sound = package_dir / "assets" / "notification.wav"
        
        if not default_sound.exists():
            logger.warning(f"Default sound file not found: {default_sound}")
        
        return default_sound
    
    async def play_notification(self, custom_path: Optional[str] = None) -> PlaybackResult:
        """
        Play notification sound with fallback support.
        
        Args:
            custom_path: Optional path to custom audio file
            
        Returns:
            PlaybackResult with status and details
        """
        # Determine which file to play
        if custom_path and self.config.custom_sound_path:
            audio_path = Path(self.config.custom_sound_path)
            use_custom = True
        elif custom_path:
            audio_path = Path(custom_path)
            use_custom = True
        else:
            audio_path = self._default_sound_path
            use_custom = False
        
        logger.info(f"Playing audio: {audio_path} (custom={use_custom})")
        
        # Try to play the requested file
        result = await self._play_with_backends(audio_path)
        
        # If custom file failed and fallback is enabled, try default
        if (result.status != PlaybackStatus.SUCCESS and 
            use_custom and 
            self.config.enable_fallback and 
            audio_path != self._default_sound_path):
            
            logger.info("Custom audio failed, trying default fallback")
            fallback_result = await self._play_with_backends(self._default_sound_path)
            
            if fallback_result.status == PlaybackStatus.SUCCESS:
                fallback_result.fallback_used = True
                fallback_result.status = PlaybackStatus.FALLBACK_USED
                fallback_result.message = f"Custom audio failed, used fallback: {result.message}"
                return fallback_result
        
        return result
    
    async def _play_with_backends(self, file_path: Path) -> PlaybackResult:
        """Try to play audio file with available backends."""
        if not self.backends:
            return PlaybackResult(
                status=PlaybackStatus.FAILED,
                message="No audio backends available"
            )
        
        last_result = None
        for backend in self.backends:
            logger.debug(f"Trying backend: {backend.name}")
            result = await backend.play(
                file_path, 
                volume=self.config.volume_level,
                timeout=self.config.playback_timeout_seconds
            )
            
            if result.status == PlaybackStatus.SUCCESS:
                return result
            
            last_result = result
            logger.debug(f"Backend {backend.name} failed: {result.message}")
        
        # All backends failed
        return last_result or PlaybackResult(
            status=PlaybackStatus.FAILED,
            message="All audio backends failed"
        )
