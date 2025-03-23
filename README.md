# WiFi Sensor Relay - Real-time Phone Sensor Data Visualization

<!-- SEO Tags -->
<meta name="description" content="A Flutter and Python-based solution for real-time streaming and visualization of phone sensor data (accelerometer, gyroscope) over WiFi with 3D visualization.">
<meta name="keywords" content="Flutter, Python, IoT, Sensor Data, Real-time Visualization, WebSocket, 3D Visualization, Accelerometer, Gyroscope, Mobile Sensors">
<meta name="author" content="Your Name">

[![Flutter](https://img.shields.io/badge/Flutter-3.0+-blue.svg)](https://flutter.dev/)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📱 Overview

WiFi Sensor Relay is a complete solution for streaming sensor data from your phone to a PC in real-time. It consists of two main components:
1. A Flutter mobile app that captures sensor data
2. A Python-based PC receiver with real-time 3D visualization

### Features

- ✨ Real-time sensor data streaming over WiFi
- 📊 3D visualization of phone orientation
- 🔄 Support for accelerometer and gyroscope data
- 💾 Automatic data recording for analysis
- 🛠️ Configurable axis mapping and calibration
- 📡 WebSocket-based communication

## 🚀 Getting Started

### Prerequisites

1. **Flutter Setup**
   - Install [Flutter](https://flutter.dev/docs/get-started/install) (3.0 or higher)
   - Install [Android Studio](https://developer.android.com/studio) or [VS Code](https://code.visualstudio.com/)
   - A physical Android/iOS device (emulators don't have sensor data)

2. **Python Setup**
   - Install [Python](https://www.python.org/downloads/) (3.7 or higher)
   - Required Python packages (installed automatically)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/sammingasainath/wifi_sensor_relay.git
   cd wifi_sensor_relay
   ```

2. **Mobile App Setup**
   ```bash
   cd sensor_stream_app
   flutter pub get
   flutter build apk  # For Android
   # or
   flutter build ios  # For iOS (requires Mac)
   ```

3. **PC Receiver Setup**
   ```bash
   cd pc_receiver
   pip install -r requirements.txt
   ```

## 📱 Running the Application

### 1. Start the PC Receiver

#### Easy Method
- Double-click `pc_receiver/start_receiver.bat`
  - This will start both the server and visualizer

#### Manual Method
1. Open two terminal windows in the `pc_receiver` directory
2. In the first terminal:
   ```bash
   python server.py
   ```
3. In the second terminal:
   ```bash
   python visualizer.py
   ```

### 2. Run the Mobile App

1. Connect your phone to the same WiFi network as your PC
2. Install and open the app
3. Enter your PC's WebSocket address (shown in the server window)
   - Format: `ws://YOUR_PC_IP:8082`
4. Click "Start Streaming"

### 3. Using the Visualizer

The visualizer provides several controls:
- **Calibration**: Click "Calibrate All" or individual axis calibration buttons
- **Axis Mapping**: Use "Swap X-Y", "Swap Y-Z", "Swap X-Z" to correct orientation
- **View Mode**: Toggle between portrait and landscape orientations
- **Reset**: "Reset All" button to return to default settings

## 📁 Project Structure

```
wifi_sensor_relay/
├── sensor_stream_app/        # Flutter mobile app
│   ├── lib/
│   │   ├── features/
│   │   │   ├── sensors/     # Sensor data collection
│   │   │   └── network/     # WebSocket client
│   │   └── main.dart        # App entry point
│   └── pubspec.yaml         # Flutter dependencies
└── pc_receiver/             # Python PC receiver
    ├── server.py            # WebSocket server
    ├── visualizer.py        # 3D visualization
    ├── run_receiver.py      # Combined runner
    └── requirements.txt     # Python dependencies
```

## 🔧 Troubleshooting

1. **Connection Issues**
   - Ensure both devices are on the same network
   - Check if the IP address is correct
   - Verify no firewall is blocking port 8082

2. **Visualization Problems**
   - Use axis swap buttons to correct orientation
   - Click "Reset All" and recalibrate
   - Place phone flat on table for initial calibration

3. **Performance Issues**
   - Reduce update frequency if visualization is slow
   - Close other 3D applications
   - Ensure Python packages are up to date

## 📈 Data Recording

Sensor data is automatically recorded in:
- Location: `pc_receiver/recordings/`
- Format: JSON files with timestamp, sensor type, and values
- Naming: `sensor_data_YYYYMMDD_HHMMSS.json`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flutter team for the excellent mobile framework
- Python community for visualization libraries
- All contributors and users of this project

<!-- Additional SEO -->
<meta property="og:title" content="WiFi Sensor Relay - Real-time Phone Sensor Visualization">
<meta property="og:description" content="Stream and visualize phone sensor data in real-time with 3D visualization">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image"> 