from tuya_iot import TuyaOpenAPI, AuthType
from config import SmartPlugConfig

config = SmartPlugConfig()

openapi = TuyaOpenAPI(config.api_endpoint, config.access_id, config.access_key, AuthType.SMART_HOME)
openapi.connect(config.username, config.password, config.country_code, config.api_schema)

def get_device_info():
    return openapi.get(f"/v1.0/devices/{config.device_id}")

def get_status():
    return openapi.get(f"/v1.0/devices/{config.device_id}/status")


def turn_on():
    return openapi.post(f"/v1.0/devices/{config.device_id}/commands", {
        "commands": [{"code": "switch_1", "value": True}]
    })

def turn_off():
    return openapi.post(f"/v1.0/devices/{config.device_id}/commands", {
        "commands": [{"code": "switch_1", "value": False}]
    })