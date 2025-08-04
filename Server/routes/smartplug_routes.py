from flask import Blueprint, jsonify, request
from smart import get_status, turn_on, turn_off, get_device_info

smartplug_bp = Blueprint('smartplug', __name__)

@smartplug_bp.route('/smartplug/fullstatus', methods=['GET'])
def smartplug_fullstatus():
    try:
        device = get_device_info()
        status = get_status()
        return jsonify({"status": status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@smartplug_bp.route('/smartplug/status', methods=['GET'])
def smartplug_status():
    try:
        response = get_status()
        if not response.get("success"):
            raise Exception("Failed to get status from Tuya API")
        
        # Find the switch_1 value
        for item in response["result"]:
            if item["code"] == "switch_1":
                return jsonify({"status": item["value"]})
        
        # If switch_1 not found
        return jsonify({"error": "switch_1 code not found"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@smartplug_bp.route('/smartplug/toggle', methods=['POST'])
def smartplug_toggle():
    try:
        data = request.get_json()
        action = data.get('action')
        if action == 'on':
            result = turn_on()
        elif action == 'off':
            result = turn_off()
        else:
            return jsonify({"error": "Invalid action"}), 400
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500