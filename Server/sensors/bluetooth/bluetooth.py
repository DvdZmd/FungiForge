# sensores/bluetooth.py
import asyncio
import threading
import struct
import time
import logging
from copy import deepcopy

from bleak import BleakClient, BleakScanner, BleakError

from flask import Blueprint, jsonify, request, current_app

# Importa tu config y modelos DB (ajusta el path si es necesario)
from config import (
    ESP32_BLE_NAME,
    ESP32_BLE_ADDRESS,
    ESP32_SENSOR_CHAR_UUID,
    ESP32_SERVO_CHAR_UUID,
    ESP32_RECONNECT_INTERVAL,
)
from database.models import SensorReading, db

logger = logging.getLogger("bluetooth")
logger.setLevel(logging.DEBUG)

# --- Clase cliente BLE que mantiene conexión y caché ---
class ESP32BLEClient:
    def __init__(
        self,
        name=None,
        address=None,
        sensor_uuid=None,
        servo_uuid=None,
        reconnect_interval=5,
    ):
        self.name = name
        self.address = address
        self.sensor_uuid = sensor_uuid
        self.servo_uuid = servo_uuid
        self.reconnect_interval = reconnect_interval

        self._client = None
        self._loop = None
        self._thread = None
        self._stop_event = threading.Event()

        self._lock = threading.Lock()
        # Cachés compartidos por rutas
        self._sensor_data = {
            "temperature_dht": 0.0,
            "humidity": 0.0,
            "temperature_ds18b20": 0.0,
            "soil_moisture": 0,
            "last_update": 0.0,
        }
        self._pan_tilt = {"pan": 0, "tilt": 0, "last_update": 0.0}

        self._connected_event = threading.Event()

    # ----- Notif handlers -----
    def _sensor_notification(self, sender: int, data: bytearray):
        # Espera 14 bytes con packing '<fffH'
        try:
            if len(data) < 14:
                logger.warning(f"Sensor notification too short: {len(data)} bytes")
                return
            temperature_dht, humidity, temperature_ds18b20, soil_moisture = struct.unpack("<fffH", data[:14])
            with self._lock:
                self._sensor_data.update({
                    "temperature_dht": round(temperature_dht, 2),
                    "humidity": round(humidity, 2),
                    "temperature_ds18b20": round(temperature_ds18b20, 2),
                    "soil_moisture": int(soil_moisture),
                    "last_update": time.time(),
                })
            logger.debug(f"Sensor updated: {self._sensor_data}")
        except Exception as e:
            logger.exception(f"Failed to parse sensor notification: {e}")

    def _servo_notification(self, sender: int, data: bytearray):
        try:
            if len(data) < 2:
                logger.warning("Servo notification too short")
                return
            pan = int(data[0])
            tilt = int(data[1])
            with self._lock:
                self._pan_tilt.update({"pan": pan, "tilt": tilt, "last_update": time.time()})
            logger.debug(f"Pan/Tilt updated: {self._pan_tilt}")
        except Exception as e:
            logger.exception(f"Failed to parse servo notification: {e}")

    # ----- Async connect and subscribe -----
    async def _connect_and_subscribe(self):
        # Si no tenemos address, buscamos por nombre
        address = self.address
        if not address:
            logger.info(f"Buscando dispositivo BLE con nombre '{self.name}'...")
            devices = await BleakScanner.discover(timeout=5.0)
            for d in devices:
                if d.name and self.name and d.name == self.name:
                    address = d.address
                    logger.info(f"Encontrado {d.name} @ {address}")
                    break
            if not address:
                raise BleakError(f"Device '{self.name}' no encontrado por BLE")

        logger.info(f"Conectando a {address} ...")
        client = BleakClient(address)
        await client.connect()
        if not client.is_connected:
            raise BleakError("No se pudo conectar")

        # Subscribe notifications
        if self.sensor_uuid:
            try:
                await client.start_notify(self.sensor_uuid, self._sensor_notification)
                logger.info(f"Subscribed to sensor notifications {self.sensor_uuid}")
            except Exception as e:
                logger.exception(f"Failed to start_notify sensor: {e}")

        if self.servo_uuid:
            try:
                await client.start_notify(self.servo_uuid, self._servo_notification)
                logger.info(f"Subscribed to servo notifications {self.servo_uuid}")
            except Exception as e:
                logger.exception(f"Failed to start_notify servo: {e}")

        self._client = client
        self._connected_event.set()

    async def _client_loop(self):
        # Intenta conectar y si se desconecta, reintenta
        while not self._stop_event.is_set():
            try:
                await self._connect_and_subscribe()
                # loop de mantenimiento
                while not self._stop_event.is_set():
                    if self._client is None or not self._client.is_connected:
                        raise BleakError("Desconectado")
                    await asyncio.sleep(1.0)
            except Exception as e:
                logger.warning(f"BLE client disconnected / error: {e}")
                self._connected_event.clear()
                try:
                    if self._client:
                        await self._client.disconnect()
                except Exception:
                    pass
                self._client = None
                await asyncio.sleep(self.reconnect_interval)

    # ----- Thread management -----
    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_loop_thread, daemon=True, name="ESP32BLEClientThread")
        self._thread.start()
        logger.info("ESP32BLEClient thread started")

    def _run_loop_thread(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._client_loop())
        finally:
            pending = asyncio.all_tasks(loop=self._loop)
            for t in pending:
                t.cancel()
            self._loop.close()
            logger.info("ESP32 loop closed")

    def stop(self):
        self._stop_event.set()
        self._connected_event.clear()
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=2)

    # ----- Sync API para rutas Flask -----
    def read_sensors(self):
        with self._lock:
            return deepcopy(self._sensor_data)

    def save_sensor_data(self, sensor_data):
        # Igual que tu sensors.save_sensor_data
        try:
            new_reading = SensorReading(
                temperature_air=sensor_data["temperature_dht"],
                humidity_air=sensor_data["humidity"],
                temperature_substrate=sensor_data["temperature_ds18b20"],
                moisture_substrate=sensor_data["soil_moisture"]
            )
            db.session.add(new_reading)
            db.session.commit()
            return True
        except Exception as e:
            logger.exception(f"[DB ERROR] Failed to store sensor reading: {e}")
            try:
                db.session.rollback()
            except Exception:
                pass
            return False

    def get_current_pan_tilt(self):
        with self._lock:
            return deepcopy(self._pan_tilt)

    def set_pan_tilt(self, pan: int, tilt: int, timeout: float = 5.0):
        # Clamp like en servos.py
        pan = max(0, min(180, int(pan)))
        tilt = max(90, min(160, int(tilt)))
        if not self._connected_event.is_set() or not self._client:
            logger.warning("BLE client not connected - cannot set pan/tilt")
            return {"pan": 0, "tilt": 0}

        # Llamamos a corutina de escritura en el loop del thread
        async def _write():
            try:
                await self._client.write_gatt_char(self.servo_uuid, bytes([pan, tilt]), response=True)
                logger.debug(f"Wrote pan/tilt {pan},{tilt}")
                # también actualizamos caché local
                with self._lock:
                    self._pan_tilt.update({"pan": pan, "tilt": tilt, "last_update": time.time()})
                return True
            except Exception as e:
                logger.exception(f"Failed to write pan/tilt: {e}")
                return False

        try:
            future = asyncio.run_coroutine_threadsafe(_write(), self._loop)
            ok = future.result(timeout=timeout)
            if ok:
                return {"pan": pan, "tilt": tilt}
            else:
                return {"pan": 0, "tilt": 0}
        except Exception as e:
            logger.exception(f"Error running write coroutine: {e}")
            return {"pan": 0, "tilt": 0}


# --- Crear instancia (no arranca la conexión hasta que se llame .start()) ---
ble_client = ESP32BLEClient(
    name=ESP32_BLE_NAME,
    address=ESP32_BLE_ADDRESS,
    sensor_uuid=ESP32_SENSOR_CHAR_UUID,
    servo_uuid=ESP32_SERVO_CHAR_UUID,
    reconnect_interval=ESP32_RECONNECT_INTERVAL,
)

# --- Flask blueprint con rutas equivalentes a las I2C actuales ---
bluetooth_bp = Blueprint("bluetooth", __name__)

@bluetooth_bp.route("/get_sensors", methods=["GET"])
def route_get_sensors():
    data = ble_client.read_sensors()
    # Retornar el mismo formato que tu sensors.read_i2c_sensors
    return jsonify({
        "temperature_dht": data["temperature_dht"],
        "humidity": data["humidity"],
        "temperature_ds18b20": data["temperature_ds18b20"],
        "soil_moisture": data["soil_moisture"],
        "last_update": data.get("last_update", 0)
    })

@bluetooth_bp.route("/sensors/save", methods=["POST"])
def route_save_sensors():
    # Si quieres dejar que la UI llame a /sensors y luego /sensors/save; o también permitir enviar payload
    payload = request.json or {}
    if payload:
        ok = ble_client.save_sensor_data(payload)
    else:
        ok = ble_client.save_sensor_data(ble_client.read_sensors())
    return jsonify({"ok": bool(ok)})

@bluetooth_bp.route("/servos", methods=["GET"])
def route_get_servos():
    return jsonify(ble_client.get_current_pan_tilt())

@bluetooth_bp.route("/servos", methods=["POST"])
def route_set_servos():
    payload = request.json or {}
    pan = payload.get("pan")
    tilt = payload.get("tilt")
    if pan is None or tilt is None:
        return jsonify({"error": "missing pan or tilt"}), 400
    result = ble_client.set_pan_tilt(pan, tilt)
    return jsonify(result)

# --- Helper init function para llamar desde tu app factory ---
def init_ble(app=None):
    """
    Registra blueprint y arranca el cliente BLE.
    Llamar desde tu create_app() después de configurar app.
    """
    if app:
        app.register_blueprint(bluetooth_bp, url_prefix="/bluetooth")
        # Iniciar el hilo BLE en background (no bloqueante)
        ble_client.start()
        app.logger.info("Bluetooth blueprint registered and BLE client started")
    else:
        # Si no pasas app, registra pero no inicia (útil para tests)
        pass
