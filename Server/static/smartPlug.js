export function setupSmartPlug() {
  const apiUrl = `${window.location.protocol}//${window.location.hostname}:5000`;

  async function updateSmartPlugStatus() {
    try {
      const res = await fetch(`${apiUrl}/smartplug/status`);
      const data = await res.json();
      document.getElementById("smartPlugStatus").textContent = data.status ? "ON" : "OFF";
      document.getElementById("smartPlugBtn").textContent = data.status ? "Turn OFF" : "Turn ON";
    } catch (e) {
      document.getElementById("smartPlugStatus").textContent = "Error";
    }
  }

  async function toggleSmartPlug() {
    const current = document.getElementById("smartPlugBtn").textContent.includes("OFF");
    const action = current ? "off" : "on";
    try {
      await fetch(`${apiUrl}/smartplug/toggle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action })
      });
      updateSmartPlugStatus();
    } catch (e) {
      document.getElementById("smartPlugStatus").textContent = "Error";
    }
  }

  document.getElementById("smartPlugBtn").addEventListener("click", toggleSmartPlug);
  updateSmartPlugStatus();
}