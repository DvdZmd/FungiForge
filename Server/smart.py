import logging
from tuya_iot import TuyaOpenAPI, AuthType
import time
from config import SMARTPLUG_DEVICE_ID, SMARTPLUG_IP, SMARTPLUG_LOCAL_KEY, SMARTPLUG_PROTOCOL_VERSION

logging.basicConfig(level=logging.DEBUG)


ACCESS_ID = ""
ACCESS_KEY = ""
API_ENDPOINT = ""
DEVICE_ID = ""
USERNAME = ""
PASSWORD = ""
COUNTRY_CODE = ""
API_SCHEMA = ""

openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY, AuthType.SMART_HOME)
response = openapi.connect(USERNAME, PASSWORD, COUNTRY_CODE, API_SCHEMA)
response = openapi.post(
    "/v1.0/iot-01/associated-users/actions/authorized-login",
    {
        "username": USERNAME,
        "password": PASSWORD,
        "country_code": COUNTRY_CODE,
        "schema": API_SCHEMA
    }
)

print("Login response:")
print(response)
# Probar acceso al dispositivo
result = openapi.get(f"/v1.0/devices/{DEVICE_ID}/status")
print("Device status:")
print(result)

def get_device_info():
    openapi.connect()
    return openapi.get("/v1.0/iot-03/devices/{}".format(DEVICE_ID))

def get_status():
    openapi.connect()
    return openapi.get("/v1.0/iot-03/devices/{}/status".format(DEVICE_ID))


def turn_on():
    openapi.connect()
    return openapi.post("/v1.0/iot-03/devices/{}/commands".format(DEVICE_ID), {
        "commands": [{"code": "switch_1", "value": True}]
    })

def turn_off():
    openapi.connect()
    return openapi.post("/v1.0/iot-03/devices/{}/commands".format(DEVICE_ID), {
        "commands": [{"code": "switch_1", "value": False}]
    })