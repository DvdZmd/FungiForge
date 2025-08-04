const apiUrl = `${window.location.protocol}//${window.location.hostname}:5000`;

/**
 * Sets up the face table controls and event listeners.
 * Handles loading and displaying face data from the server.
 */
export function setupFaceTable() {
  document.getElementById("loadFacesBtn").addEventListener("click", () => {
    fetch(`${apiUrl}/faces`)
      .then(response => response.json())
      .then(data => {
        const tableBody = document.querySelector("#faces-table tbody");
        tableBody.innerHTML = ""; // Clear previous content

        data.forEach(face => {
          const row = document.createElement("tr");

          // ID cell
          const idCell = document.createElement("td");
          idCell.textContent = face[0];
          row.appendChild(idCell);

          // Encoding cell (truncated for readability)
          const encodingCell = document.createElement("td");
          encodingCell.textContent = face[1].substring(0, 50) + "...";
          row.appendChild(encodingCell);

          // Timestamp cell
          const timestampCell = document.createElement("td");
          timestampCell.textContent = face[2];
          row.appendChild(timestampCell);

          // Count cell
          const countCell = document.createElement("td");
          countCell.textContent = face[3];
          row.appendChild(countCell);

          tableBody.appendChild(row);
        });
      })
      .catch(error => {
        console.error("Error fetching faces:", error);
        // Optionally update UI to indicate error
      });
  });
}