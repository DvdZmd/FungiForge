import { servo_pan, servo_tilt, moveServo, fetchServoPosition, updateServoDisplay } from './servoControl.js';
import { fetchSensorData } from './sensorData.js';
import { setupTimelapse } from './timelapse.js';
import { setupCameraControls } from './camera.js';
import { setupSmartPlug } from './smartPlug.js';


window.onload = () => {
  // Bind UI events for servo control
  document.getElementById("btn-up").addEventListener("click", () => moveServo(servo_pan, servo_tilt + 5));
  document.getElementById("btn-down").addEventListener("click", () => moveServo(servo_pan, servo_tilt - 5));
  document.getElementById("btn-left").addEventListener("click", () => moveServo(servo_pan - 5, servo_tilt));
  document.getElementById("btn-right").addEventListener("click", () => moveServo(servo_pan + 5, servo_tilt));

  // Setup other modules
  setupTimelapse();
  setupCameraControls();
  setupSmartPlug();

  // Periodic updates
  if (window.read_i2c_sensors) setInterval(fetchSensorData, 500);
  if (window.read_servos) setInterval(fetchServoPosition, 200);
};