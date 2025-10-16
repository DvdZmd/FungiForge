import threading
import smbus2
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy import and_
from sensors.i2c.sensors import read_i2c_sensors, save_sensor_data
from sensors.i2c.servos import set_pan_tilt, get_current_pan_tilt
from database.models import SensorReading
from config import READ_I2C_SENSORS, READ_SERVOS

i2c_bp = Blueprint('i2c', __name__)

# I²C Bus
bus = smbus2.SMBus(1)  # Use I²C bus 1 (default for Raspberry Pi)
i2c_lock = threading.Lock()

# ======= SERVO CONTROL FUNCTION ===========
@i2c_bp.route('/request_current_pan_tilt', methods=['GET'])
def request_current_pan_tilt():
    
    if not READ_SERVOS:
        return jsonify({"error": "Servo control is disabled"}), 503
    
    return jsonify(get_current_pan_tilt())

@i2c_bp.route('/send_pan_tilt', methods=['POST'])
def send_pan_tilt():
    global requested_pan, requested_tilt, servo_position

    if not READ_SERVOS:
        return jsonify({"error": "Servo control is disabled"}), 503
    
    data = request.get_json()
    if 'pan' in data and 'tilt' in data:
        result = set_pan_tilt(data['pan'], data['tilt'])
        return jsonify({"message": "Servo command queued", **result})
    else:
        return jsonify({"error": "Missing pan or tilt value"}), 400


# ======= READ SENSOR DATA FROM ARDUINO ===========
@i2c_bp.route('/get_sensors', methods=['GET'])
def get_sensors():
    if not READ_I2C_SENSORS:
        return jsonify({"error": "Sensor reading is disabled"}), 503
    
    # Read sensor data from the I²C bus
    sensor_data = read_i2c_sensors()
    #sensor_data = read_i2c_sensors()

    return jsonify(sensor_data)


@i2c_bp.route('/readings_history', methods=['GET'])
def get_readings_history():
    try:
        # Pagination
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        # Filters
        min_temp_air = request.args.get('min_temp_air', type=float)
        max_temp_air = request.args.get('max_temp_air', type=float)
        min_humidity = request.args.get('min_humidity', type=float)
        max_humidity = request.args.get('max_humidity', type=float)
        min_temp_sub = request.args.get('min_temp_sub', type=float)
        max_temp_sub = request.args.get('max_temp_sub', type=float)
        min_moisture = request.args.get('min_moisture', type=float)
        max_moisture = request.args.get('max_moisture', type=float)

        start_date = request.args.get('start_date')  # Format: YYYY-MM-DD
        end_date = request.args.get('end_date')

        # Build query filters
        filters = []

        if min_temp_air is not None:
            filters.append(SensorReading.temperature_air >= min_temp_air)
        if max_temp_air is not None:
            filters.append(SensorReading.temperature_air <= max_temp_air)
        if min_humidity is not None:
            filters.append(SensorReading.humidity_air >= min_humidity)
        if max_humidity is not None:
            filters.append(SensorReading.humidity_air <= max_humidity)
        if min_temp_sub is not None:
            filters.append(SensorReading.temperature_substrate >= min_temp_sub)
        if max_temp_sub is not None:
            filters.append(SensorReading.temperature_substrate <= max_temp_sub)
        if min_moisture is not None:
            filters.append(SensorReading.moisture_substrate >= min_moisture)
        if max_moisture is not None:
            filters.append(SensorReading.moisture_substrate <= max_moisture)
        if start_date:
            filters.append(SensorReading.timestamp >= datetime.strptime(start_date, "%Y-%m-%d"))
        if end_date:
            filters.append(SensorReading.timestamp <= datetime.strptime(end_date, "%Y-%m-%d"))

        # Run query with filters and pagination
        pagination = SensorReading.query.filter(and_(*filters)).order_by(SensorReading.timestamp.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        results = [
            {
                "timestamp": reading.timestamp.isoformat(),
                "temperature_air": reading.temperature_air,
                "humidity_air": reading.humidity_air,
                "temperature_substrate": reading.temperature_substrate,
                "moisture_substrate": reading.moisture_substrate
            }
            for reading in pagination.items
        ]

        return jsonify({
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "readings": results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
