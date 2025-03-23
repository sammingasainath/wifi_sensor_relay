import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;

class WebSocketClient {
  static final WebSocketClient _instance = WebSocketClient._internal();
  factory WebSocketClient() => _instance;

  WebSocketClient._internal();

  WebSocketChannel? _channel;
  bool _isConnected = false;
  String? _serverAddress;

  bool get isConnected => _isConnected;
  String? get serverAddress => _serverAddress;

  Future<bool> connect(String address) async {
    try {
      _serverAddress = address;
      _channel = WebSocketChannel.connect(Uri.parse(address));
      _isConnected = true;
      print('Connected to WebSocket server at $address');

      // Listen for server messages
      _channel?.stream.listen((message) {
        print('Received: $message');
      }, onError: (error) {
        print('WebSocket error: $error');
        _isConnected = false;
      }, onDone: () {
        print('WebSocket connection closed');
        _isConnected = false;
      });

      return true;
    } catch (e) {
      print('Failed to connect: $e');
      _isConnected = false;
      return false;
    }
  }

  void sendData(Map<String, dynamic> data) {
    if (_isConnected && _channel != null) {
      try {
        _channel!.sink.add(jsonEncode(data));
      } catch (e) {
        print('Error sending data: $e');
      }
    }
  }

  void disconnect() {
    _channel?.sink.close(status.goingAway);
    _isConnected = false;
    _serverAddress = null;
  }
}
