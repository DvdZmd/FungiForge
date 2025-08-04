import struct
import threading
from smbus2 import SMBus, i2c_msg
from config import ARDUINO_SENSORS
from database.models import SensorReading, db

i2c_lock = threading.Lock()
bus = SMBus(1)

def read_sensors():
    with i2c_lock:
        try:
            # Assuming the Arduino sends data in the format: <temperature_dht: float, humidity: float, temperature_ds18b20: float, soil_moisture: uint16>
            read = i2c_msg.read(ARDUINO_SENSORS, 14)
            bus.i2c_rdwr(read)
            raw_data = bytes(list(read))

            # Unpack the raw data
            temperature_dht, humidity, temperature_ds18b20, soil_moisture = struct.unpack('<fffH', raw_data)
        except Exception as e:
            print(f"[I2C ERROR] Failed to read sensor data: {e}")
            temperature_dht, humidity, temperature_ds18b20, soil_moisture = 0.0, 0.0, 0.0, 0

    sensor_data = {
        "temperature_dht": round(temperature_dht, 2),
        "humidity": round(humidity, 2),
        "temperature_ds18b20": round(temperature_ds18b20, 2),
        "soil_moisture": soil_moisture
    }

    return sensor_data

def save_sensor_data(sensor_data):
    try:
        new_reading = SensorReading(
            temperature_air=sensor_data["temperature_dht"],
            humidity_air=sensor_data["humidity"],
            temperature_substrate=sensor_data["temperature_ds18b20"],
            moisture_substrate=sensor_data["soil_moisture"]
        )
        db.session.add(new_reading)
        db.session.commit()
    except Exception as e:
        print(f"[DB ERROR] Failed to store sensor reading: {e}")
