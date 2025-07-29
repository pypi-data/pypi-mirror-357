#!/usr/bin/env python3
"""
Enhanced test script for MCP server audio device functionality.

This script provides comprehensive testing of audio device selection,
switching, and restoration capabilities.

Usage:
    python test_audio_devices.py                           # List devices and show usage
    python test_audio_devices.py --audio-device "BW01"     # Test specific device
    python test_audio_devices.py --list-only               # Only list devices
    python test_audio_devices.py --current                 # Show current device
"""

import sys
import asyncio
import os
import argparse
import subprocess
sys.path.insert(0, '../src')

from notification_sound_windows.config import ServerConfig
from notification_sound_windows.audio_player import AudioPlayer, AFPlayBackend

async def get_current_device():
    """Get the current default audio device."""
    try:
        result = subprocess.run(["SwitchAudioSource", "-c"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "Unknown"

async def list_available_devices():
    """List all available audio output devices."""
    try:
        devices = await AFPlayBackend.get_available_audio_devices()
        return devices
    except Exception as e:
        print(f"❌ Error listing devices: {e}")
        return []

async def test_specific_device(device_name):
    """Test audio playback with a specific device."""
    print(f"=== Testing Audio Device: {device_name} ===")

    # Get current device before test
    original_device = await get_current_device()
    print(f"Original device: {original_device}")

    try:
        # Set the audio device in environment
        os.environ['AUDIO_DEVICE'] = device_name

        # Create configuration with the device
        config = ServerConfig.from_environment()
        config.validate()
        print(f"Config audio device: {config.audio_device}")

        # Create audio player
        player = AudioPlayer(config)
        print(f"AudioPlayer created with {len(player.backends)} backends")

        # Check device before playback
        device_before = await get_current_device()
        print(f"Device before playback: {device_before}")

        # Test playback
        print(f"Playing notification sound through '{device_name}'...")
        result = await player.play_notification()

        if result.status.value == "success":
            print("✅ Audio playback succeeded!")
            print(f"Backend used: {result.backend_used}")
            print(f"Message: {result.message}")

            # Check device after playback (should be restored)
            await asyncio.sleep(1)  # Give time for restoration
            device_after = await get_current_device()
            print(f"Device after playback: {device_after}")

            # Verify restoration
            if device_after == original_device:
                print("✅ Device restoration successful!")
                print(f"Successfully restored to: {original_device}")
                return True
            else:
                print("❌ Device restoration failed!")
                print(f"Expected: {original_device}")
                print(f"Actual: {device_after}")
                return False
        else:
            print("❌ Audio playback failed!")
            print(f"Status: {result.status.value}")
            print(f"Message: {result.message}")
            return False

    except Exception as e:
        print(f"❌ Exception in device-specific playback: {e}")
        import traceback
        traceback.print_exc()
        return False

async def show_device_info():
    """Show comprehensive device information."""
    print("=== Audio Device Information ===")

    # Current device
    current_device = await get_current_device()
    print(f"\n📱 Current Default Device: {current_device}")

    # Available devices
    print(f"\n🔊 Available Audio Output Devices:")
    devices = await list_available_devices()

    if not devices:
        print("❌ No audio devices found!")
        return False

    for i, device in enumerate(devices, 1):
        default_marker = " (SYSTEM DEFAULT)" if device.get("is_default") else ""
        current_marker = " (CURRENT)" if device['name'] == current_device else ""
        print(f"  {i}. {device['name']}{default_marker}{current_marker}")

    return True

def show_usage_examples():
    """Show usage examples and instructions."""
    print("\n" + "="*60)
    print("📖 USAGE EXAMPLES")
    print("="*60)
    print()
    print("1. List all available devices:")
    print("   python test_audio_devices.py --list-only")
    print()
    print("2. Show current device:")
    print("   python test_audio_devices.py --current")
    print()
    print("3. Test a specific device:")
    print("   python test_audio_devices.py --audio-device \"Mac Studio Speakers\"")
    print("   python test_audio_devices.py --audio-device \"BW01\"")
    print()
    print("4. Test with no device specified (use current default):")
    print("   python test_audio_devices.py --audio-device \"\"")
    print()
    print("💡 TIP: Device names are case-sensitive and must match exactly!")
    print("💡 TIP: Use --list-only first to see available device names")
    print()

async def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Test MCP server audio device functionality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Show device info and usage
  %(prog)s --audio-device "Mac Studio Speakers"  # Test specific device
  %(prog)s --list-only                        # Only list devices
  %(prog)s --current                          # Show current device
        """
    )

    parser.add_argument(
        "--audio-device",
        type=str,
        help="Test audio playback with specified device name"
    )

    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list available audio devices"
    )

    parser.add_argument(
        "--current",
        action="store_true",
        help="Show current default audio device"
    )

    args = parser.parse_args()

    # Handle different modes
    if args.current:
        current_device = await get_current_device()
        print(f"Current default audio device: {current_device}")
        return True

    elif args.list_only:
        success = await show_device_info()
        return success

    elif args.audio_device is not None:
        # Test specific device
        if not args.audio_device.strip():
            print("Testing with no AUDIO_DEVICE set (current system default)...")
            # Clear environment variable
            if 'AUDIO_DEVICE' in os.environ:
                del os.environ['AUDIO_DEVICE']
            success = await test_specific_device("")
        else:
            # Validate device exists
            devices = await list_available_devices()
            device_names = [d['name'] for d in devices]

            if args.audio_device not in device_names:
                print(f"❌ Device '{args.audio_device}' not found!")
                print(f"Available devices: {', '.join(device_names)}")
                return False

            success = await test_specific_device(args.audio_device)

        return success

    else:
        # Default mode: show info and usage
        success = await show_device_info()
        show_usage_examples()
        return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
