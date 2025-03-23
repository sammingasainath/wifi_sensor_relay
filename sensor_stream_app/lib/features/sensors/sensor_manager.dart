import 'dart:async';
import 'dart:convert';
import 'package:sensors_plus/sensors_plus.dart';
import 'package:device_info_plus/device_info_plus.dart';

class SensorManager {
  static final SensorManager _instance = SensorManager._internal();
  factory SensorManager() => _instance;

  SensorManager._internal();

  StreamSubscription<dynamic>? _accelerometerSubscription;
  StreamSubscription<dynamic>? _gyroscopeSubscription;
  final _deviceInfo = DeviceInfoPlugin();

  // Callback for when sensor data is ready
  Function(Map<String, dynamic>)? onSensorData;

  Future<void> initialize() async {
    // Get device info for metadata
    final androidInfo = await _deviceInfo.androidInfo;
    print('Device: ${androidInfo.model}');
  }

  void startSensors() {
    // Start accelerometer
    _accelerometerSubscription =
        accelerometerEvents.listen((AccelerometerEvent event) {
      if (onSensorData != null) {
        onSensorData!({
          'sensorType': 'accelerometer',
          'timestamp': DateTime.now().millisecondsSinceEpoch,
          'values': {
            'x': event.x,
            'y': event.y,
            'z': event.z,
          }
        });
      }
    });

    // Start gyroscope
    _gyroscopeSubscription = gyroscopeEvents.listen((GyroscopeEvent event) {
      if (onSensorData != null) {
        onSensorData!({
          'sensorType': 'gyroscope',
          'timestamp': DateTime.now().millisecondsSinceEpoch,
          'values': {
            'x': event.x,
            'y': event.y,
            'z': event.z,
          }
        });
      }
    });
  }

  void stopSensors() {
    _accelerometerSubscription?.cancel();
    _gyroscopeSubscription?.cancel();
  }
}
