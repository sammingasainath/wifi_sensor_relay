@echo off
echo Starting Sensor Stream Receiver...

:: Start the server in a new window
start "Sensor Stream Server" cmd /k python server.py

:: Start the visualizer in a new window
start "Sensor Stream Visualizer" cmd /k python visualizer.py

echo Both components started successfully!
echo Server window title: "Sensor Stream Server"
echo Visualizer window title: "Sensor Stream Visualizer"
echo.
echo To close both components, simply close their respective windows.
pause 