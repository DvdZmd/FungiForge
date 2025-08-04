from picamera2 import Picamera2, Preview
from config import FRAME_RATE, NOISE_REDUCTION_MODE, CAMERA_WIDTH, CAMERA_HEIGHT
from logs.logging_config import logger

picam2 = None
video_config = None

try:
    picam2 = Picamera2()
    
    controls = {
        "FrameRate": FRAME_RATE,
        "NoiseReductionMode": NOISE_REDUCTION_MODE
    }

    # Check if autofocus is supported
    available_controls = picam2.camera_controls
    if "AfMode" in available_controls:
        controls["AfMode"] = 2  # Continuous autofocus

    video_config = picam2.create_video_configuration(
        main={"size": (CAMERA_WIDTH, CAMERA_HEIGHT)},  # <-- here's the size
        controls=controls
    )

    picam2.configure(video_config)
    picam2.start()
    logger.info("[Camera] Cámara iniciada correctamente.")

except Exception as e:
    logger.exception("[Camera] No se pudo iniciar la cámara")