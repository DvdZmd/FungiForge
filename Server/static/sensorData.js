const apiUrl = `${window.location.protocol}//${window.location.hostname}:5000`;

/**
 * Fetches the latest sensor data from the server and updates the UI.
 * Handles temperature, humidity, and soil moisture readings.
 */
export async function fetchSensorData() {
  try {
    const response = await fetch(`${apiUrl}/get_sensors`);
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`);

    const data = await response.json();

    // Update UI elements with sensor values
    document.getElementById("temperature_dht").textContent = data.temperature_dht;
    document.getElementById("humidity").textContent = data.humidity;
    document.getElementById("temperature_ds18b20").textContent = data.temperature_ds18b20;
    document.getElementById("soil_moisture").textContent = data.soil_moisture;
  } catch (error) {
    console.error("Error fetching sensor data:", error);
    // Optionally, update the UI to indicate an error
  }
}