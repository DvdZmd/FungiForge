const apiUrl = `${window.location.protocol}//${window.location.hostname}:5000`;

/**
 * Sets up camera controls and event listeners.
 * Handles toggling the camera on/off and changing rotation.
 */
export function setupCameraControls() {
  let cameraEnabled = true;

  // Toggle camera on/off
  document.getElementById("toggleCameraBtn").addEventListener("click", async () => {
    try {
      const res = await fetch(`${apiUrl}/toggle_camera`, {
        method: "POST"
      });
      const data = await res.json();
      cameraEnabled = data.enabled;
      document.getElementById("toggleCameraBtn").textContent = cameraEnabled
        ? "Turn Camera Off"
        : "Turn Camera On";
    } catch (error) {
      console.error("Error toggling camera:", error);
      // Optionally update UI to indicate error
    }
  });

  // Change camera rotation
  document.getElementById('rotationSelect').addEventListener('change', async function () {
    const rotation = parseInt(this.value);
    try {
      const res = await fetch(`${apiUrl}/set_rotation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ rotation })
      });
      const data = await res.json();
      // Optionally update UI or show a message
    } catch (error) {
      console.error("Error setting rotation:", error);
    }
  });

  // Set video feed source
  document.getElementById("videoFeed").src = `${apiUrl}/video_feed`;

  // Change stream resolution
  document.getElementById('streamResolution').addEventListener('change', function() {
    const resolution = this.value;
    fetch(`${apiUrl}/set_stream_resolution`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resolution: resolution })
    })
    .then(response => response.json())
    .then(data => {
        // Optionally update UI or reload stream
        // For example, force reload by updating src with a timestamp
        // document.getElementById('videoFeed').src = `${apiUrl}/video_feed?${Date.now()}`;
    })
    .catch(error => {
      console.error("Error changing stream resolution:", error);
    });
  });
}