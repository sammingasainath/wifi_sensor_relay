import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'features/sensors/sensor_manager.dart';
import 'features/network/websocket_client.dart';

void main() {
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sensor Stream',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const SensorStreamPage(),
    );
  }
}

class SensorStreamPage extends StatefulWidget {
  const SensorStreamPage({super.key});

  @override
  State<SensorStreamPage> createState() => _SensorStreamPageState();
}

class _SensorStreamPageState extends State<SensorStreamPage> {
  final _sensorManager = SensorManager();
  final _webSocketClient = WebSocketClient();
  final _serverController =
      TextEditingController(text: 'ws://192.168.1.100:8082');
  bool _isStreaming = false;

  @override
  void initState() {
    super.initState();
    _setupSensors();
  }

  Future<void> _setupSensors() async {
    await _sensorManager.initialize();
    _sensorManager.onSensorData = _handleSensorData;
  }

  void _handleSensorData(Map<String, dynamic> data) {
    if (_webSocketClient.isConnected) {
      _webSocketClient.sendData(data);
    }
  }

  Future<void> _toggleStreaming() async {
    if (!_isStreaming) {
      // Start streaming
      final connected = await _webSocketClient.connect(_serverController.text);
      if (connected) {
        _sensorManager.startSensors();
        setState(() => _isStreaming = true);
      }
    } else {
      // Stop streaming
      _sensorManager.stopSensors();
      _webSocketClient.disconnect();
      setState(() => _isStreaming = false);
    }
  }

  @override
  void dispose() {
    _sensorManager.stopSensors();
    _webSocketClient.disconnect();
    _serverController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sensor Stream'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _serverController,
              decoration: const InputDecoration(
                labelText: 'Server Address',
                hintText: 'ws://192.168.1.100:8082',
                border: OutlineInputBorder(),
              ),
              enabled: !_isStreaming,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _toggleStreaming,
              style: ElevatedButton.styleFrom(
                backgroundColor: _isStreaming ? Colors.red : Colors.green,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.all(16),
              ),
              child: Text(_isStreaming ? 'Stop Streaming' : 'Start Streaming'),
            ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Status: ${_isStreaming ? "Streaming" : "Stopped"}',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    if (_webSocketClient.isConnected) ...[
                      const SizedBox(height: 8),
                      Text('Connected to: ${_webSocketClient.serverAddress}'),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
