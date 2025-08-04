# 🌱 FungiForge — Intelligent Mushroom Growing Chamber

**FungiForge** is a full-stack IoT platform for cultivating mushrooms, built with a Raspberry Pi. It integrates camera streaming, servo-based pan/tilt control, real-time environmental monitoring, smart plug automation, and a web-based interface — all developed in Python using Flask.

---

## 🚀 Features

- 📸 Live MJPEG camera stream with pan/tilt controls
- 🌡️ Sensor monitoring (humidity, temperature, soil moisture)
- 🔌 Smart plug automation (e.g., lights, humidifier via Tuya API)
- 🧾 Sensor data logging and historical query support
- 🕒 Timelapse system with customizable interval and resolution
- 🔐 OAuth2-secured RESTful API
- 🧠 Modular architecture designed for future AI integration

---

## System Architecture

- **Raspberry Pi:** Hosts the Flask API, handles camera logic, and stores captured images/data.
- **ATmega Microcontrollers:**
  - **Pan/Tilt Controller:** Receives pan/tilt commands via I²C.
  - **Sensor Node:** Continuously reads from sensors and responds to I²C read requests.
- **Web Interface:**
  - Built with HTML/JS templates served by Flask
  - Displays live video, status panel, and control buttons
  - Future-ready for user authentication and data charts
- **Persistence:**
  - Uses SQLite to store sensor data, timelapse configuration, and user data.
  - Timelapse settings survive reboots.

### 📄 Logging System

FungiForge includes a centralized logging system for observability and debugging:

- **File-based Logging:**  
  All important events (INFO, WARNING, ERROR) are logged to a file defined in `Server/config.py`.  
  Example:
  ```python
  LOG_FILE_PATH = "logs/server.log"
  LOG_LEVEL = "INFO"

## Getting Started

### Prerequisites

- Raspberry Pi (Pi 4 or newer)
- Picamera2-compatible camera
- Two ATmega microcontrollers (e.g., Arduino Uno/Nano)
- Sensors: DHT22 (air temp/humidity), DS18B20 (substrate temp), soil moisture
- Pan & tilt servo hardware
- Tuya-based smart plug (optional)
- I²C wiring between Pi and ATmegas

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/DvdZmd/FungiForge.git
   cd FungiForge
   ```

2. **Run the Setup Script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Flash the Microcontrollers**
   - `Arduino/PanTilt/PanTilt.ino` → pan/tilt ATmega
   - `Arduino/SensorsReadings/SensorsReadings.ino` → sensor ATmega

4. **Start the Server Manually (Optional)**
   ```bash
   chmod +x init.sh
   ./init.sh
   ```
   Web interface will be available at: [http://localhost:5000](http://localhost:5000)

### Configuration

Edit `Server/config.py` to adjust:
- Camera resolution, frame rate, noise settings
- I²C device addresses
- Smart plug IP/device ID/key
- Sensor logging interval (`SENSOR_LOG_INTERVAL = '1m'`)
- Timelapse directory (`TIMELAPSE_DIR = '/your/path'`)
- Logging path and level (`LOG_FILE_PATH = 'logs/server.log'`, `LOG_LEVEL = 'INFO'`)
- Enable/disable features (e.g., `ENABLE_SENSOR_LOGGER = True`)

## Setup & Auto-start

### 🔧 `setup.sh`

This script prepares the Raspberry Pi for running the FungiForge system. It:

- Installs required system packages (e.g., `python3`, `pip`, `smbus2`, etc.)
- Creates a Python virtual environment (`.venv`)
- Installs required Python dependencies from `requirements.txt`
- Sets up a `systemd` service to start the Flask server automatically at boot.

To use it:

```bash
chmod +x setup.sh
./setup.sh
```

The web server will now start automatically every time the Raspberry Pi boots.

### 🚀 `init.sh`

This is a helper script to manually start the Flask server from the command line.

```bash
chmod +x init.sh
./init.sh
```

It activates the virtual environment and runs the `Server/app.py` file.

## Usage Highlights

## 🔐 Authentication Overview

The FungiForge web server supports secure user authentication:

### Username/Password Login
- Users register and log in via HTML forms.
- Passwords are hashed and stored securely.
- Session is created upon login (`session['user_id']`), enabling route protection.

### OAuth2 Token Flow
- API clients can request access tokens using the **Password Grant** (`/oauth/token`).
- Issued tokens must be used to access protected REST endpoints.
- Tokens and clients are persisted using SQLAlchemy models.

### Route Protection
- Use `@login_required` to secure web routes (e.g., home page, camera control).
- Use `@require_oauth()` to secure API endpoints.

### Google Login (Coming Soon)
- Integration planned using Google’s OAuth2 Authorization Code Grant.


### 🔹 Sensor Logging

Sensor data is automatically logged in the background at intervals (e.g., every 1 minute). You can adjust this via:

```python
# config.py
SENSOR_LOG_INTERVAL = '1m'  # 10s, 30s, 5m, 1h, etc.
```

## ⏱️ Timelapse Feature

- Runs on a separate background scheduler thread
- Saves images with timestamps
- Interval and resolution configurable via API/UI
- Independent from manual camera control

### 🔹 History API (Sensor Readings)

`GET /readings_history` supports:
- Pagination (`page`, `per_page`)
- Filters:
  - `start_date`, `end_date` (YYYY-MM-DD)
  - `min_temp_air`, `max_temp_air`
  - `min_humidity`, `max_humidity`
  - `min_temp_sub`, `max_temp_sub`
  - `min_moisture`, `max_moisture`

## Folder Structure (Simplified)

```
Server/
├── app.py
├── config.py
├── camera/
│   ├── picam.py           # Picamera2 init/config
│   ├── timelapse.py       # Background timelapse logic
├── database/
│   ├── models.py          # SQLAlchemy models
│   └── app.db             # SQLite database
├── routes/
│   ├── camera_routes.py
│   ├── i2c_routes.py
│   └── smartplug_routes.py
├── sensors_logger/
│   └── sensor_logger.py   # Background sensor logging loop
├── static/
│   ├── main.js
│   ├── timelapse.js
│   └── ...
├── templates/
│   └── index.html
setup.sh
init.sh
```
---

## 📌 Roadmap

- [ ] WebSocket support for real-time updates
- [ ] CO₂ and light sensors integration
- [ ] Docker container setup
- [ ] Telegram/Email alerts
- [ ] Growth stage classification using AI

---

## License

MIT License. See [LICENSE](LICENSE).

## Acknowledgments

- [Picamera2](https://github.com/raspberrypi/picamera2)
- [Flask](https://flask.palletsprojects.com/)
- [TinyTuya](https://github.com/jasonacox/tinytuya)
- [OpenCV](https://opencv.org/)