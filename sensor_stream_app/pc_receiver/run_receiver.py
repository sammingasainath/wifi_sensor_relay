import subprocess
import sys
import time
import os
import argparse
import signal
from pathlib import Path

def run_server_and_visualizer(server_only=False):
    """Run the WebSocket server and optionally the visualizer"""
    print("Starting Sensor Stream Receiver...")
    
    # Create the recordings directory if it doesn't exist
    Path("recordings").mkdir(exist_ok=True)
    
    # Start the WebSocket server in a separate process
    server_process = subprocess.Popen([sys.executable, "server.py"])
    
    # Start the visualizer in the current process if not server_only
    visualizer_process = None
    if not server_only:
        print("Starting data visualizer...")
        time.sleep(1)  # Give the server a moment to start
        visualizer_process = subprocess.Popen([sys.executable, "visualizer.py"])
    
    try:
        # Wait for the processes to complete
        server_process.wait()
        if visualizer_process:
            visualizer_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        # Clean shutdown of processes
        if server_process.poll() is None:
            if os.name == 'nt':  # Windows
                server_process.terminate()
            else:  # Unix/Linux
                os.kill(server_process.pid, signal.SIGTERM)
        
        if visualizer_process and visualizer_process.poll() is None:
            if os.name == 'nt':  # Windows
                visualizer_process.terminate()
            else:  # Unix/Linux
                os.kill(visualizer_process.pid, signal.SIGTERM)
    
    print("Sensor Stream Receiver stopped")

def play_audio_recordings():
    """Run the audio player"""
    print("Starting audio player...")
    subprocess.run([sys.executable, "audio_player.py", "--interactive"])

def main():
    parser = argparse.ArgumentParser(description="Sensor Stream Receiver")
    parser.add_argument("--server-only", action="store_true", help="Run only the server without visualizer")
    parser.add_argument("--audio-player", action="store_true", help="Run the audio player for recordings")
    args = parser.parse_args()
    
    if args.audio_player:
        play_audio_recordings()
    else:
        run_server_and_visualizer(server_only=args.server_only)

if __name__ == "__main__":
    main() 