# config.py

# Default camera resolution
import os

# Logging
LOG_FILE_PATH = "/home/pi/Desktop/logs/server.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

#timelapse folder
TIMELAPSE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '/home/pi/Desktop/timelapse'))

# List of available camera resolutions (width, height)
AVAILABLE_RESOLUTIONS = [
    (640, 480),
    (800, 600),
    (1280, 720),
    (1920, 1080),
    (2592, 1944),
]

# I2C addresses for Arduino devices
ARDUINO_PAN_TILT = 0x10      # I2C address for pan/tilt servo controller
ARDUINO_SENSORS = 0x20       # I2C address for sensor readings

# Axis inversion flags for servo control
INVERT_PAN_AXIS = False      # Set to True to invert pan axis
INVERT_TILT_AXIS = False     # Set to True to invert tilt axis

# I2C bus configuration
I2C_BUS_ID = 1               # Default I2C bus on Raspberry Pi

# Camera settings
FRAME_RATE = 60              # Camera frame rate (FPS)
NOISE_REDUCTION_MODE = 2     # Camera noise reduction mode

# Flags and intervals for reading sensors and servos and store in database
READ_SENSORS = True         # Enable/disable periodic sensor reading
READ_SERVOS = True          # Enable/disable periodic servo reading
READ_SENSORS_INTERVAL = 0.1  # Interval (seconds) for sensor polling
READ_SERVOS_INTERVAL = 0.1   # Interval (seconds) for servo polling
SENSOR_LOG_INTERVAL = '1m'  # Options: '10s', '30s', '1m', '5m', '1h'
ENABLE_SENSOR_LOGGER = True

# Smart Plug Configuration (TinyTuya)
SMARTPLUG_DEVICE_ID = 'YOUR_TUYA_DEVICE_ID'     # Tuya device ID
SMARTPLUG_IP = '192.168.x.x'                    # Smart plug IP address
SMARTPLUG_LOCAL_KEY = 'LOCAL_KEY'               # Local key for device authentication
SMARTPLUG_PROTOCOL_VERSION = 3.4                # Tuya protocol version