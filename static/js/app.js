/**
 * Puducherry CRIMEMAP - Command & Control Center (C4I)
 * Core Frontend Application Controller
 * Handles Leaflet Maps, Heatmaps, Spatial Analytics, ML Risk Predictions,
 * CAD Emergency Dispatch, and CopAI Tactical Assistant.
 */

// Application State
let map;
let baseLayers = {};
let currentBasemap = 'dark';

// Layer Groups
let layers = {
  incidents: null,
  heatmap: null,
  stations: null,
  patrols: null,
  cctv: null,
  darkspots: null,
  patrolRoute: null,
  dispatchRoute: null
};

// Data caches
let allIncidents = [];
let allStations = [];
let allCctvs = [];
let allDarkSpots = [];
let allPatrols = [];
let analyticsData = null;
let currentSectorPredictions = [];

// Chart instances
let chartHourlyInstance = null;
let chartDowInstance = null;
let chartCategoryInstance = null;
let chartStationsInstance = null;
let chartForecastInstance = null;

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  initClock();
  initMap();
  loadAllData();
});

/* ==========================================================
   1. CLOCK & TELEMETRY
   ========================================================== */
function initClock() {
  const clockEl = document.getElementById('istClock');
  function update() {
    const now = new Date();
    clockEl.innerText = now.toLocaleTimeString('en-US', { hour12: false }) + ' IST';
  }
  update();
  setInterval(update, 1000);
}

/* ==========================================================
   2. LEAFLET MAP INITIALIZATION
   ========================================================== */
function initMap() {
  // Center on Puducherry Boulevard & Town: [11.9338, 79.8326]
  map = L.map('leafletMap', {
    center: [11.9338, 79.8326],
    zoom: 13,
    zoomControl: true
  });

  // Basemaps
  baseLayers.dark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CartoDB &copy; OpenStreetMap',
    maxZoom: 19
  });

  baseLayers.osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19
  });

  baseLayers.satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: '&copy; Esri &copy; DigitalGlobe',
    maxZoom: 19
  });

  baseLayers.dark.addTo(map);

  // Initialize Layer Groups
  layers.incidents = L.markerClusterGroup({
    maxClusterRadius: 40,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false
  });
  layers.stations = L.layerGroup();
  layers.patrols = L.layerGroup();
  layers.cctv = L.layerGroup();
  layers.darkspots = L.layerGroup();
  layers.patrolRoute = L.layerGroup();
  layers.dispatchRoute = L.layerGroup();

  map.addLayer(layers.incidents);
  map.addLayer(layers.stations);
  map.addLayer(layers.patrols);
  map.addLayer(layers.cctv);
  map.addLayer(layers.darkspots);
  map.addLayer(layers.patrolRoute);
  map.addLayer(layers.dispatchRoute);

  // Click on map to trigger CAD SOS Emergency Simulator
  map.on('click', function(e) {
    const lat = e.latlng.lat.toFixed(5);
    const lng = e.latlng.lng.toFixed(5);
    
    // Set CAD form values
    document.getElementById('cadLat').value = lat;
    document.getElementById('cadLng').value = lng;
    
    // Create instant popup offering CAD dispatch
    L.popup()
      .setLatLng(e.latlng)
      .setContent(`
        <div style="font-family:sans-serif; font-size:12px; color:#1e293b;">
          <strong style="color:#ef4444;"><i class="fa-solid fa-tower-broadcast"></i> 112 SOS Incident Point</strong><br>
          Lat: ${lat}, Lng: ${lng}<br><br>
          <button style="background:#ef4444; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer; font-weight:bold;"
                  onclick="triggerCadFromPopup(${lat}, ${lng})">
            🚨 Dispatch Nearest PCR Van Here
          </button>
        </div>
      `)
      .openOn(map);
  });
}

function setBasemap(type) {
  currentBasemap = type;
  document.querySelectorAll('.btn-basemap').forEach(b => b.classList.remove('active'));
  if (type === 'dark') document.getElementById('btnBaseDark').classList.add('active');
  if (type === 'osm') document.getElementById('btnBaseOsm').classList.add('active');
  if (type === 'satellite') document.getElementById('btnBaseSat').classList.add('active');

  map.removeLayer(baseLayers.dark);
  map.removeLayer(baseLayers.osm);
  map.removeLayer(baseLayers.satellite);
  baseLayers[type].addTo(map);
}

function toggleMapLayer(layerKey) {
  const isChecked = document.getElementById('layer' + layerKey.charAt(0).toUpperCase() + layerKey.slice(1)).checked;
  const targetLayer = layers[layerKey];
  if (!targetLayer) return;

  if (isChecked) {
    if (!map.hasLayer(targetLayer)) map.addLayer(targetLayer);
  } else {
    if (map.hasLayer(targetLayer)) map.removeLayer(targetLayer);
  }
}

/* ==========================================================
   3. DATA LOADING & RENDERING
   ========================================================== */
async function loadAllData() {
  try {
    const [incidentsRes, stationsRes, cctvsRes, darkspotsRes, patrolsRes, analyticsRes] = await Promise.all([
      fetch('/api/incidents'),
      fetch('/api/stations'),
      fetch('/api/cctvs'),
      fetch('/api/darkspots'),
      fetch('/api/patrols'),
      fetch('/api/analytics')
    ]);

    const incidentsJson = await incidentsRes.json();
    allIncidents = incidentsJson.data;
    allStations = await stationsRes.json();
    allCctvs = await cctvsRes.json();
    allDarkSpots = await darkspotsRes.json();
    allPatrols = await patrolsRes.json();
    analyticsData = await analyticsRes.json();

    // Render layers
    renderIncidents(allIncidents);
    renderHeatmap(allIncidents);
    renderStations(allStations);
    renderPatrols(allPatrols);
    renderCctvs(allCctvs);
    renderDarkSpots(allDarkSpots);

    // Render analytics & predictions
    updateKPIs(analyticsData.summary);
    renderCharts(analyticsData);
    refreshPredictions();
    loadForecastCurve();
    generateOptimalPatrolRoute();

  } catch (err) {
    console.error('Error loading Puducherry data:', err);
  }
}

/* --- Render Incidents --- */
function renderIncidents(incidents) {
  layers.incidents.clearLayers();
  document.getElementById('mapStatIncidents').innerText = incidents.length.toLocaleString();
  document.getElementById('incidentCounterBadge').innerText = incidents.length.toLocaleString();

  incidents.forEach(inc => {
    // Custom icon color based on severity
    let markerColor = '#3b82f6';
    if (inc.severity === 'Critical') markerColor = '#ef4444';
    else if (inc.severity === 'High') markerColor = '#f97316';
    else if (inc.severity === 'Medium') markerColor = '#eab308';

    const iconHtml = `
      <div style="background-color: ${markerColor}; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #ffffff; box-shadow: 0 0 8px ${markerColor};"></div>
    `;
    const customIcon = L.divIcon({
      className: 'custom-crime-pin',
      html: iconHtml,
      iconSize: [14, 14],
      iconAnchor: [7, 7]
    });

    const marker = L.marker([inc.lat, inc.lng], { icon: customIcon });

    const popupHtml = `
      <div style="font-family: 'Inter', sans-serif; font-size: 12px; color: #1e293b; max-width: 260px;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #cbd5e1; padding-bottom:4px; margin-bottom:6px;">
          <strong style="color:#0f172a; font-size:13px;">${inc.id}</strong>
          <span style="background:${markerColor}; color:#fff; font-size:10px; font-weight:bold; padding:1px 6px; border-radius:3px;">
            ${inc.severity}
          </span>
        </div>
        <div style="font-weight:600; color:#0f172a; margin-bottom:4px;">${inc.title}</div>
        <div style="color:#64748b; font-size:11px; margin-bottom:2px;"><strong>IPC / Law:</strong> ${inc.ipc_section}</div>
        <div style="color:#64748b; font-size:11px; margin-bottom:2px;"><strong>Station:</strong> ${inc.police_station}</div>
        <div style="color:#64748b; font-size:11px; margin-bottom:2px;"><strong>Time:</strong> ${inc.timestamp}</div>
        <div style="color:#64748b; font-size:11px; margin-bottom:4px;"><strong>Lighting:</strong> ${inc.lighting}</div>
        <div style="background:#f1f5f9; padding:5px; border-radius:4px; font-size:11px; color:#334155;">
          ${inc.description}
        </div>
        <div style="margin-top:6px; font-size:11px; font-weight:bold; color:#10b981;">
          Status: ${inc.status}
        </div>
      </div>
    `;

    marker.bindPopup(popupHtml);
    layers.incidents.addLayer(marker);
  });
}

/* --- Render Heatmap (Kernel Density Estimation) --- */
function renderHeatmap(incidents) {
  if (layers.heatmap && map.hasLayer(layers.heatmap)) {
    map.removeLayer(layers.heatmap);
  }

  const heatPoints = incidents.map(inc => [inc.lat, inc.lng, (inc.weight || 3) * 0.25]);

  layers.heatmap = L.heatLayer(heatPoints, {
    radius: 26,
    blur: 18,
    maxZoom: 16,
    gradient: {
      0.2: '#06b6d4',
      0.4: '#10b981',
      0.6: '#eab308',
      0.8: '#f97316',
      1.0: '#ef4444'
    }
  });

  const isHeatChecked = document.getElementById('layerHeatmap').checked;
  if (isHeatChecked) {
    layers.heatmap.addTo(map);
  }
}

/* --- Render Police Stations --- */
function renderStations(stations) {
  layers.stations.clearLayers();
  stations.forEach(ps => {
    const iconHtml = `
      <div style="background:#1e3a8a; border:2px solid #3b82f6; color:#fff; width:28px; height:28px; border-radius:6px; display:flex; align-items:center; justify-content:center; box-shadow:0 0 10px rgba(59,130,246,0.6);">
        <i class="fa-solid fa-building-shield" style="font-size:14px;"></i>
      </div>
    `;
    const icon = L.divIcon({ html: iconHtml, className: 'station-pin', iconSize: [28, 28], iconAnchor: [14, 14] });
    const marker = L.marker([ps.lat, ps.lng], { icon: icon });

    marker.bindPopup(`
      <div style="font-family:sans-serif; font-size:12px; color:#1e293b;">
        <strong style="color:#1e3a8a; font-size:13px;"><i class="fa-solid fa-building-shield"></i> ${ps.name}</strong><br>
        <span style="color:#64748b;">Division: ${ps.division}</span><br><br>
        <strong>Officer in Charge:</strong> ${ps.inspector}<br>
        <strong>Emergency Contact:</strong> ${ps.contact}<br>
        <strong>Jurisdiction Area:</strong> ${ps.coverage_sqkm} sq.km<br>
        <strong>Deployed Personnel:</strong> ${ps.personnel} Active Staff
      </div>
    `);

    layers.stations.addLayer(marker);
  });
}

/* --- Render Live Patrol Units --- */
function renderPatrols(patrols) {
  layers.patrols.clearLayers();
  patrols.forEach(p => {
    let statusColor = p.status === 'RESPONDING' ? '#ef4444' : '#10b981';
    const iconHtml = `
      <div style="background:#0f172a; border:2px solid ${statusColor}; color:${statusColor}; width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 0 12px ${statusColor};">
        <i class="fa-solid fa-car-side" style="font-size:14px;"></i>
      </div>
    `;
    const icon = L.divIcon({ html: iconHtml, className: 'patrol-pin', iconSize: [30, 30], iconAnchor: [15, 15] });
    const marker = L.marker([p.lat, p.lng], { icon: icon });

    marker.bindPopup(`
      <div style="font-family:sans-serif; font-size:12px; color:#1e293b;">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #cbd5e1; padding-bottom:4px; margin-bottom:6px;">
          <strong style="color:#0f172a; font-size:13px;">${p.callsign} (${p.id})</strong>
          <span style="background:${statusColor}; color:white; font-size:10px; font-weight:bold; padding:2px 6px; border-radius:3px;">
            ${p.status}
          </span>
        </div>
        <strong>Vehicle:</strong> ${p.vehicle}<br>
        <strong>Assigned Sector:</strong> ${p.sector}<br>
        <strong>Officer:</strong> ${p.officer}<br>
        <strong>Speed:</strong> ${p.speed_kmh} km/h | <strong>Battery/Fuel:</strong> ${p.battery}%<br>
        <strong>Phone:</strong> ${p.phone}
      </div>
    `);

    layers.patrols.addLayer(marker);
  });
}

/* --- Render CCTV Surveillance Grid --- */
function renderCctvs(cctvs) {
  layers.cctv.clearLayers();
  cctvs.forEach(cam => {
    let color = cam.status === 'ONLINE' ? '#06b6d4' : (cam.status === 'OFFLINE' ? '#ef4444' : '#f59e0b');
    const iconHtml = `
      <div style="background:#0f172a; border:2px solid ${color}; color:${color}; width:24px; height:24px; border-radius:4px; display:flex; align-items:center; justify-content:center;">
        <i class="fa-solid fa-video" style="font-size:11px;"></i>
      </div>
    `;
    const icon = L.divIcon({ html: iconHtml, className: 'cctv-pin', iconSize: [24, 24], iconAnchor: [12, 12] });
    const marker = L.marker([cam.lat, cam.lng], { icon: icon });

    marker.bindPopup(`
      <div style="font-family:sans-serif; font-size:12px; color:#1e293b;">
        <strong style="color:#0f172a;"><i class="fa-solid fa-video"></i> ${cam.name} (${cam.id})</strong><br>
        <strong>Zone:</strong> ${cam.zone}<br>
        <strong>Type:</strong> ${cam.type}<br>
        <strong>Live Stream:</strong> <span style="color:${color}; font-weight:bold;">${cam.status}</span><br><br>
        <div style="background:#000; color:#34d399; font-family:monospace; padding:8px; border-radius:4px; text-align:center;">
          [SIMULATED 4K FEED ACTIVE]<br>
          LAT: ${cam.lat} | LNG: ${cam.lng}
        </div>
      </div>
    `);

    layers.cctv.addLayer(marker);
  });
}

/* --- Render Dark Spots & Infrastructure Vulnerability --- */
function renderDarkSpots(darkspots) {
  layers.darkspots.clearLayers();
  darkspots.forEach(ds => {
    const iconHtml = `
      <div style="background:#78350f; border:2px solid #eab308; color:#fde047; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; box-shadow:0 0 10px rgba(234,179,8,0.7);">
        <i class="fa-solid fa-lightbulb" style="font-size:12px;"></i>
      </div>
    `;
    const icon = L.divIcon({ html: iconHtml, className: 'darkspot-pin', iconSize: [26, 26], iconAnchor: [13, 13] });
    const marker = L.marker([ds.lat, ds.lng], { icon: icon });

    marker.bindPopup(`
      <div style="font-family:sans-serif; font-size:12px; color:#1e293b;">
        <strong style="color:#b45309;"><i class="fa-solid fa-lightbulb"></i> Dark Spot: ${ds.name}</strong><br>
        <strong>Illuminance:</strong> <span style="color:#ef4444; font-family:monospace; font-weight:bold;">${ds.lux_level} Lux</span> (Threshold &lt; 5.0 Lux)<br>
        <strong>Defect Note:</strong> ${ds.defect}<br>
        <strong>Crime Correlation:</strong> ${ds.crime_history}<br>
        <strong>PWD Ticket:</strong> <span style="font-family:monospace; color:#3b82f6;">${ds.pwd_ticket}</span><br>
        <strong>Priority:</strong> <span style="color:#ef4444; font-weight:bold;">${ds.priority}</span>
      </div>
    `);

    layers.darkspots.addLayer(marker);
  });
}

/* ==========================================================
   4. SPATIO-TEMPORAL FILTERS
   ========================================================== */
function applyFilters() {
  const station = document.getElementById('filterStation').value;
  const category = document.getElementById('filterCategory').value;
  const severity = document.getElementById('filterSeverity').value;
  const hourVal = parseInt(document.getElementById('hourSlider').value, 10);

  let filtered = allIncidents;

  if (station !== 'All') {
    filtered = filtered.filter(x => x.police_station === station);
  }
  if (category !== 'All') {
    filtered = filtered.filter(x => x.category === category);
  }
  if (severity !== 'All') {
    filtered = filtered.filter(x => x.severity === severity);
  }

  // If slider is less than 23, filter by specific hour window (+/- 2 hours)
  if (hourVal < 23) {
    const minH = Math.max(0, hourVal - 2);
    const maxH = Math.min(23, hourVal + 2);
    filtered = filtered.filter(x => x.hour >= minH && x.hour <= maxH);
  }

  renderIncidents(filtered);
  renderHeatmap(filtered);
}

function onHourSliderChange(val) {
  const v = parseInt(val, 10);
  const label = document.getElementById('timeSliderVal');
  if (v === 23) {
    label.innerText = '00:00 - 23:59 (Full Day)';
  } else {
    const minH = Math.max(0, v - 2);
    const maxH = Math.min(23, v + 2);
    label.innerText = `${String(minH).padStart(2, '0')}:00 - ${String(maxH).padStart(2, '0')}:00 Window`;
  }
  applyFilters();
}

function resetFilters() {
  document.getElementById('filterStation').value = 'All';
  document.getElementById('filterCategory').value = 'All';
  document.getElementById('filterSeverity').value = 'All';
  document.getElementById('hourSlider').value = '23';
  document.getElementById('timeSliderVal').innerText = '00:00 - 23:59 (Full Day)';
  renderIncidents(allIncidents);
  renderHeatmap(allIncidents);
}

/* ==========================================================
   5. TAB 2: ANALYTICS & CHARTS
   ========================================================== */
function updateKPIs(summary) {
  document.getElementById('kpiTotal').innerText = summary.total_incidents.toLocaleString();
  document.getElementById('kpiResolved').innerText = summary.resolution_rate_pct + '%';
  document.getElementById('kpiCritical').innerText = summary.critical_cases.toLocaleString();
  document.getElementById('kpiResponse').innerText = summary.mean_response_time_mins + ' Min';

  // Website Portal Metrics
  const webCases = summary.web_cases_filed || 142;
  const ongoingCases = summary.ongoing_cases || 318;

  if (document.getElementById('headerWebCases')) document.getElementById('headerWebCases').innerText = webCases.toLocaleString();
  if (document.getElementById('headerOngoingCases')) document.getElementById('headerOngoingCases').innerText = ongoingCases.toLocaleString();
  if (document.getElementById('mapStatWebCases')) document.getElementById('mapStatWebCases').innerText = `${webCases.toLocaleString()} Cases`;
  if (document.getElementById('mapStatOngoingCases')) document.getElementById('mapStatOngoingCases').innerText = `${ongoingCases.toLocaleString()} Active`;
  if (document.getElementById('kpiWebCases')) document.getElementById('kpiWebCases').innerText = webCases.toLocaleString();
  if (document.getElementById('kpiOngoingCases')) document.getElementById('kpiOngoingCases').innerText = ongoingCases.toLocaleString();

  // Modal report elements
  document.getElementById('repTotal').innerText = summary.total_incidents.toLocaleString();
  document.getElementById('repResolved').innerText = summary.resolution_rate_pct + '%';
  document.getElementById('repCritical').innerText = summary.critical_cases.toLocaleString();
  document.getElementById('repEta').innerText = summary.mean_response_time_mins + ' Min';
}

function renderCharts(data) {
  Chart.defaults.color = '#94a3b8';
  Chart.defaults.font.family = "'Inter', sans-serif";

  // Chart 1: Diurnal Hourly Curve
  const ctxHourly = document.getElementById('chartHourly').getContext('2d');
  const hourlyLabels = Object.keys(data.hourly).map(h => `${h}:00`);
  const hourlyVals = Object.values(data.hourly);

  if (chartHourlyInstance) chartHourlyInstance.destroy();
  chartHourlyInstance = new Chart(ctxHourly, {
    type: 'line',
    data: {
      labels: hourlyLabels,
      datasets: [{
        label: 'Incident Volume',
        data: hourlyVals,
        borderColor: '#06b6d4',
        backgroundColor: 'rgba(6, 182, 212, 0.15)',
        tension: 0.35,
        fill: true,
        pointBackgroundColor: '#06b6d4',
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' } },
        y: { grid: { color: 'rgba(255,255,255,0.05)' } }
      }
    }
  });

  // Chart 2: Day of Week Trend
  const ctxDow = document.getElementById('chartDow').getContext('2d');
  const dowLabels = Object.keys(data.day_of_week);
  const dowVals = Object.values(data.day_of_week);

  if (chartDowInstance) chartDowInstance.destroy();
  chartDowInstance = new Chart(ctxDow, {
    type: 'bar',
    data: {
      labels: dowLabels,
      datasets: [{
        label: 'Incident Frequency',
        data: dowVals,
        backgroundColor: dowLabels.map(d => (d === 'Saturday' || d === 'Sunday') ? '#ef4444' : '#3b82f6'),
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: 'rgba(255,255,255,0.05)' } }
      }
    }
  });

  // Chart 3: Typology Doughnut
  const ctxCat = document.getElementById('chartCategory').getContext('2d');
  const catLabels = Object.keys(data.categories);
  const catVals = Object.values(data.categories);

  if (chartCategoryInstance) chartCategoryInstance.destroy();
  chartCategoryInstance = new Chart(ctxCat, {
    type: 'doughnut',
    data: {
      labels: catLabels,
      datasets: [{
        data: catVals,
        backgroundColor: [
          '#ef4444', '#f97316', '#f59e0b', '#10b981',
          '#06b6d4', '#3b82f6', '#6366f1', '#a855f7'
        ],
        borderWidth: 1,
        borderColor: '#111827'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right', labels: { boxWidth: 10, font: { size: 10 } } }
      }
    }
  });

  // Chart 4: Station Leaderboard
  const ctxStations = document.getElementById('chartStations').getContext('2d');
  const stationLabels = data.top_police_stations.map(x => x[0].replace(' Police Station', ''));
  const stationVals = data.top_police_stations.map(x => x[1]);

  if (chartStationsInstance) chartStationsInstance.destroy();
  chartStationsInstance = new Chart(ctxStations, {
    type: 'bar',
    data: {
      labels: stationLabels,
      datasets: [{
        label: 'Recorded FIRs',
        data: stationVals,
        backgroundColor: '#8b5cf6',
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(255,255,255,0.05)' } },
        y: { grid: { display: false }, ticks: { font: { size: 10 } } }
      }
    }
  });
}

/* ==========================================================
   6. TAB 3: MACHINE LEARNING RISK PREDICTIONS
   ========================================================== */
async function refreshPredictions(customScenario = null) {
  const hour = parseInt(document.getElementById('predictHour').value, 10);
  const dow = parseInt(document.getElementById('predictDow').value, 10);

  const payload = {
    hour: hour,
    day_of_week: dow,
    scenario: customScenario
  };

  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    currentSectorPredictions = result.predictions;
    renderSectorRiskCards(currentSectorPredictions);
  } catch (err) {
    console.error('Error calculating predictions:', err);
  }
}

function renderSectorRiskCards(sectors) {
  const grid = document.getElementById('sectorRiskGrid');
  grid.innerHTML = '';

  sectors.forEach(sec => {
    const card = document.createElement('div');
    card.className = `sector-card threat-${sec.threat_level}`;

    card.innerHTML = `
      <div class="sector-card-top">
        <div>
          <div class="sector-title">${sec.sector_name}</div>
          <div class="sector-sub">${sec.police_station}</div>
        </div>
        <div class="sector-risk-badge risk-${sec.threat_level}">
          ${sec.risk_score} RISK
        </div>
      </div>
      <div class="sector-threat-desc">
        <strong>Primary Threat:</strong> ${sec.primary_threat}
      </div>
      <div class="sector-action">
        <i class="fa-solid fa-shield-virus"></i> ${sec.recommended_action}
      </div>
    `;

    grid.appendChild(card);
  });
}

async function loadForecastCurve() {
  try {
    const res = await fetch('/api/forecast?dow=5');
    const forecast = await res.json();

    const labels = forecast.map(f => f.time_label);
    const avgData = forecast.map(f => f.average_city_risk);
    const peakData = forecast.map(f => f.peak_sector_risk);

    const ctx = document.getElementById('chartForecast').getContext('2d');
    if (chartForecastInstance) chartForecastInstance.destroy();

    chartForecastInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Peak Sector Risk',
            data: peakData,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            fill: true,
            tension: 0.3
          },
          {
            label: 'Citywide Average Risk',
            data: avgData,
            borderColor: '#3b82f6',
            borderDash: [5, 5],
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12 } }
        },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, min: 0, max: 100 }
        }
      }
    });
  } catch (err) {
    console.error('Forecast curve error:', err);
  }
}

async function runSimulation(scenarioType, btnEl) {
  document.querySelectorAll('.btn-sim-preset').forEach(b => b.classList.remove('active'));
  if (btnEl) btnEl.classList.add('active');

  const hour = parseInt(document.getElementById('predictHour').value, 10);
  const dow = parseInt(document.getElementById('predictDow').value, 10);

  try {
    const res = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: scenarioType, hour: hour, dow: dow })
    });
    const data = await res.json();

    document.getElementById('simBannerTitle').innerText = data.scenario_name;
    document.getElementById('simBannerDesc').innerText = data.description;

    renderSectorRiskCards(data.simulated_predictions);
  } catch (err) {
    console.error('Simulation error:', err);
  }
}

/* ==========================================================
   7. TAB 4: DECISION SUPPORT (PATROL ROUTING & CAD)
   ========================================================== */
let activePatrolPlan = null;

async function generateOptimalPatrolRoute() {
  const patrolId = document.getElementById('selectPatrolUnit').value;

  try {
    const res = await fetch('/api/optimize-patrol', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patrol_id: patrolId })
    });
    activePatrolPlan = await res.json();

    document.getElementById('routeDist').innerText = activePatrolPlan.total_route_distance_km + ' km';
    document.getElementById('routeTime').innerText = activePatrolPlan.estimated_circuit_mins + ' Mins';

    const listEl = document.getElementById('routeItinerary');
    listEl.innerHTML = '';

    activePatrolPlan.checkpoints.forEach(cp => {
      const stepEl = document.createElement('div');
      stepEl.className = 'itinerary-step';
      stepEl.innerHTML = `
        <div class="step-num">${cp.step}</div>
        <div class="step-details">
          <div class="step-title">${cp.name}</div>
          <div class="step-meta">
            ${cp.threat ? `Threat: ${cp.threat} • ` : ''} ETA: +${cp.eta_mins} mins (${cp.cum_distance_km} km)
          </div>
          <div class="step-action">
            <i class="fa-solid fa-bullseye"></i> ${cp.action}
          </div>
        </div>
      `;
      listEl.appendChild(stepEl);
    });

  } catch (err) {
    console.error('Patrol route optimization error:', err);
  }
}

function showPatrolRouteOnMap() {
  if (!activePatrolPlan) return;
  switchTab('map-tab');

  layers.patrolRoute.clearLayers();
  const latlngs = activePatrolPlan.checkpoints.map(cp => [cp.lat, cp.lng]);

  const polyline = L.polyline(latlngs, {
    color: '#06b6d4',
    weight: 4,
    opacity: 0.85,
    dashArray: '8, 8'
  }).addTo(layers.patrolRoute);

  map.fitBounds(polyline.getBounds(), { padding: [50, 50] });

  // Add animated start point marker
  const startCp = activePatrolPlan.checkpoints[0];
  L.popup()
    .setLatLng([startCp.lat, startCp.lng])
    .setContent(`<strong>🚀 Patrol Circuit Activated:</strong> ${activePatrolPlan.callsign}<br>Total Circuit: ${activePatrolPlan.total_route_distance_km} km`)
    .openOn(map);
}

/* --- CAD 112 Emergency Dispatch --- */
async function executeCadDispatch() {
  const incidentType = document.getElementById('cadIncidentType').value;
  const lat = parseFloat(document.getElementById('cadLat').value);
  const lng = parseFloat(document.getElementById('cadLng').value);

  try {
    const res = await fetch('/api/dispatch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lat: lat,
        lng: lng,
        emergency_type: incidentType
      })
    });
    const dispatch = await res.json();

    // Show result card
    const card = document.getElementById('cadResult');
    card.style.display = 'block';

    document.getElementById('cadDispatchedCallsign').innerText = `${dispatch.dispatched_unit.callsign} (${dispatch.dispatched_unit.id})`;
    document.getElementById('cadVehicle').innerText = dispatch.dispatched_unit.vehicle;
    document.getElementById('cadOfficer').innerText = dispatch.dispatched_unit.officer;
    document.getElementById('cadDist').innerText = dispatch.distance_km + ' km';
    document.getElementById('cadEta').innerText = dispatch.eta_mins + ' mins';
    document.getElementById('cadBackup').innerText = dispatch.nearby_backup ? `${dispatch.nearby_backup.callsign} (${dispatch.nearby_backup.id})` : 'None';

    // Show secure CAD alert confirmation
    const emailNoticeEl = document.getElementById('cadEmailNotice');
    if (!emailNoticeEl) {
      const emailDiv = document.createElement('div');
      emailDiv.id = 'cadEmailNotice';
      emailDiv.style.cssText = 'background:rgba(16,185,129,0.15); border:1px solid #10b981; color:#34d399; padding:6px 10px; border-radius:4px; font-size:11px; margin-top:8px; display:flex; align-items:center; gap:6px;';
      emailDiv.innerHTML = `<i class="fa-solid fa-satellite-dish"></i> <strong>Priority CAD Alert:</strong> Dispatched to Senior Police Command (Encrypted Channel)`;
      card.querySelector('.cad-result-card > div:nth-child(2)').appendChild(emailDiv);
    }

    // Draw dispatch line on map
    layers.dispatchRoute.clearLayers();

    // Incident target red flashing marker
    const emergencyIcon = L.divIcon({
      html: `<div style="background:#ef4444; width:22px; height:22px; border-radius:50%; border:3px solid #fff; box-shadow:0 0 16px #ef4444;"></div>`,
      className: 'emergency-pulse',
      iconSize: [22, 22],
      iconAnchor: [11, 11]
    });
    L.marker([lat, lng], { icon: emergencyIcon })
      .bindPopup(`<strong>🚨 ACTIVE 112 SOS CALL:</strong><br>${incidentType}`)
      .addTo(layers.dispatchRoute)
      .openPopup();

    // Dispatch path
    const routeLine = L.polyline(dispatch.trajectory, {
      color: '#ef4444',
      weight: 5,
      opacity: 0.9,
      dashArray: '6, 6'
    }).addTo(layers.dispatchRoute);

  } catch (err) {
    console.error('CAD Dispatch error:', err);
  }
}

function triggerCadFromPopup(lat, lng) {
  document.getElementById('cadLat').value = lat;
  document.getElementById('cadLng').value = lng;
  switchTab('prevent-tab');
  executeCadDispatch();
}

function setCadCoordinatesFromPreset() {
  document.getElementById('cadLat').value = '11.9328';
  document.getElementById('cadLng').value = '79.8352';
}

function triggerQuickSosDemo() {
  switchTab('prevent-tab');
  setCadCoordinatesFromPreset();
  executeCadDispatch();
}

/* ==========================================================
   8. TAB NAVIGATION
   ========================================================== */
function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

  const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
  if (activeBtn) activeBtn.classList.add('active');

  const content = document.getElementById(tabId);
  if (content) content.classList.add('active');

  // Trigger Leaflet resize calculation when returning to map tab
  if (tabId === 'map-tab' && map) {
    setTimeout(() => { map.invalidateSize(); }, 200);
  }
}

/* ==========================================================
   9. HACKATHON DEMO WALKTHROUGHS
   ========================================================== */
function loadDemoScenario(name) {
  if (name === 'promenade') {
    document.getElementById('filterStation').value = 'Grand Bazaar Police Station';
    document.getElementById('filterCategory').value = 'Tourist Harassment & Women Safety';
    document.getElementById('hourSlider').value = '21';
    onHourSliderChange(21);
    map.flyTo([11.9335, 79.8350], 15);
  } else if (name === 'burglary') {
    document.getElementById('filterStation').value = 'Lawspet Police Station';
    document.getElementById('filterCategory').value = 'Night House Burglary & Trespass';
    document.getElementById('hourSlider').value = '2';
    onHourSliderChange(2);
    map.flyTo([11.9640, 79.8180], 14);
  } else if (name === 'ecr') {
    document.getElementById('filterStation').value = 'Muthialpet Police Station';
    document.getElementById('filterCategory').value = 'Narcotics (NDPS) Trafficking & Peddling';
    document.getElementById('hourSlider').value = '23';
    onHourSliderChange(23);
    map.flyTo([11.9560, 79.8330], 14);
  }
}

/* ==========================================================
   10. COP-AI ASSISTANT CHAT
   ========================================================== */
function toggleCopilot() {
  const drawer = document.getElementById('copilotDrawer');
  drawer.style.display = (drawer.style.display === 'flex') ? 'none' : 'flex';
}

async function sendCopilotQuery() {
  const input = document.getElementById('copilotInput');
  const query = input.value.trim();
  if (!query) return;

  const msgs = document.getElementById('copilotMessages');

  // Add User bubble
  const userBubble = document.createElement('div');
  userBubble.className = 'chat-bubble user';
  userBubble.innerText = query;
  msgs.appendChild(userBubble);
  input.value = '';
  msgs.scrollTop = msgs.scrollHeight;

  // Add Loading assistant bubble
  const assistantBubble = document.createElement('div');
  assistantBubble.className = 'chat-bubble assistant';
  assistantBubble.innerHTML = `<em>Consulting C4I intelligence engine...</em>`;
  msgs.appendChild(assistantBubble);
  msgs.scrollTop = msgs.scrollHeight;

  try {
    const res = await fetch('/api/copilot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query })
    });
    const data = await res.json();
    assistantBubble.innerHTML = data.answer.replace(/\n/g, '<br>');
    msgs.scrollTop = msgs.scrollHeight;
  } catch (err) {
    assistantBubble.innerText = 'Unable to reach CopAI assistant server.';
  }
}

/* ==========================================================
   11. LIVE FIR REGISTRATION MODAL
   ========================================================== */
function openFirModal() {
  document.getElementById('modalFir').style.display = 'flex';
}

function closeFirModal() {
  document.getElementById('modalFir').style.display = 'none';
}

async function submitNewFir() {
  const payload = {
    title: document.getElementById('newFirTitle').value || 'Reported Live Crime',
    category: document.getElementById('newFirCategory').value,
    police_station: document.getElementById('newFirStation').value,
    severity: document.getElementById('newFirSeverity').value,
    lat: parseFloat(document.getElementById('newFirLat').value),
    lng: parseFloat(document.getElementById('newFirLng').value),
    description: document.getElementById('newFirDesc').value
  };

  try {
    const res = await fetch('/api/incidents', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    alert(`🚨 SUCCESS: ${result.message}\n📡 Priority Emergency Alert dispatched to District Police Command.`);
    closeFirModal();

    // Reload all data to refresh map & analytics
    await loadAllData();
    switchTab('map-tab');
    map.flyTo([payload.lat, payload.lng], 16);
  } catch (err) {
    alert('Error saving FIR: ' + err);
  }
}

/* ==========================================================
   12. DAILY SITREP BRIEFING MODAL
   ========================================================== */
function openSitRepModal() {
  document.getElementById('modalSitRep').style.display = 'flex';
}

function closeSitRepModal() {
  document.getElementById('modalSitRep').style.display = 'none';
}

/* ==========================================================
   13. SECURE C4I OFFICER / ADMIN PORTAL (PIN PROTECTED)
   ========================================================== */
let adminSessionVerified = false;
let currentAdminPin = null;

function openAdminModal() {
  document.getElementById('modalAdmin').style.display = 'flex';
  if (adminSessionVerified) {
    showAdminDashboard();
  } else {
    document.getElementById('adminPinGate').style.display = 'flex';
    document.getElementById('adminSecretPanel').style.display = 'none';
    document.getElementById('adminPinInput').value = '';
    document.getElementById('adminPinError').style.display = 'none';
  }
}

function closeAdminModal() {
  document.getElementById('modalAdmin').style.display = 'none';
}

async function verifyAdminPin() {
  const pin = document.getElementById('adminPinInput').value.trim();
  const errorEl = document.getElementById('adminPinError');

  try {
    const res = await fetch(`/api/email-config?pin=${encodeURIComponent(pin)}`);
    if (res.status === 200) {
      const data = await res.json();
      adminSessionVerified = true;
      currentAdminPin = pin;
      showAdminDashboard(data);
    } else {
      errorEl.style.display = 'block';
      errorEl.innerText = 'Unauthorized. Incorrect Officer PIN.';
    }
  } catch (err) {
    errorEl.style.display = 'block';
    errorEl.innerText = 'Verification failed: ' + err;
  }
}

function showAdminDashboard(configData = null) {
  document.getElementById('adminPinGate').style.display = 'none';
  document.getElementById('adminSecretPanel').style.display = 'flex';

  if (configData) {
    document.getElementById('emailTargetInput').value = configData.target_email || '';
    document.getElementById('emailSmtpUserInput').value = configData.smtp_user || '';
    document.getElementById('emailSmtpPassInput').value = configData.smtp_pass || '';
  }
  loadEmailLogs();
}

function logoutAdminSession() {
  adminSessionVerified = false;
  currentAdminPin = null;
  document.getElementById('adminSecretPanel').style.display = 'none';
  document.getElementById('adminPinGate').style.display = 'flex';
  document.getElementById('adminPinInput').value = '';
  document.getElementById('emailTargetInput').value = '';
}

async function loadEmailLogs() {
  if (!currentAdminPin) return;
  const box = document.getElementById('emailLogBox');
  try {
    const res = await fetch(`/api/email-logs?pin=${encodeURIComponent(currentAdminPin)}`);
    const data = await res.json();
    if (data.logs && data.logs.length > 0) {
      box.innerText = data.logs.join('\n');
    } else {
      box.innerText = 'No email transmissions recorded yet. Live FIRs and SOS dispatches will log here.';
    }
  } catch (err) {
    box.innerText = 'Access restricted.';
  }
}

async function saveEmailConfig() {
  if (!currentAdminPin) {
    alert('Please verify your PIN first.');
    return;
  }
  const targetEmail = document.getElementById('emailTargetInput').value.trim();
  const smtpUser = document.getElementById('emailSmtpUserInput').value.trim();
  const smtpPass = document.getElementById('emailSmtpPassInput').value.trim();

  try {
    const res = await fetch('/api/email-config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pin: currentAdminPin,
        target_email: targetEmail,
        smtp_user: smtpUser,
        smtp_pass: smtpPass
      })
    });
    if (res.status === 200) {
      alert('Security & Notification settings updated successfully!');
      loadEmailLogs();
    } else {
      alert('Unauthorized request. Session expired.');
      logoutAdminSession();
    }
  } catch (err) {
    alert('Error saving configuration: ' + err);
  }
}
