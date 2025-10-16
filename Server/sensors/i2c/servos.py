import threading
from smbus2 import SMBus, i2c_msg
from config import ARDUINO_PAN_TILT

i2c_lock = threading.Lock()
bus = SMBus(1)

def get_current_pan_tilt():
    with i2c_lock:
        try:
            read = i2c_msg.read(ARDUINO_PAN_TILT, 2)
            bus.i2c_rdwr(read)
            data = list(read)
            return {"pan": data[0], "tilt": data[1]}
        except Exception as e:
            print(f"[I2C ERROR] Failed to read servo angles: {e}")
            return {"pan": 0, "tilt": 0}

def set_pan_tilt(pan, tilt):
    pan = max(0, min(180, int(pan)))
    tilt = max(90, min(160, int(tilt)))
    with i2c_lock:
        try:
            bus.write_i2c_block_data(ARDUINO_PAN_TILT, 0x00, [pan, tilt])
            return {"pan": pan, "tilt": tilt}
        except Exception as e:
            print(f"[I2C ERROR] Failed to send servo command: {e}")
            return {"pan": 0, "tilt": 0}
