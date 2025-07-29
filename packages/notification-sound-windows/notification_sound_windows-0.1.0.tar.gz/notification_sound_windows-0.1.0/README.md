# Notification Sound Windows

A Windows notification sound player for Model Context Protocol (MCP) servers. This package provides simple audio playback functionality for Windows systems, enabling AI agents and applications to play sound notifications.

> **✨ Windows Focused**
> This package is specifically designed and optimized for Windows systems, providing reliable audio notification capabilities.

## Features

- **Windows Audio Support**: Native Windows sound playback using system APIs
- **Default Sound**: Bundled notification sound for immediate use
- **Custom Audio**: Support for custom audio files (WAV, MP3, FLAC, OGG, M4A)
- **Intelligent Fallback**: Automatic fallback to default sound if custom audio fails
- **Easy Integration**: Simple API for integration with MCP servers and applications

## Installation & Setup

### Development Setup

1. **Clone and install**:
```bash
git clone <repository-url>
cd notification-sound-windows
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

2. **Configure Claude Desktop**:
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "notification-sound": {
      "command": "uv",
      "args": [
              "run",
              "mcp-server-play-sound"
          ],
    }
  }
}
```

3. **Test**: Restart Claude Desktop and ask: "Can you play a notification sound?"

## Configuration

Environment variables (optional):
- `CUSTOM_SOUND_PATH`: Path to custom audio file
- `VOLUME_LEVEL`: Playback volume (0.0-1.0, default: 0.8)
- `ENABLE_FALLBACK`: Enable fallback to default sound (default: true)
- `AUDIO_DEVICE`: Specific audio output device name (e.g., "Mac Studio Speakers")

## Available Tools

### `play_notification_sound`
Plays a notification sound to alert the user.

**Parameters:**
- `custom_sound_path` (optional): Path to custom audio file
- `message` (optional): Context message for the notification

### `get_audio_status`
Returns current audio system status and configuration.

### `test_audio_playback`
Tests audio playback functionality.

**Parameters:**
- `use_custom` (optional): Test with custom sound if configured

### `list_audio_devices`
Lists all available audio output devices on the system.

**Returns:**
- List of available audio devices with their properties
- Current configured device (if any)
- Default device information

## Development

### Prerequisites
- Python 3.10+
- uv (recommended) or pip

### Testing
```bash
pytest tests/
```

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- Python audio library maintainers
