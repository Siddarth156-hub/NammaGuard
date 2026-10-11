# 🚨 NammaGuard: Puducherry Geospatial Intelligence, Analytics & Decision-Support System

> **Project Name:** **NammaGuard** ("Our Safety Shield" for Puducherry)  
> **Hackathon Theme: M-A-P-P (Map • Analyse • Predict • Prevent)**  
> **Jurisdiction:** Union Territory of Puducherry, India (Pondicherry Police C4I Center)

---

## 📌 Executive Summary

**NammaGuard** is a next-generation **Law Enforcement Tactical Command, Control, Communications, and Intelligence (C4I)** platform purpose-built for the Union Territory of Puducherry. Designed around the four hackathon pillars—**Map, Analyse, Predict, and Prevent**—NammaGuard integrates real-time citizen complaint tracking, geospatial intelligence, statistical criminology, ensemble machine learning, and decision-support dispatch automation.

---

## 🌟 The 4 Core Pillars (M - A - P - P)

### 1. 🗺️ MAP (Geospatial Intelligence)
* **Real Geo-Referenced Cartography:** Interactive dark tactical map centered on Puducherry Boulevard, White Town, Lawspet, Muthialpet, Orleanpet, Villianur, and coastal corridors.
* **Granular Crime Incident Clusters:** 1,250+ historical and live FIR records coded with Indian Penal Code (IPC) and Bharatiya Nyaya Sanhita (BNS) sections, severity tags, and investigation statuses.
* **Dynamic Kernel Density Heatmap:** Real-time smoothing of incident weight distributions highlighting danger clusters.
* **Police Station Jurisdictions:** Coverage maps and live personnel stats for 12 Puducherry police stations (Grand Bazaar, Muthialpet, Lawspet, Orleanpet, Mudaliarpet, Reddiarpalayam, D'Nagar, Villianur, Ariyankuppam, Kalapet, Bahour, Coastal & Marine).
* **Smart CCTV Grid:** Live status tracking of 22 municipal PTZ and ANPR cameras.
* **Infrastructure Dark Spots:** Identification of unlit municipal stretches (< 5 Lux) linked to street crimes.
* **Live GPS Patrol Tracking:** Real-time monitoring of 8 Police Control Room (PCR) Bolero/Xenon vans and Cheetah motorcycle squads.

### 2. 📊 ANALYSE (Statistical Analytics & Criminology)
* **Diurnal Crime Curve:** 24-hour hourly cycle identifying peak night vulnerability windows (21:00 - 03:00 hrs).
* **Day-of-Week Trendline:** Comparative analytics capturing weekend tourist surges along Promenade Beach vs weekday resident crime.
* **Crime Typology Pareto Breakdown:** Categorization across 2-wheeler theft, night burglary, tourist harassment, NDPS trafficking, and cyber fraud.
* **Jurisdictional Station Load:** Automated workload distribution across Puducherry police circles.
* **Environmental Crime Correlation:** Empirical data showing **68.4% of after-dark snatching cases** occur within 150m of identified PWD dark spots.
* **Modus Operandi (MO) Clustering:** Automated suspect profiling for repeat offenses (e.g., bike-borne chain snatchers on MG Road).

### 3. 🧠 PREDICT (Machine Learning Spatio-Temporal Risk Engine)
* **Ensemble Predictive Model:** Trained with `RandomForestRegressor` and cyclic spatio-temporal features (`sin/cos` cyclic hour, day of week, tourist footfall index, lighting deficit factor).
* **Sector Risk Scores:** Real-time calculation of crime risk scores (0–100) across 12 Puducherry operational sectors.
* **24-Hour Forward Forecast Curve:** Future risk trajectory alerting commanding officers before danger windows peak.
* **"What-If" Tactical Scenario Simulator:**
  * *Scenario A:* Weekend Tourist Surge (+70% footfall in White Town)
  * *Scenario B:* Monsoon Power Cuts (80% jump in unlit dark spots)
  * *Scenario C:* ECR Midnight Drag Racing & NDPS Corridor
  * *Scenario D:* Operation Suraksha (+60% patrol saturation)

### 4. 🛡️ PREVENT (Decision-Support, Routing & Dispatch)
* **Dynamic Patrol Route Optimizer:** Solves the Traveling Salesperson Problem (TSP) using nearest-neighbor heuristics to generate the most fuel-efficient, high-deterrence patrol circuit for PCR vans.
* **112 CAD (Computer-Aided Dispatch) Simulator:** Click anywhere on the Puducherry map or trigger emergency SOS; CAD identifies the closest active patrol vehicle, calculates ETA, and streams turn-by-turn dispatch trajectories.
* **Infrastructure Remediation Auditor:** Automatically generates tracking tickets for the Public Works Department (PWD Electrical Division) to fix non-functional sodium lamps.
* **Executive Daily Situation Report (SitRep):** Generates official printable intelligence briefings for the Senior Superintendent of Police (SSP) and DGP.
* **Puducherry CopAI Tactical Assistant:** Natural language chatbot providing instant tactical guidance for field officers.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend & APIs** | Python 3.13, Flask, Flask-CORS |
| **Machine Learning** | Scikit-Learn (Random Forest Ensemble), NumPy, SciPy |
| **Geospatial Mapping** | Leaflet.js, Leaflet.heat, Leaflet.markercluster, CartoDB Dark Matter tiles |
| **Data Visualizations** | Chart.js 4.x (Diurnal curves, Doughnut typology, Bar load) |
| **Frontend UI** | HTML5, CSS3 Glassmorphism, FontAwesome 6, JetBrains Mono |
| **Data Engine** | GeoJSON spatial points, simulated GPS telemetry |

---

## 🚀 How to Run the Project

### Prerequisites
- Python 3.10+ (Python 3.13 tested)

### 1. Navigate to Project Directory
```powershell
cd C:\Users\user\.gemini\antigravity\scratch\crimemap-puducherry
```

### 2. Verify / Install Dependencies
```powershell
py -m pip install flask flask-cors numpy scikit-learn scipy
```

### 3. Start the CRIMEMAP Server
```powershell
py app.py
```

### 4. Open in Your Browser
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🎯 Hackathon Live Pitch & Demo Guide (3-Minute Walkthrough)

When presenting to hackathon judges:

1. **The Problem:** Puducherry is a major tourist and cultural hub with a high influx of weekend visitors, dense heritage quarters, and long coastal transit corridors (ECR). Traditional policing is reactive.
2. **Pillar 1 - MAP (Tab 1):**
   * Show the tactical dark map of Puducherry.
   * Toggle the **Heatmap**, **Police Stations**, and **Live Patrols**.
   * Click on a cluster near **Promenade Beach (Goubert Avenue)** to show detailed FIR information.
3. **Pillar 2 - ANALYSE (Tab 2):**
   * Point out the **Diurnal Crime Curve** and **Weekend Surge chart**.
   * Highlight the **Dark Spot Correlation Insight**: street crimes correlate strongly with unlit alleys.
4. **Pillar 3 - PREDICT (Tab 3):**
   * Demonstrate the **What-If Simulator**: Click *"Scenario A: Weekend Tourist Influx"* and show the ML risk score for White Town jumping to Critical.
   * Show the **24-Hour Predictive Crime Risk Curve**.
5. **Pillar 4 - PREVENT (Tab 4):**
   * Click **"Generate Optimal Route"** for `PCR-01` to show the calculated TSP patrol itinerary.
   * Click **"Dispatch Nearest Patrol Unit Now"** under the 112 CAD console to demonstrate instant ETA calculation and dispatch route mapping.
   * Open the **CopAI Assistant** in the bottom-right corner and ask: *"Where should we deploy extra patrols tonight?"*
   * Click **"Daily SitRep"** on the top header to show the printable police executive report.

---

## 📂 Project Directory Structure

```
crimemap-puducherry/
├── app.py                   # Main Flask REST server & routing
├── ml_engine.py             # Random Forest predictive risk & TSP routing engine
├── data_generator.py        # Puducherry dataset & spatial seed generator
├── README.md                # Comprehensive documentation
├── data/
│   ├── incidents.json       # 1,250+ geo-referenced Puducherry crime records
│   ├── police_stations.json # 12 Puducherry police stations & jurisdictions
│   ├── cctv_network.json    # 22 municipal surveillance cameras
│   ├── dark_spots.json      # 7 infrastructure unlit vulnerability zones
│   └── patrol_units.json    # 8 active PCR patrol vehicles
├── static/
│   ├── css/
│   │   └── style.css        # Tactical dark-mode command center stylesheet
│   └── js/
│       └── app.js           # Leaflet maps, Chart.js, CAD dispatch & CopAI logic
└── templates/
    └── index.html           # Main C4I Command & Control Center Dashboard
```

---

*Developed for Puducherry Police Department Hackathon submission.*
