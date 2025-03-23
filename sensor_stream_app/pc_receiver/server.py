import asyncio
import json
import base64
import websockets
import socket
import datetime
import os
from pathlib import Path

# Create directories for storing received data
RECORDINGS_DIR = Path("recordings")
RECORDINGS_DIR.mkdir(exist_ok=True)

class SensorStreamServer:
    def __init__(self, host='0.0.0.0', port=8082):
        self.host = host
        self.port = port
        self.active_connections = set()
        self.audio_file = None
        
    async def start_server(self):
        """Start the WebSocket server"""
        server = await websockets.serve(self.handle_connection, self.host, self.port)
        
        # Get the local IP address
        local_ip = self.get_local_ip()
        print(f"Server running on ws://{local_ip}:{self.port}")
        print(f"Use this IP address in your Flutter app")
        
        # Start the server
        await server.wait_closed()
        
    def get_local_ip(self):
        """Get the local IP address of the machine"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't need to be reachable
            s.connect(('10.255.255.255', 1))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        return local_ip
        
    async def handle_connection(self, websocket, path):
        """Handle a WebSocket connection"""
        # Add the connection to the set of active connections
        self.active_connections.add(websocket)
        client = websocket.remote_address[0]
        print(f"New connection from {client}")
        
        try:
            # Process incoming messages
            async for message in websocket:
                await self.process_message(message, client)
        except websockets.ConnectionClosed:
            print(f"Connection closed from {client}")
        finally:
            # Remove the connection from the set of active connections
            self.active_connections.remove(websocket)
            
            # Close the audio file if it's open
            if self.audio_file:
                self.audio_file.close()
                self.audio_file = None
                
    async def process_message(self, message, client):
        """Process an incoming message"""
        try:
            # Parse the JSON message
            print(f"Received message: {message}")
            
            try:
                data = json.loads(message)
                print(f"Parsed JSON: {data}")
            except:
                print(f"Error parsing JSON, treating as raw message")
                # If it's not JSON, just save as raw data
                filename = RECORDINGS_DIR / f"unknown_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(filename, 'w') as f:
                    f.write(message)
                return
            
            # Check the message type
            message_type = data.get('type')
            
            # If the message contains sensorType, values, and timestamp, it's sensor data
            if 'sensorType' in data and 'values' in data and 'timestamp' in data:
                await self.handle_sensor_data({"data": data}, client)
            # If the message has the explicit type field
            elif message_type == 'sensor':
                await self.handle_sensor_data(data, client)
            elif message_type == 'audio':
                await self.handle_audio_data(data, client)
            else:
                print(f"Unknown message type: {message_type}")
                # Save the unknown data
                filename = RECORDINGS_DIR / f"unknown_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error processing message: {e}")
            
    async def handle_sensor_data(self, data, client):
        """Handle sensor data"""
        sensor_data = data.get('data', {})
        sensor_type = sensor_data.get('sensorType', 'unknown')
        timestamp = sensor_data.get('timestamp', '')
        values = sensor_data.get('values', {})
        
        # Format the values as a string
        values_str = ', '.join([f"{key}: {value}" for key, value in values.items()])
        
        # Print the sensor data
        print(f"Sensor data from {client} - {sensor_type}: {values_str}")
        
        # Save the sensor data to a file
        filename = RECORDINGS_DIR / f"sensor_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'a') as f:
            json.dump(sensor_data, f)
            f.write('\n')
            
    async def handle_audio_data(self, data, client):
        """Handle audio data"""
        audio_base64 = data.get('data', '')
        timestamp = data.get('timestamp', '')
        
        try:
            # Decode the base64 audio data
            audio_data = base64.b64decode(audio_base64)
            
            # Create a filename based on the timestamp
            timestamp_obj = datetime.datetime.fromisoformat(timestamp)
            filename = RECORDINGS_DIR / f"audio_{timestamp_obj.strftime('%Y%m%d_%H%M%S')}.pcm"
            
            # Open the file if it's not already open
            if not self.audio_file or self.audio_file.name != str(filename):
                if self.audio_file:
                    self.audio_file.close()
                self.audio_file = open(filename, 'wb')
                
            # Write the audio data to the file
            self.audio_file.write(audio_data)
            self.audio_file.flush()
            
            # Print a message
            print(f"Received audio data from {client} - size: {len(audio_data)} bytes")
        except Exception as e:
            print(f"Error handling audio data: {e}")
            
async def main():
    """Main function"""
    server = SensorStreamServer()
    await server.start_server()
    
if __name__ == "__main__":
    asyncio.run(main()) 