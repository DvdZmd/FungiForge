# camera/timelapse.py
import os
import cv2
from datetime import datetime
from threading import Event, Thread
from config import AVAILABLE_RESOLUTIONS, FRAME_RATE, NOISE_REDUCTION_MODE, TIMELAPSE_DIR
from camera.picam import picam2, video_config
from database.models import TimelapseConfig, db
from logs.logging_config import logger


timelapse_thread = None
timelapse_stop_event = Event()

current_timelapse_config = {
    "interval_minutes": None,
    "width": None,
    "height": None
}

def is_timelapse_running():
    global timelapse_thread
    return timelapse_thread is not None and timelapse_thread.is_alive()

def save_timelapse_config(interval_minutes, width, height, running):
    config = TimelapseConfig.query.first()
    if not config:
        config = TimelapseConfig(
            interval_minutes=interval_minutes,
            width=width,
            height=height,
            is_running=running,
            updated_at=datetime.utcnow()
        )
        db.session.add(config)
    else:
        config.interval_minutes = interval_minutes
        config.width = width
        config.height = height
        config.is_running = running
        config.updated_at = datetime.utcnow()

    db.session.commit()


def start_timelapse(interval_minutes, width, height):
    global timelapse_thread, timelapse_stop_event, current_timelapse_config

    if timelapse_thread and timelapse_thread.is_alive():
        return False  # Already running

    current_timelapse_config.update({
        "interval_minutes": interval_minutes,
        "width": width,
        "height": height
    })

    timelapse_stop_event.clear()
    timelapse_thread = Thread(
        target=_timelapse_worker,
        args=(interval_minutes, width, height),
        daemon=True
    )
    timelapse_thread.start()
    save_timelapse_config(interval_minutes, width, height, True)

    return True

def load_saved_config():
    global current_timelapse_config
    config = TimelapseConfig.query.first()
    if config and config.is_running:
        current_timelapse_config.update({
            "interval_minutes": config.interval_minutes,
            "width": config.width,
            "height": config.height
        })
        print(f"[Timelapse] Loaded config: every {config.interval_minutes}m at {config.width}x{config.height}")
        start_timelapse(
            config.interval_minutes,
            config.width,
            config.height
        )

def get_timelapse_config():
    config = TimelapseConfig.query.first()
    if config:
        return {
            "running": config.is_running,
            "interval_minutes": config.interval_minutes,
            "width": config.width,
            "height": config.height,
            "last_updated": config.updated_at.isoformat()
        }
    return {
        "running": False,
        "interval_minutes": None,
        "width": None,
        "height": None
    }


def stop_timelapse():
    global timelapse_thread, timelapse_stop_event

    if timelapse_thread and timelapse_thread.is_alive():
        timelapse_stop_event.set()
        timelapse_thread.join()
        current_timelapse_config.update({
            "interval_minutes": None,
            "width": None,
            "height": None
        })
        save_timelapse_config(0, 0, 0, False)
        return True
    return False

def _timelapse_worker(interval_minutes, width, height):
    while not timelapse_stop_event.is_set():
        try:
            resolution = (width, height)

            if resolution not in AVAILABLE_RESOLUTIONS:
                print(f"[Timelapse] Unsupported resolution: {resolution}")
                break

            # Reconfigure for still capture
            picam2.stop()
            controls = {
                "FrameRate": FRAME_RATE,
                "NoiseReductionMode": NOISE_REDUCTION_MODE
            }

            if "AfMode" in picam2.camera_controls:
                controls["AfMode"] = 2

            still_config = picam2.create_video_configuration(
                main={"size": resolution},
                controls=controls
            )
            picam2.configure(still_config)
            picam2.start()

            image = picam2.capture_array()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            date_folder = datetime.now().strftime("%Y-%m-%d")
            save_folder = os.path.join(TIMELAPSE_DIR, date_folder)
            os.makedirs(save_folder, exist_ok=True)

            timestamp = datetime.now().strftime("%H-%M-%S")
            filepath = os.path.join(save_folder, f"{timestamp}.jpg")

            cv2.imwrite(filepath, image)
            print(f"[Timelapse] Saved: {filepath}")

        except Exception as e:
            logger.exception("[Timelapse] Error capturing image")

        finally:
            try:
                picam2.stop()
                picam2.configure(video_config)
                picam2.start()
            except Exception as e:
                logger.exception("[Timelapse] Error restoring camera configuration")

        if timelapse_stop_event.wait(interval_minutes * 60):
            break

    print("[Timelapse] Stopped")
