"""
MCP Server implementation for audio playback notifications.

This module implements the Model Context Protocol server using FastMCP,
providing the play_notification_sound tool for AI agents.
"""

import logging
from typing import Optional, Dict, Any

from mcp.server.fastmcp import FastMCP

from .config import ServerConfig
from .audio_player import AudioPlayer, PlaybackStatus, AFPlayBackend

logger = logging.getLogger(__name__)


class PlaySoundServer:
    """MCP Server for audio playback notifications."""
    
    def __init__(self, config: ServerConfig):
        """Initialize the MCP server with configuration."""
        self.config = config
        self.audio_player = AudioPlayer(config)
        
        # Initialize FastMCP server
        self.app = FastMCP("play-sound-server")
        self._setup_tools()
        
        logger.info("PlaySoundServer initialized")
    
    def _setup_tools(self) -> None:
        """Set up MCP tools."""
        
        @self.app.tool()
        async def play_notification_sound(
            custom_sound_path: Optional[str] = None,
            message: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Play a notification sound to alert the user.
            
            This tool plays an audio notification to get the user's attention,
            typically used when an AI coding task has been completed.
            
            Args:
                custom_sound_path: Optional path to a custom audio file to play.
                                 If not provided, uses the configured default or built-in sound.
                message: Optional message to include in the response for context.
            
            Returns:
                Dictionary containing playback status, message, and details.
            """
            logger.info(f"play_notification_sound called: custom_path={custom_sound_path}, message={message}")
            
            try:
                # Play the notification sound
                result = await self.audio_player.play_notification(custom_sound_path)
                
                # Prepare response
                response = {
                    "success": result.status in [PlaybackStatus.SUCCESS, PlaybackStatus.FALLBACK_USED],
                    "status": result.status.value,
                    "message": result.message,
                    "backend_used": result.backend_used,
                    "fallback_used": result.fallback_used,
                }
                
                # Add user message if provided
                if message:
                    response["user_message"] = message
                
                # Add duration if available
                if result.duration_ms:
                    response["duration_ms"] = result.duration_ms
                
                # Log the result
                if result.status == PlaybackStatus.SUCCESS:
                    logger.info(f"Notification played successfully using {result.backend_used}")
                elif result.status == PlaybackStatus.FALLBACK_USED:
                    logger.info(f"Notification played using fallback with {result.backend_used}")
                else:
                    logger.warning(f"Notification playback failed: {result.message}")
                
                return response
                
            except Exception as e:
                logger.error(f"Error in play_notification_sound: {e}")
                return {
                    "success": False,
                    "status": "error",
                    "message": f"Unexpected error: {str(e)}",
                    "backend_used": None,
                    "fallback_used": False,
                }
        
        @self.app.tool()
        async def get_audio_status() -> Dict[str, Any]:
            """
            Get the current audio system status and configuration.
            
            Returns information about available audio backends, configuration,
            and system capabilities.
            
            Returns:
                Dictionary containing audio system status and configuration.
            """
            logger.debug("get_audio_status called")
            
            try:
                # Get backend information
                backend_info = []
                for backend in self.audio_player.backends:
                    backend_info.append({
                        "name": backend.name,
                        "available": backend.is_available(),
                    })
                
                # Prepare status response
                status = {
                    "backends_available": len(self.audio_player.backends),
                    "backends": backend_info,
                    "configuration": {
                        "volume_level": self.config.volume_level,
                        "enable_fallback": self.config.enable_fallback,
                        "custom_sound_configured": bool(self.config.custom_sound_path),
                        "audio_backend": self.config.audio_backend,
                        "playback_timeout_seconds": self.config.playback_timeout_seconds,
                    },
                    "default_sound_exists": self.audio_player._default_sound_path.exists(),
                }
                
                # Add custom sound info if configured
                if self.config.custom_sound_path:
                    from pathlib import Path
                    custom_path = Path(self.config.custom_sound_path)
                    status["custom_sound"] = {
                        "path": str(custom_path),
                        "exists": custom_path.exists(),
                        "size_mb": round(custom_path.stat().st_size / (1024 * 1024), 2) if custom_path.exists() else None,
                    }
                
                logger.debug(f"Audio status: {len(backend_info)} backends available")
                return status
                
            except Exception as e:
                logger.error(f"Error in get_audio_status: {e}")
                return {
                    "error": f"Failed to get audio status: {str(e)}",
                    "backends_available": 0,
                    "backends": [],
                }
        
        @self.app.tool()
        async def test_audio_playback(
            use_custom: bool = False
        ) -> Dict[str, Any]:
            """
            Test audio playback functionality.
            
            Performs a test of the audio system to verify it's working correctly.
            Useful for troubleshooting audio issues.
            
            Args:
                use_custom: If True, test with custom sound (if configured).
                          If False, test with default sound.
            
            Returns:
                Dictionary containing test results and diagnostic information.
            """
            logger.info(f"test_audio_playback called: use_custom={use_custom}")
            
            try:
                # Determine which sound to test
                test_path = None
                if use_custom and self.config.custom_sound_path:
                    test_path = self.config.custom_sound_path
                
                # Run the test
                result = await self.audio_player.play_notification(test_path)
                
                # Prepare test results
                test_result = {
                    "test_passed": result.status in [PlaybackStatus.SUCCESS, PlaybackStatus.FALLBACK_USED],
                    "status": result.status.value,
                    "message": result.message,
                    "backend_used": result.backend_used,
                    "fallback_used": result.fallback_used,
                    "test_type": "custom" if use_custom else "default",
                }
                
                logger.info(f"Audio test completed: {result.status.value}")
                return test_result
                
            except Exception as e:
                logger.error(f"Error in test_audio_playback: {e}")
                return {
                    "test_passed": False,
                    "status": "error",
                    "message": f"Test failed with error: {str(e)}",
                    "backend_used": None,
                    "fallback_used": False,
                    "test_type": "custom" if use_custom else "default",
                }

        @self.app.tool()
        async def list_audio_devices() -> Dict[str, Any]:
            """
            List available audio output devices on the system.

            Returns information about all available audio output devices,
            including which one is currently the default.

            Returns:
                Dictionary containing list of available audio devices with their properties.
            """
            logger.info("list_audio_devices called")

            try:
                from .audio_player import AFPlayBackend
                devices = await AFPlayBackend.get_available_audio_devices()

                return {
                    "success": True,
                    "devices": devices,
                    "device_count": len(devices),
                    "current_configured_device": self.config.audio_device,
                    "message": f"Found {len(devices)} audio output devices"
                }

            except Exception as e:
                logger.error(f"Error in list_audio_devices: {e}")
                return {
                    "success": False,
                    "devices": [],
                    "device_count": 0,
                    "current_configured_device": self.config.audio_device,
                    "error": str(e),
                    "message": f"Failed to list audio devices: {str(e)}"
                }
    
    def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting MCP Play Sound Server...")

        try:
            # Run the FastMCP server
            self.app.run()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            logger.info("MCP Play Sound Server stopped")
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information for debugging."""
        return {
            "name": "MCP Play Sound Server",
            "version": "0.1.0",
            "tools_count": 4,  # We have 4 tools: play_notification_sound, get_audio_status, test_audio_playback, list_audio_devices
            "backends_available": len(self.audio_player.backends),
            "config": {
                "volume_level": self.config.volume_level,
                "enable_fallback": self.config.enable_fallback,
                "custom_sound_configured": bool(self.config.custom_sound_path),
            }
        }
