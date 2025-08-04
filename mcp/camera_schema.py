# mcp/camera_schema.py
from modelcontext.host import Schema, Function
from modelcontext.types import String, Integer, Bool

# Import your real camera logic
from server.camera.picam import (
    start_preview, stop_preview,
    capture_image, set_resolution,
    get_camera_status
)
from server.camera.timelapse import start_timelapse, stop_timelapse

@Function()
def mcp_start_preview() -> String:
    start_preview()
    return "Camera preview started."

@Function()
def mcp_stop_preview() -> String:
    stop_preview()
    return "Camera preview stopped."

@Function(name="capture_image")
def mcp_capture_image(filename: String = "capture.jpg") -> String:
    path = capture_image(filename)
    return f"Image captured and saved at: {path}"

@Function()
def mcp_set_resolution(resolution: String) -> String:
    success = set_resolution(resolution)
    return "Resolution set." if success else "Failed to set resolution."

@Function()
def mcp_get_camera_status() -> String:
    return get_camera_status()  # Example: "Camera is idle"

@Function()
def mcp_start_timelapse(interval_sec: Integer = 300, resolution: String = "1920x1080") -> String:
    start_timelapse(interval_sec, resolution)
    return f"Timelapse started every {interval_sec} seconds at {resolution}."

@Function()
def mcp_stop_timelapse() -> String:
    stop_timelapse()
    return "Timelapse stopped."

camera_schema = Schema(
    name="CameraControl",
    description="Functions to control the camera and timelapse",
    functions=[
        mcp_start_preview,
        mcp_stop_preview,
        mcp_capture_image,
        mcp_set_resolution,
        mcp_get_camera_status,
        mcp_start_timelapse,
        mcp_stop_timelapse
    ]
)
