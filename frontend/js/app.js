const API = "/api";
const HARARE_CENTER = [-17.8292, 31.0537];

let map;
const markers = { cameras: [], sensors: [], incidents: [], units: [] };

async function fetchJSON(path, options = {}) {
  const res = await fetch(API + path, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function initMap() {
  map = L.map("map").setView(HARARE_CENTER, 13);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap",
    maxZoom: 18,
  }).addTo(map);
}

function clearLayer(layer) {
  markers[layer].forEach((m) => map.removeLayer(m));
  markers[layer] = [];
}

function addMarker(layer, lat, lng, color, popup) {
  const icon = L.divIcon({
    className: "custom-marker",
    html: `<div style="background:${color};width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 0 4px rgba(0,0,0,.5)"></div>`,
    iconSize: [12, 12],
  });
  const m = L.marker([lat, lng], { icon }).addTo(map).bindPopup(popup);
  markers[layer].push(m);
}

function badge(text, cls) {
  return `<span class="badge ${cls}">${text}</span>`;
}

async function loadStats() {
  const s = await fetchJSON("/dashboard/stats");
  document.getElementById("statsGrid").innerHTML = `
    <div class="stat-card"><div class="value">${s.active_incidents}</div><div class="label">Active Incidents</div></div>
    <div class="stat-card"><div class="value">${s.open_alerts}</div><div class="label">Open Alerts</div></div>
    <div class="stat-card"><div class="value">${s.cameras_online}</div><div class="label">Cameras Online</div></div>
    <div class="stat-card"><div class="value">${s.sensors_active}</div><div class="label">Sensors Active</div></div>
    <div class="stat-card"><div class="value">${s.units_available}</div><div class="label">Units Available</div></div>
    <div class="stat-card"><div class="value">${s.citizen_reports_pending}</div><div class="label">Pending Reports</div></div>
  `;
}

async function loadIncidents() {
  const items = await fetchJSON("/incidents");
  const active = items.filter((i) => i.status !== "resolved");
  document.getElementById("incidentList").innerHTML = active
    .map(
      (i) => `
    <div class="list-item" data-lat="${i.latitude}" data-lng="${i.longitude}">
      <div class="title">${i.title}</div>
      <div class="meta">${i.zone} · ${badge(i.priority, i.priority)} ${badge(i.status, i.status)}</div>
    </div>`
    )
    .join("") || "<p class='meta'>No active incidents</p>";

  clearLayer("incidents");
  items.forEach((i) => {
    const color = i.priority === "critical" || i.priority === "high" ? "#ef4444" : "#f59e0b";
    addMarker("incidents", i.latitude, i.longitude, color, `<b>${i.title}</b><br>${i.incident_type}<br>${i.status}`);
  });

  document.querySelectorAll("#incidentList .list-item").forEach((el) => {
    el.onclick = () => map.setView([+el.dataset.lat, +el.dataset.lng], 16);
  });
}

async function loadAlerts() {
  const items = await fetchJSON("/alerts?acknowledged=false");
  document.getElementById("alertList").innerHTML = items
    .map(
      (a) => `
    <div class="list-item">
      <div class="title">${a.message}</div>
      <div class="meta">${a.zone} · ${badge(a.severity, a.severity)}
        <button class="btn secondary" onclick="ackAlert(${a.id})">Ack</button>
      </div>
    </div>`
    )
    .join("") || "<p class='meta'>No open alerts</p>";
}

window.ackAlert = async (id) => {
  await fetchJSON(`/alerts/${id}/acknowledge`, { method: "PATCH" });
  refreshAll();
};

async function loadCameras() {
  const items = await fetchJSON("/cameras");
  document.getElementById("cameraList").innerHTML = items
    .map(
      (c) => `
    <div class="list-item">
      <div class="title">${c.name}</div>
      <div class="meta">${c.zone} · ${c.camera_type} · ${c.status}
        <button class="btn secondary" onclick="analyzeCam(${c.id})">AI Scan</button>
        <button class="btn secondary" onclick="focusMap(${c.latitude},${c.longitude})">Map</button>
      </div>
    </div>`
    )
    .join("");

  clearLayer("cameras");
  items.forEach((c) => {
    const color = c.status === "online" ? "#3b82f6" : "#64748b";
    addMarker("cameras", c.latitude, c.longitude, color, `<b>${c.name}</b><br>${c.camera_type}`);
  });
}

window.analyzeCam = async (id) => {
  const r = await fetchJSON(`/cameras/${id}/analyze`, { method: "POST" });
  alert(r.detected ? `Detection: ${r.message}` : r.message);
  refreshAll();
};

async function loadSensors() {
  const items = await fetchJSON("/sensors");
  document.getElementById("sensorList").innerHTML = items
    .map(
      (s) => `
    <div class="list-item">
      <div class="title">${s.name}</div>
      <div class="meta">${s.sensor_type}: ${s.last_value} ${s.unit}
        <button class="btn secondary" onclick="triggerSensor(${s.id})">Simulate</button>
      </div>
    </div>`
    )
    .join("");

  clearLayer("sensors");
  items.forEach((s) => {
    addMarker("sensors", s.latitude, s.longitude, "#a855f7", `<b>${s.name}</b><br>${s.sensor_type}: ${s.last_value}`);
  });
}

window.triggerSensor = async (id) => {
  const r = await fetchJSON(`/sensors/${id}/trigger`, { method: "POST" });
  alert(r.triggered ? r.message : r.message);
  refreshAll();
};

async function loadTraffic() {
  const items = await fetchJSON("/traffic");
  document.getElementById("trafficList").innerHTML = items
    .map(
      (t) => `
    <div class="list-item">
      <div class="title">${t.intersection}</div>
      <div class="meta">${t.vehicle_count} vehicles · ${badge(t.congestion_level, t.congestion_level)}</div>
    </div>`
    )
    .join("");
}

async function loadUnits() {
  const items = await fetchJSON("/dispatch/units");
  document.getElementById("unitList").innerHTML = items
    .map(
      (u) => `
    <div class="list-item">
      <div class="title">${u.unit_name}</div>
      <div class="meta">${u.agency} · ${u.unit_type} · ${badge(u.status, u.status === "available" ? "low" : "medium")}</div>
    </div>`
    )
    .join("");

  clearLayer("units");
  items.forEach((u) => {
    const color = u.status === "available" ? "#22c55e" : "#64748b";
    addMarker("units", u.latitude, u.longitude, color, `<b>${u.unit_name}</b><br>${u.agency}`);
  });
}

async function loadWatchlist() {
  const items = await fetchJSON("/watchlist");
  document.getElementById("watchlistList").innerHTML = items
    .map(
      (w) => `
    <div class="list-item">
      <div class="title">#${w.id} ${w.full_name}</div>
      <div class="meta">${w.reason} · ${w.has_face_enrolled ? "Face enrolled" : "No face data"}</div>
    </div>`
    )
    .join("");
}

async function loadVehicles() {
  const items = await fetchJSON("/anpr/vehicles");
  const el = document.getElementById("vehicleList");
  if (!el) return;
  el.innerHTML = items
    .map(
      (v) => `
    <div class="list-item">
      <div class="title">${v.plate_number}</div>
      <div class="meta">${v.owner_name} · ${badge(v.status, v.status === "registered" ? "low" : "high")}</div>
    </div>`
    )
    .join("");
}

async function loadHotspots() {
  const items = await fetchJSON("/dashboard/hotspots");
  document.getElementById("hotspotList").innerHTML = items
    .map(
      (h) => `
    <div class="list-item">
      <div class="title">${h.zone}</div>
      <div class="meta">${h.incident_count} incidents · Risk ${h.risk_score}% · ${h.dominant_type}</div>
    </div>`
    )
    .join("");
}

async function loadReports() {
  const items = await fetchJSON("/citizen/reports");
  document.getElementById("reportList").innerHTML = items
    .slice(0, 5)
    .map(
      (r) => `
    <div class="list-item">
      <div class="title">${r.report_type}</div>
      <div class="meta">${r.description.slice(0, 60)}...</div>
    </div>`
    )
    .join("");
}

window.focusMap = (lat, lng) => map.setView([lat, lng], 16);

document.getElementById("btnDispatch").onclick = async () => {
  const incident_id = +document.getElementById("dispatchIncidentId").value;
  const unit_id = +document.getElementById("dispatchUnitId").value;
  try {
    const r = await fetchJSON("/dispatch/assign", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ incident_id, unit_id }),
    });
    alert(`Dispatched ${r.assigned_unit} to incident #${r.id}`);
    refreshAll();
  } catch (e) {
    alert("Dispatch failed: " + e.message);
  }
};

document.getElementById("btnEnrollFace").onclick = async () => {
  const id = document.getElementById("enrollWatchlistId").value;
  const fileInput = document.getElementById("enrollFaceFile");
  if (!id || !fileInput.files.length) {
    alert("Enter watchlist ID and select a reference photo.");
    return;
  }
  const form = new FormData();
  form.append("watchlist_id", id);
  form.append("file", fileInput.files[0]);
  const res = await fetch(API + "/watchlist/enroll", { method: "POST", body: form });
  const r = await res.json();
  document.getElementById("faceResult").textContent = JSON.stringify(r, null, 2);
  if (res.ok) loadWatchlist();
};

document.getElementById("btnFaceScan").onclick = async () => {
  const fileInput = document.getElementById("faceScanFile");
  if (!fileInput.files.length) {
    alert("Select an image to analyze.");
    return;
  }
  const form = new FormData();
  form.append("file", fileInput.files[0]);
  form.append("create_incident", document.getElementById("faceCreateIncident").checked);
  form.append("zone", "Zone 1 - CBD");
  document.getElementById("faceResult").textContent = "Analyzing faces...";
  const res = await fetch(API + "/facial-recognition/analyze-image", { method: "POST", body: form });
  const r = await res.json();
  document.getElementById("faceResult").textContent = JSON.stringify(r, null, 2);
  if (r.annotated_image_base64) {
    const img = document.getElementById("facePreview");
    img.src = "data:image/jpeg;base64," + r.annotated_image_base64;
    img.style.display = "block";
  }
  if (r.incident_id) refreshAll();
};

document.getElementById("btnAnprScan").onclick = async () => {
  const fileInput = document.getElementById("anprFile");
  if (!fileInput.files.length) {
    alert("Select a vehicle image.");
    return;
  }
  const form = new FormData();
  form.append("file", fileInput.files[0]);
  form.append("create_incident", document.getElementById("anprCreateIncident").checked);
  form.append("zone", "Zone 2 - Intersections");
  document.getElementById("anprResult").textContent = "Running ANPR (first run may take a minute)...";
  const res = await fetch(API + "/anpr/analyze-image", { method: "POST", body: form });
  const r = await res.json();
  document.getElementById("anprResult").textContent = JSON.stringify(r, null, 2);
  if (r.annotated_image_base64) {
    const img = document.getElementById("anprPreview");
    img.src = "data:image/jpeg;base64," + r.annotated_image_base64;
    img.style.display = "block";
  }
  if (r.incident_id) refreshAll();
};

async function uploadVision(endpoint, fileInputId) {
  const fileInput = document.getElementById(fileInputId);
  if (!fileInput.files.length) {
    alert("Please select a file first.");
    return;
  }
  const form = new FormData();
  form.append("file", fileInput.files[0]);
  form.append("create_incident", document.getElementById("visionCreateIncident").checked);
  form.append("zone", document.getElementById("visionZone").value);
  document.getElementById("visionResult").textContent = "Analyzing...";
  const res = await fetch(API + endpoint, { method: "POST", body: form });
  const r = await res.json();
  if (!res.ok) {
    document.getElementById("visionResult").textContent = r.detail || "Analysis failed";
    return;
  }
  const summary = { message: r.message, motion_detected: r.motion_detected, incident_id: r.incident_id };
  if (r.region_count !== undefined) summary.regions = r.region_count;
  if (r.motion_events !== undefined) summary.motion_events = r.motion_events;
  document.getElementById("visionResult").textContent = JSON.stringify(summary, null, 2);
  const preview = document.getElementById("visionPreview");
  const b64 = r.annotated_image_base64 || (r.events && r.events[0] && r.events[0].preview_base64);
  if (b64) {
    preview.src = "data:image/jpeg;base64," + b64;
    preview.style.display = "block";
  } else {
    preview.style.display = "none";
  }
  if (r.incident_id) refreshAll();
}

document.getElementById("btnVisionImage").onclick = () => uploadVision("/vision/analyze-image", "visionImageFile");
document.getElementById("btnVisionVideo").onclick = () => uploadVision("/vision/analyze-video", "visionVideoFile");

document.getElementById("citizenForm").onsubmit = async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const body = Object.fromEntries(fd.entries());
  body.latitude = parseFloat(body.latitude);
  body.longitude = parseFloat(body.longitude);
  await fetchJSON("/citizen/reports", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  alert("Report submitted and linked to incident.");
  e.target.reset();
  refreshAll();
};

document.querySelectorAll(".module-nav button").forEach((btn) => {
  btn.onclick = () => {
    document.querySelectorAll(".module-nav button").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach((t) => t.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
  };
});

async function refreshAll() {
  await Promise.all([
    loadStats(),
    loadIncidents(),
    loadAlerts(),
    loadCameras(),
    loadSensors(),
    loadTraffic(),
    loadUnits(),
    loadWatchlist(),
    loadVehicles(),
    loadHotspots(),
    loadReports(),
  ]);
}

initMap();
refreshAll();
setInterval(refreshAll, 30000);
