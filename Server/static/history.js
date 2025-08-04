let currentPage = 1;

async function fetchHistory(page = 1) {
  const params = new URLSearchParams();
  params.append("page", page);
  params.append("per_page", 10);

  // Read filters
  const startDate = document.getElementById("startDate").value;
  const endDate = document.getElementById("endDate").value;
  const minTempAir = document.getElementById("minTempAir").value;
  const maxTempAir = document.getElementById("maxTempAir").value;
  const minMoisture = document.getElementById("minMoisture").value;
  const maxMoisture = document.getElementById("maxMoisture").value;

  if (startDate) params.append("start_date", startDate);
  if (endDate) params.append("end_date", endDate);
  if (minTempAir) params.append("min_temp_air", minTempAir);
  if (maxTempAir) params.append("max_temp_air", maxTempAir);
  if (minMoisture) params.append("min_moisture", minMoisture);
  if (maxMoisture) params.append("max_moisture", maxMoisture);

  const res = await fetch(`/readings_history?${params.toString()}`);
  const data = await res.json();

  renderResults(data.readings);
  renderPagination(data.page, data.pages);
  currentPage = data.page;
}

function renderResults(readings) {
  const container = document.getElementById("historyResults");
  if (readings.length === 0) {
    container.innerHTML = "<p>No readings found.</p>";
    return;
  }

  let html = "<table><thead><tr><th>Timestamp</th><th>Temp Air</th><th>Humidity</th><th>Temp Sub</th><th>Moisture</th></tr></thead><tbody>";

  for (const r of readings) {
    html += `<tr>
      <td>${new Date(r.timestamp).toLocaleString()}</td>
      <td>${r.temperature_air}°C</td>
      <td>${r.humidity_air}%</td>
      <td>${r.temperature_substrate}°C</td>
      <td>${r.moisture_substrate}</td>
    </tr>`;
  }

  html += "</tbody></table>";
  container.innerHTML = html;
}

function renderPagination(current, total) {
  const container = document.getElementById("paginationControls");
  container.innerHTML = "";

  if (total <= 1) return;

  if (current > 1) {
    const prev = document.createElement("button");
    prev.textContent = "⬅️ Prev";
    prev.onclick = () => fetchHistory(current - 1);
    container.appendChild(prev);
  }

  container.innerHTML += ` <strong>Page ${current} of ${total}</strong> `;

  if (current < total) {
    const next = document.createElement("button");
    next.textContent = "Next ➡️";
    next.onclick = () => fetchHistory(current + 1);
    container.appendChild(next);
  }
}

// Bind buttons
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("loadHistoryBtn").addEventListener("click", () => fetchHistory(1));
  document.getElementById("applyFiltersBtn").addEventListener("click", () => fetchHistory(1));
});
