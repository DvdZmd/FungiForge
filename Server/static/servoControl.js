// Servo control logic for pan and tilt

const apiUrl = `${window.location.protocol}//${window.location.hostname}:5000`;
let servo_pan = 90;
let servo_tilt = 90;

/**
 * Update the displayed servo positions in the UI.
 */
function updateServoDisplay() {
  document.getElementById("servo_pan_value").textContent = servo_pan;
  document.getElementById("servo_tilt_value").textContent = servo_tilt;
}

/**
 * Move the servo to the specified pan and tilt angles.
 * @param {number} pan - Pan angle (0-180)
 * @param {number} tilt - Tilt angle (90-160)
 */
async function moveServo(pan, tilt) {
  if (!window.read_servos) return;

  servo_tilt = Math.max(90, Math.min(160, tilt));
  servo_pan = Math.max(0, Math.min(180, pan));

  try {
    const response = await fetch(`${apiUrl}/bluetooth/servos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pan: servo_pan, tilt: servo_tilt }),
    });
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    updateServoDisplay();
  } catch (error) {
    console.error("Error moving servo:", error);
  }
}

/**
 * Fetch the current servo position from the server.
 */
async function fetchServoPosition() {
  try {
    const response = await fetch(`${apiUrl}/bluetooth/servos`);
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
    const data = await response.json();
    servo_pan = data.pan;
    servo_tilt = data.tilt;
    updateServoDisplay();
  } catch (error) {
    console.error("Error fetching servo position:", error);
  }
}

export {servo_pan, servo_tilt, moveServo, fetchServoPosition, updateServoDisplay };