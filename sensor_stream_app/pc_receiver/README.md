# Sensor Stream PC Receiver

This is the PC component of the Sensor Stream application. It receives sensor data and audio from your mobile device over a WebSocket connection and provides visualization and audio playback.

## Features

- Real-time sensor data visualization
- Audio recording and playback
- WebSocket server for receiving data

## Installation

1. Install Python 3.7+ if not already installed
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Start the receiver application

To start both the WebSocket server and data visualizer:

```bash
python run_receiver.py
```

### Server-only mode

To run only the WebSocket server without the visualizer:

```bash
python run_receiver.py --server-only
```

### Audio Player

To play recorded audio files:

```bash
python run_receiver.py --audio
```

Or directly:

```bash
python audio_player.py
```

## Connecting from the Mobile App

1. Make sure your mobile device and PC are on the same WiFi network
2. Start the PC receiver application
3. Note the IP address displayed on the console
4. Enter this IP address in the mobile app, along with port 8082
5. Connect and start streaming data

## Troubleshooting

- If you have connection issues, check your firewall settings
- Ensure port 8082 is not blocked
- Verify both devices are on the same network

## Data Storage

All received data is stored in the `recordings` directory:
- Sensor data: `sensor_data_*.json`
- Audio data: `audio_*.pcm` 