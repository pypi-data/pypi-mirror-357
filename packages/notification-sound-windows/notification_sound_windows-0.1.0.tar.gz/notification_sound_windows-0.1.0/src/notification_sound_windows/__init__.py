"""
MCP Server for Audio Playback Notifications

A Model Context Protocol server that provides audio playback functionality
for agentic coding agents. Enables AI agents to play sound notifications
when coding tasks are completed.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .config import ServerConfig
from .audio_player import AudioPlayer, PlaybackResult

# Only import server if mcp is available (to avoid import errors during testing)
try:
    from .server import PlaySoundServer
    __all__ = [
        "PlaySoundServer",
        "ServerConfig", 
        "AudioPlayer",
        "PlaybackResult",
    ]
except ImportError:
    # MCP dependencies not available, skip server import
    __all__ = [
        "ServerConfig", 
        "AudioPlayer",
        "PlaybackResult",
    ]
