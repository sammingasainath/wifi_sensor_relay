import os
import pyaudio
import numpy as np
import time
from pathlib import Path
import glob

# Path to recordings
RECORDINGS_DIR = Path("recordings")

# Audio settings
SAMPLE_RATE = 44100  # Hz
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1024

class AudioPlayer:
    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.stream = None
        
    def play_audio_file(self, file_path):
        """Play a PCM audio file"""
        try:
            # Read PCM data
            with open(file_path, 'rb') as f:
                audio_data = f.read()
                
            # Calculate duration
            bytes_per_sample = 2  # 16-bit audio
            num_samples = len(audio_data) // bytes_per_sample
            duration = num_samples / SAMPLE_RATE
            
            print(f"Playing audio file: {file_path}")
            print(f"File size: {len(audio_data)} bytes")
            print(f"Duration: {duration:.2f} seconds")
            
            # Open audio stream
            self.stream = self.pyaudio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                output=True
            )
            
            # Play audio in chunks
            offset = 0
            chunk_size = CHUNK * 2  # 2 bytes per sample
            
            while offset < len(audio_data):
                chunk = audio_data[offset:offset + chunk_size]
                self.stream.write(chunk)
                offset += chunk_size
                
            # Close stream
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
            return True
        except Exception as e:
            print(f"Error playing audio file: {e}")
            
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
                
            return False
            
    def list_audio_files(self):
        """List all PCM audio files in the recordings directory"""
        files = sorted(list(RECORDINGS_DIR.glob('audio_*.pcm')))
        return files
        
    def close(self):
        """Close PyAudio"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            
        self.pyaudio.terminate()
        
def interactive_menu(player):
    """Display an interactive menu for playing audio files"""
    while True:
        print("\n== Audio Player Menu ==")
        
        # List audio files
        files = player.list_audio_files()
        
        if not files:
            print("No audio files found in recordings directory.")
            choice = input("\nPress Enter to refresh or 'q' to quit: ").strip().lower()
            if choice == 'q':
                break
            continue
            
        print("\nAvailable audio files:")
        for i, file_path in enumerate(files):
            print(f"{i+1}. {file_path.name}")
            
        # Get user choice
        choice = input("\nEnter file number to play, 'r' to refresh, or 'q' to quit: ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == 'r':
            continue
        
        try:
            file_idx = int(choice) - 1
            if 0 <= file_idx < len(files):
                player.play_audio_file(files[file_idx])
            else:
                print("Invalid file number.")
        except ValueError:
            print("Invalid input. Please enter a number, 'r', or 'q'.")
            
def main():
    print("Starting Audio Player")
    
    # Create audio player
    player = AudioPlayer()
    
    try:
        # Run interactive menu
        interactive_menu(player)
    finally:
        # Clean up
        player.close()
        
    print("Audio Player closed.")

if __name__ == "__main__":
    main() 