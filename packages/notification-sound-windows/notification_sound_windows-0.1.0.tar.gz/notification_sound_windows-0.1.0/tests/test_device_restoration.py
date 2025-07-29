#!/usr/bin/env python3
"""
Test script to verify device switching and restoration works correctly.
"""

import sys
import asyncio
import os
import subprocess
sys.path.insert(0, '../src')

from notification_sound_windows.config import ServerConfig
from notification_sound_windows.audio_player import AudioPlayer

async def test_device_restoration():
    """Test that device switching and restoration works correctly."""
    print("=== Testing Device Switching and Restoration ===")
    
    # Get current device before test
    try:
        result = subprocess.run(["SwitchAudioSource", "-c"], capture_output=True, text=True)
        if result.returncode == 0:
            original_device = result.stdout.strip()
            print(f"Original device: {original_device}")
        else:
            print("❌ Could not get current device")
            return False
    except Exception as e:
        print(f"❌ Error getting current device: {e}")
        return False
    
    # Test with Mac Studio Speakers configuration
    print(f"\n--- Testing MCP Server with Mac Studio Speakers ---")
    try:
        # Set environment to use Mac Studio Speakers
        os.environ['AUDIO_DEVICE'] = 'Mac Studio Speakers'
        
        # Create and test audio player
        config = ServerConfig.from_environment()
        config.validate()
        print(f"Config audio device: {config.audio_device}")
        
        player = AudioPlayer(config)
        
        # Check device before playback
        result = subprocess.run(["SwitchAudioSource", "-c"], capture_output=True, text=True)
        device_before = result.stdout.strip() if result.returncode == 0 else "unknown"
        print(f"Device before playback: {device_before}")
        
        # Play notification sound
        print("Playing notification sound...")
        playback_result = await player.play_notification()
        
        if playback_result.status.value == "success":
            print("✅ Playback successful!")
            print(f"Message: {playback_result.message}")
        else:
            print("❌ Playback failed!")
            print(f"Error: {playback_result.message}")
            return False
        
        # Check device after playback (should be restored)
        await asyncio.sleep(1)  # Give time for restoration
        result = subprocess.run(["SwitchAudioSource", "-c"], capture_output=True, text=True)
        device_after = result.stdout.strip() if result.returncode == 0 else "unknown"
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
            
            # Try to manually restore
            print(f"Manually restoring to {original_device}...")
            subprocess.run(["SwitchAudioSource", "-s", original_device], capture_output=True)
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to restore original device
        try:
            subprocess.run(["SwitchAudioSource", "-s", original_device], capture_output=True)
        except:
            pass
        return False

if __name__ == "__main__":
    success = asyncio.run(test_device_restoration())
    sys.exit(0 if success else 1)
