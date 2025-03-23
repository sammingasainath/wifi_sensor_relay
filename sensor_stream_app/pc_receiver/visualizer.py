import json
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.animation as animation
from collections import deque
from pathlib import Path
import math

# Path to recordings
RECORDINGS_DIR = Path("recordings")
RECORDINGS_DIR.mkdir(exist_ok=True)

# Very fast update interval
UPDATE_INTERVAL = 30  # milliseconds

class SensorDataVisualizer:
    def __init__(self):
        # Create figure - simple and focused
        self.fig = plt.figure(figsize=(8, 8))
        
        # Create 3D axes for phone orientation
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_title('Phone Orientation (Realtime)')
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(-1, 1)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        
        # Set fixed viewing angle to reduce computation
        self.ax.view_init(elev=30, azim=45)
        
        # Axis mapping (for swapping axes)
        self.axis_mapping = {
            'x': 0,  # Maps to original x
            'y': 1,  # Maps to original y
            'z': 2   # Maps to original z
        }
        
        # Sign flipping for each axis (1 or -1)
        self.axis_signs = {
            'x': 1,
            'y': 1,
            'z': 1
        }
        
        # Phone dimensions
        self.is_portrait = True
        self.update_phone_model()
        
        # Reference orientation (used for calibration)
        self.ref_accel = {'x': 0, 'y': 0, 'z': 0}
        self.ref_orientation = {'pitch': 0, 'roll': 0, 'yaw': 0}
        
        # Calibration offsets
        self.pitch_offset = -math.pi/2  # Default offset to align with screen up
        self.roll_offset = 0
        self.yaw_offset = 0
        
        # Orientation angles
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        
        # Calibration flags for each axis
        self.calibrated_axes = {'pitch': False, 'roll': False, 'yaw': False}
        
        # Keep track of last processed file time
        self.last_file_time = 0
        
        # Initialize sensor data buffers
        self.accel_data = {'x': 0, 'y': 0, 'z': 0}
        self.gyro_data = {'x': 0, 'y': 0, 'z': 0}
        
        # Last update time for dt calculation
        self.last_update_time = time.time()
        
        # Add buttons for calibration and axis swapping
        plt.subplots_adjust(bottom=0.3)  # Make more room for buttons
        button_width = 0.15
        button_height = 0.05
        button_spacing = 0.02
        
        # Create buttons for calibration
        self.calibrate_all_button_ax = plt.axes([0.2, 0.15, button_width, button_height])
        self.calibrate_all_button = plt.Button(self.calibrate_all_button_ax, 'Calibrate All')
        self.calibrate_all_button.on_clicked(self.calibrate)
        
        self.calibrate_pitch_button_ax = plt.axes([0.4, 0.15, button_width, button_height])
        self.calibrate_pitch_button = plt.Button(self.calibrate_pitch_button_ax, 'Cal Pitch')
        self.calibrate_pitch_button.on_clicked(lambda x: self.calibrate_axis('pitch'))
        
        self.calibrate_roll_button_ax = plt.axes([0.6, 0.15, button_width, button_height])
        self.calibrate_roll_button = plt.Button(self.calibrate_roll_button_ax, 'Cal Roll')
        self.calibrate_roll_button.on_clicked(lambda x: self.calibrate_axis('roll'))
        
        self.calibrate_yaw_button_ax = plt.axes([0.8, 0.15, button_width, button_height])
        self.calibrate_yaw_button = plt.Button(self.calibrate_yaw_button_ax, 'Cal Yaw')
        self.calibrate_yaw_button.on_clicked(lambda x: self.calibrate_axis('yaw'))
        
        # Create buttons for axis swapping
        self.swap_xy_button_ax = plt.axes([0.2, 0.05, button_width, button_height])
        self.swap_xy_button = plt.Button(self.swap_xy_button_ax, 'Swap X-Y')
        self.swap_xy_button.on_clicked(lambda x: self.swap_axes('x', 'y'))
        
        self.swap_yz_button_ax = plt.axes([0.4, 0.05, button_width, button_height])
        self.swap_yz_button = plt.Button(self.swap_yz_button_ax, 'Swap Y-Z')
        self.swap_yz_button.on_clicked(lambda x: self.swap_axes('y', 'z'))
        
        self.swap_xz_button_ax = plt.axes([0.6, 0.05, button_width, button_height])
        self.swap_xz_button = plt.Button(self.swap_xz_button_ax, 'Swap X-Z')
        self.swap_xz_button.on_clicked(lambda x: self.swap_axes('x', 'z'))
        
        # Add buttons for flipping axes
        self.flip_x_button_ax = plt.axes([0.2, 0.25, button_width, button_height])
        self.flip_x_button = plt.Button(self.flip_x_button_ax, 'Flip X')
        self.flip_x_button.on_clicked(lambda x: self.flip_axis('x'))
        
        self.flip_y_button_ax = plt.axes([0.4, 0.25, button_width, button_height])
        self.flip_y_button = plt.Button(self.flip_y_button_ax, 'Flip Y')
        self.flip_y_button.on_clicked(lambda x: self.flip_axis('y'))
        
        self.flip_z_button_ax = plt.axes([0.6, 0.25, button_width, button_height])
        self.flip_z_button = plt.Button(self.flip_z_button_ax, 'Flip Z')
        self.flip_z_button.on_clicked(lambda x: self.flip_axis('z'))
        
        self.reset_axes_button_ax = plt.axes([0.8, 0.05, button_width, button_height])
        self.reset_axes_button = plt.Button(self.reset_axes_button_ax, 'Reset All')
        self.reset_axes_button.on_clicked(self.reset_axes)
        
        # Create orientation toggle button
        self.orientation_button_ax = plt.axes([0.2, 0.35, button_width * 2, button_height])
        self.orientation_button = plt.Button(self.orientation_button_ax, 'Toggle Portrait/Landscape')
        self.orientation_button.on_clicked(self.toggle_orientation)
        
        # Status text
        self.status_text = self.fig.text(
            0.02, 0.02, "", fontsize=9,
            bbox=dict(facecolor='white', alpha=0.7)
        )
    
    def calibrate_axis(self, axis):
        """Calibrate a specific axis using current sensor data"""
        print(f"Calibrating {axis} axis...")
        
        # Store current accelerometer data as reference
        self.ref_accel = {
            'x': self.accel_data['x'],
            'y': self.accel_data['y'],
            'z': self.accel_data['z']
        }
        
        # Calculate gravity vector magnitude
        grav_mag = math.sqrt(sum(v*v for v in self.ref_accel.values()))
        
        if grav_mag < 0.1:
            print(f"Calibration failed: Insufficient sensor data")
            return
            
        if axis == 'pitch':
            # Calculate pitch offset to make screen face up
            self.pitch_offset = -math.atan2(self.ref_accel['x'], 
                                          math.sqrt(self.ref_accel['y']**2 + self.ref_accel['z']**2))
            self.pitch = 0
            self.calibrated_axes['pitch'] = True
            
        elif axis == 'roll':
            # Calculate roll offset
            self.roll_offset = -math.atan2(self.ref_accel['y'], self.ref_accel['z'])
            self.roll = 0
            self.calibrated_axes['roll'] = True
            
        elif axis == 'yaw':
            # Store current yaw as offset
            self.yaw_offset = -self.yaw
            self.yaw = 0
            self.calibrated_axes['yaw'] = True
        
        # Store reference orientation
        self.ref_orientation = {
            'pitch': self.pitch,
            'roll': self.roll,
            'yaw': self.yaw
        }
        
        print(f"{axis.capitalize()} calibrated: offset = {math.degrees(getattr(self, f'{axis}_offset')):.1f}°")
    
    def calibrate(self, event=None):
        """Calibrate all axes"""
        print("Calibrating all axes...")
        
        # Calibrate each axis
        for axis in ['pitch', 'roll', 'yaw']:
            self.calibrate_axis(axis)
        
        print("Full calibration complete")
    
    def rotation_matrix(self):
        """Create rotation matrix from Euler angles with calibration offsets"""
        # Apply calibration offsets
        pitch = self.pitch + self.pitch_offset
        roll = self.roll + self.roll_offset
        yaw = self.yaw + self.yaw_offset
        
        # Create rotation matrix
        cy, sy = math.cos(yaw), math.sin(yaw)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cr, sr = math.cos(roll), math.sin(roll)
        
        R = np.array([
            [cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
            [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
            [-sp, cp*sr, cp*cr]
        ])
        
        return R
    
    def update_orientation(self, gyro_x, gyro_y, gyro_z, dt):
        """Update orientation using gyroscope data"""
        # Apply gyro readings with light filtering
        filter_factor = 0.8  # Higher value = more responsive
        self.roll += gyro_x * dt * filter_factor
        self.pitch += gyro_y * dt * filter_factor
        self.yaw += gyro_z * dt * filter_factor
    
    def check_new_data(self):
        """Check for new sensor data files - minimized file system access"""
        try:
            # Only check the most recent file
            latest_files = sorted(RECORDINGS_DIR.glob('sensor_data_*.json'), 
                                 key=os.path.getmtime, reverse=True)
            
            if not latest_files:
                return
                
            latest_file = latest_files[0]
            file_time = os.path.getmtime(latest_file)
            
            # Skip if already processed
            if file_time <= self.last_file_time:
                return
                
            # Process the file
            with open(latest_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        sensor_type = data.get('sensorType', '')
                        values = data.get('values', {})
                        
                        if sensor_type == 'accelerometer':
                            self.accel_data['x'] = values.get('x', 0)
                            self.accel_data['y'] = values.get('y', 0)
                            self.accel_data['z'] = values.get('z', 0)
                        elif sensor_type == 'gyroscope':
                            self.gyro_data['x'] = values.get('x', 0)
                            self.gyro_data['y'] = values.get('y', 0)
                            self.gyro_data['z'] = values.get('z', 0)
                    except json.JSONDecodeError:
                        continue
                        
            # Update last processed time
            self.last_file_time = file_time
        except Exception as e:
            print(f"Error reading sensor data: {e}")
    
    def swap_axes(self, axis1, axis2):
        """Swap two axes in the coordinate system"""
        print(f"Swapping {axis1} and {axis2} axes")
        # Swap the axis mappings
        temp = self.axis_mapping[axis1]
        self.axis_mapping[axis1] = self.axis_mapping[axis2]
        self.axis_mapping[axis2] = temp
        
        # Reset angles after swapping
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        
        # Reset calibration state for affected axes
        self.calibrated_axes[axis1] = False
        self.calibrated_axes[axis2] = False
        
        print(f"New axis mapping: {self.axis_mapping}")
    
    def flip_axis(self, axis):
        """Flip the direction of an axis"""
        print(f"Flipping {axis} axis")
        self.axis_signs[axis] *= -1
        
        # Reset angles and calibration for the flipped axis
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.calibrated_axes[axis] = False
        
        print(f"New axis signs: {self.axis_signs}")
    
    def reset_axes(self, event=None):
        """Reset axes to their original configuration"""
        print("Resetting axes to default configuration")
        self.axis_mapping = {'x': 0, 'y': 1, 'z': 2}
        self.axis_signs = {'x': 1, 'y': 1, 'z': 1}
        
        # Reset all angles and calibration
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        self.pitch_offset = -math.pi/2
        self.roll_offset = 0
        self.yaw_offset = 0
        self.calibrated_axes = {'pitch': False, 'roll': False, 'yaw': False}
        
        print("Axes reset complete")
    
    def apply_axis_mapping(self, data):
        """Apply axis mapping and signs to input data"""
        if isinstance(data, dict):
            # For dictionary inputs (like accel_data and gyro_data)
            mapped_data = {}
            reverse_mapping = {v: k for k, v in self.axis_mapping.items()}
            for i in range(3):
                axis = reverse_mapping[i]
                mapped_data[axis] = data[axis] * self.axis_signs[axis]
            return mapped_data
        else:
            # For array inputs (like vertices)
            mapped_data = np.zeros_like(data)
            for i in range(len(data)):
                mapped_data[i] = [
                    data[i][self.axis_mapping['x']] * self.axis_signs['x'],
                    data[i][self.axis_mapping['y']] * self.axis_signs['y'],
                    data[i][self.axis_mapping['z']] * self.axis_signs['z']
                ]
            return mapped_data
    
    def update_plot(self, frame):
        """Update the visualization - simplified for performance"""
        # Get sensor data
        self.check_new_data()
        
        # Calculate time delta
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        dt = min(dt, 0.1)  # Limit dt to avoid large jumps
        
        # Auto-calibrate on first significant data
        if not self.calibrated_axes['pitch'] and abs(self.accel_data['z']) > 1.0:
            self.calibrate()
        
        # Update orientation using mapped gyro data
        mapped_gyro = self.apply_axis_mapping(self.gyro_data)
        self.update_orientation(
            mapped_gyro['x'],
            mapped_gyro['y'],
            mapped_gyro['z'],
            dt
        )
        
        # Clear the axis each frame (most reliable for 3D)
        self.ax.clear()
        
        # Reset axes properties
        self.ax.set_title('Phone Orientation (Realtime)')
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(-1, 1)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        
        # Apply rotation
        R = self.rotation_matrix()
        rotated_vertices = np.dot(self.vertices, R.T)
        
        # Apply axis mapping to rotated vertices
        mapped_vertices = self.apply_axis_mapping(rotated_vertices)
        
        # Draw the phone
        # Draw back of phone (gray)
        back_verts = [mapped_vertices[[0, 1, 2, 3]]]
        back = Poly3DCollection(back_verts, facecolors='gray', edgecolors='k', alpha=0.7)
        self.ax.add_collection3d(back)
        
        # Draw screen of phone (blue)
        screen_verts = [mapped_vertices[[4, 5, 6, 7]]]
        screen = Poly3DCollection(screen_verts, facecolors='blue', edgecolors='k', alpha=0.7)
        self.ax.add_collection3d(screen)
        
        # Draw other sides
        sides = [
            mapped_vertices[[0, 1, 5, 4]],  # front edge
            mapped_vertices[[1, 2, 6, 5]],  # right
            mapped_vertices[[2, 3, 7, 6]],  # back edge
            mapped_vertices[[3, 0, 4, 7]]   # left
        ]
        side_colors = ['r', 'g', 'c', 'm']
        for i, verts in enumerate(sides):
            side = Poly3DCollection([verts], facecolors=side_colors[i], edgecolors='k', alpha=0.4)
            self.ax.add_collection3d(side)
        
        # Add direction indicator (z-axis of phone = normal to screen)
        arrow_length = 0.8
        origin = np.array([0, 0, 0])
        z_axis = np.dot(np.array([0, 0, arrow_length]), R.T)
        self.ax.quiver(
            origin[0], origin[1], origin[2],
            z_axis[0], z_axis[1], z_axis[2],
            color='blue', arrow_length_ratio=0.1
        )
        
        # Update status text with mapped values and axis signs
        mapped_accel = self.apply_axis_mapping(self.accel_data)
        mapped_gyro = self.apply_axis_mapping(self.gyro_data)
        accel_mag = math.sqrt(sum(v*v for v in mapped_accel.values()))
        status_text = f"Accel: X={mapped_accel['x']:.1f}, Y={mapped_accel['y']:.1f}, Z={mapped_accel['z']:.1f} (Mag={accel_mag:.1f})\n"
        status_text += f"Gyro: X={mapped_gyro['x']:.1f}, Y={mapped_gyro['y']:.1f}, Z={mapped_gyro['z']:.1f}\n"
        status_text += f"Angles: P={np.degrees(self.pitch):.0f}°, R={np.degrees(self.roll):.0f}°, Y={np.degrees(self.yaw):.0f}°\n"
        status_text += f"Calibrated: Pitch={self.calibrated_axes['pitch']}, Roll={self.calibrated_axes['roll']}, Yaw={self.calibrated_axes['yaw']}\n"
        status_text += f"Axis Map: X→{list(self.axis_mapping.keys())[list(self.axis_mapping.values()).index(0)]}({self.axis_signs['x']}), "
        status_text += f"Y→{list(self.axis_mapping.keys())[list(self.axis_mapping.values()).index(1)]}({self.axis_signs['y']}), "
        status_text += f"Z→{list(self.axis_mapping.keys())[list(self.axis_mapping.values()).index(2)]}({self.axis_signs['z']})"
        
        self.status_text.set_text(status_text)
        
        return []  # No blitting for 3D plots
    
    def start_visualization(self):
        """Start the visualization"""
        ani = animation.FuncAnimation(
            self.fig, 
            self.update_plot, 
            interval=UPDATE_INTERVAL,
            blit=False,
            cache_frame_data=False
        )
        
        # Show the plot with hardware acceleration if available
        plt.rcParams['figure.autolayout'] = True
        plt.show()

    def update_phone_model(self):
        """Update phone model vertices based on orientation"""
        if self.is_portrait:
            # Portrait mode (taller than wide)
            self.vertices = np.array([
                [-0.3, -0.6, -0.05],  # 0
                [0.3, -0.6, -0.05],   # 1
                [0.3, 0.6, -0.05],    # 2
                [-0.3, 0.6, -0.05],   # 3
                [-0.3, -0.6, 0.05],   # 4
                [0.3, -0.6, 0.05],    # 5
                [0.3, 0.6, 0.05],     # 6
                [-0.3, 0.6, 0.05]     # 7
            ])
        else:
            # Landscape mode (wider than tall)
            self.vertices = np.array([
                [-0.6, -0.3, -0.05],  # 0
                [0.6, -0.3, -0.05],   # 1
                [0.6, 0.3, -0.05],    # 2
                [-0.6, 0.3, -0.05],   # 3
                [-0.6, -0.3, 0.05],   # 4
                [0.6, -0.3, 0.05],    # 5
                [0.6, 0.3, 0.05],     # 6
                [-0.6, 0.3, 0.05]     # 7
            ])
    
    def toggle_orientation(self, event=None):
        """Toggle between portrait and landscape orientation"""
        self.is_portrait = not self.is_portrait
        self.update_phone_model()
        print(f"Switched to {'portrait' if self.is_portrait else 'landscape'} mode")

def main():
    print("Starting Realtime 3D Orientation Visualizer")
    print("Monitoring for sensor data in the recordings directory...")
    visualizer = SensorDataVisualizer()
    visualizer.start_visualization()

if __name__ == "__main__":
    main() 