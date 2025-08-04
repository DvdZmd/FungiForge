# sensors_logger/sensor_logger.py
import time
import threading
import re
from i2c.sensors import read_sensors, save_sensor_data
from config import SENSOR_LOG_INTERVAL, ENABLE_SENSOR_LOGGER
from logs.logging_config import logger
from logs.db_logger import log_error_to_db

def parse_interval(interval_str):
    match = re.match(r'^(\d+)(s|m|h)$', interval_str.strip().lower())
    if not match:
        raise ValueError(f"Invalid interval format: {interval_str}")
    value, unit = match.groups()
    value = int(value)
    return value * {'s': 1, 'm': 60, 'h': 3600}[unit]

def sensor_loop(app):
    interval = parse_interval(SENSOR_LOG_INTERVAL)
    logger.info(f"[SensorLogger] Logging every {interval} seconds")

    while True:
        try:
            with app.app_context():
                data = read_sensors()
                save_sensor_data(data)
                #logger.info(f"[SensorLogger] Saved: {data}")
        except Exception as e:
            logger.exception("[SensorLogger] Error while logging sensor data")
            log_error_to_db("sensor_logger.py", e)
        time.sleep(interval)

def start_sensor_logger(app):
    if ENABLE_SENSOR_LOGGER:
        thread = threading.Thread(target=sensor_loop, args=(app,), daemon=True)
        thread.start()
        logger.info("[SensorLogger] Background logger started")
