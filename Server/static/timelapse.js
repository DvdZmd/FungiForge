const apiUrl = `${window.location.protocol}//${window.location.hostname}:5000`;

/**
 * Sets up the timelapse controls and event listeners.
 * Handles starting/stopping timelapse and capturing images.
 */
export function setupTimelapse() {
  let timelapseActive = false;

  async function initTimelapseStatus() {
    try {
      const res = await fetch(`${apiUrl}/timelapse_status`);
      const data = await res.json();

      console.log("timelapse_status", data);

      timelapseActive = data.running;

      document.getElementById("timelapseToggleBtn").textContent = timelapseActive
        ? "Stop Timelapse"
        : "Start Timelapse";

      document.getElementById("timelapseStatus").textContent = timelapseActive
        ? `⏳ Running every ${data.interval_minutes} min at ${data.width}x${data.height}`
        : "⏸️ Timelapse is stopped";

      // Optionally pre-fill form
      if (data.interval_minutes) {
        document.getElementById("timelapseInterval").value = data.interval_minutes;
      }
      if (data.width && data.height) {
        document.getElementById("timelapseResolution").value = `${data.width}x${data.height}`;
      }

    } catch (error) {
      console.error("Failed to fetch timelapse status:", error);
      document.getElementById("timelapseStatus").textContent = "❌ Unable to check timelapse status";
    }
  }


  // Load status on init
  initTimelapseStatus();


  // Timelapse toggle button
  document.getElementById("timelapseToggleBtn").addEventListener("click", async () => {
    const interval = parseInt(document.getElementById("timelapseInterval").value);
    const [width, height] = document
      .getElementById("timelapseResolution").value
      .split("x")
      .map(Number);

    try {
      const response = await fetch(`${apiUrl}/timelapse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          action: timelapseActive ? "stop" : "start",
          interval_minutes: interval,
          width,
          height
        })
      });

      const data = await response.json();
      document.getElementById("timelapseStatus").textContent = data.message;

      timelapseActive = !timelapseActive;
      document.getElementById("timelapseToggleBtn").textContent = timelapseActive
        ? "Stop Timelapse"
        : "Start Timelapse";
    } catch (error) {
      console.error("Error toggling timelapse:", error);
      document.getElementById("timelapseStatus").textContent = "❌ Error communicating with server";
    }
  });

  // 📸 Capture Still Image
  document.getElementById("captureBtn").addEventListener("click", async () => {
    const resolutionValue = document.getElementById("pictureResolution").value;
    const [width, height] = resolutionValue.split("x").map(Number);

    try {
      const response = await fetch(`${apiUrl}/capture_image?width=${width}&height=${height}&download=true`);
      if (!response.ok) throw new Error(`HTTP error: ${response.status}`);

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `image_${width}x${height}.jpg`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      document.getElementById("captureStatus").textContent = `✅ Downloaded image at ${width}x${height}`;
    } catch (error) {
      console.error("Download error:", error);
      document.getElementById("captureStatus").textContent = "❌ Error downloading image";
    }
  });
}