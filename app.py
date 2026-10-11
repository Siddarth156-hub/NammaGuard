"""
Puducherry CRIMEMAP - Geospatial Intelligence, Analytics and Decision-Support System
Main Flask Application Server
"""

import json
import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from ml_engine import CrimePredictiveEngine
from notifier import (
    send_fir_notification,
    send_sos_notification,
    load_config as load_email_cfg,
    get_recent_email_logs
)

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

DATA_DIR = Path(__file__).parent / "data"
ml_engine = CrimePredictiveEngine(DATA_DIR)


def load_json(filename):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename, data):
    with open(DATA_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/incidents", methods=["GET"])
def get_incidents():
    incidents = load_json("incidents.json")
    
    # Query filters
    category = request.args.get("category")
    station = request.args.get("station")
    severity = request.args.get("severity")
    status = request.args.get("status")
    hour_min = request.args.get("hour_min", type=int)
    hour_max = request.args.get("hour_max", type=int)
    limit = request.args.get("limit", default=1000, type=int)

    filtered = incidents
    if category and category != "All":
        filtered = [x for x in filtered if x.get("category") == category]
    if station and station != "All":
        filtered = [x for x in filtered if x.get("police_station") == station]
    if severity and severity != "All":
        filtered = [x for x in filtered if x.get("severity") == severity]
    if status and status != "All":
        filtered = [x for x in filtered if x.get("status") == status]
    if hour_min is not None and hour_max is not None:
        if hour_min <= hour_max:
            filtered = [x for x in filtered if hour_min <= x.get("hour", 0) <= hour_max]
        else: # Overnight wrap around (e.g. 22 to 4)
            filtered = [x for x in filtered if x.get("hour", 0) >= hour_min or x.get("hour", 0) <= hour_max]

    return jsonify({
        "total_matches": len(filtered),
        "data": filtered[:limit]
    })


@app.route("/api/incidents", methods=["POST"])
def create_incident():
    payload = request.get_json(force=True)
    incidents = load_json("incidents.json")
    
    now = datetime.datetime.now()
    new_fir_id = f"PY-2026-FIR-{len(incidents) + 1001}"
    
    new_record = {
        "id": new_fir_id,
        "title": payload.get("title", "Reported Incident"),
        "category": payload.get("category", "General Incident"),
        "ipc_section": payload.get("ipc_section", "IPC 379"),
        "severity": payload.get("severity", "High"),
        "weight": 3 if payload.get("severity") == "High" else (4 if payload.get("severity") == "Critical" else 2),
        "police_station": payload.get("police_station", "Grand Bazaar Police Station"),
        "location_name": payload.get("location_name", "Puducherry"),
        "lat": float(payload.get("lat", 11.9338)),
        "lng": float(payload.get("lng", 79.8326)),
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "hour": now.hour,
        "day_of_week": now.strftime("%A"),
        "is_weekend": now.weekday() >= 5,
        "source": "nammaportal_web",
        "status": "Under Investigation",
        "lighting": payload.get("lighting", "Commercial Bright"),
        "response_time_mins": 5,
        "description": payload.get("description", "Immediate response unit dispatched.")
    }
    
    incidents.insert(0, new_record)
    save_json("incidents.json", incidents)
    
    # Send email notification to siddarthssakthivel@gmail.com
    email_status = send_fir_notification(new_record)
    
    return jsonify({
        "status": "success",
        "message": f"FIR registered successfully under {new_fir_id}",
        "record": new_record,
        "email_status": email_status
    }), 201


@app.route("/api/stations", methods=["GET"])
def get_stations():
    stations = load_json("police_stations.json")
    return jsonify(stations)


@app.route("/api/cctvs", methods=["GET"])
def get_cctvs():
    cctvs = load_json("cctv_network.json")
    return jsonify(cctvs)


@app.route("/api/darkspots", methods=["GET"])
def get_darkspots():
    dark_spots = load_json("dark_spots.json")
    return jsonify(dark_spots)


@app.route("/api/patrols", methods=["GET"])
def get_patrols():
    patrols = load_json("patrol_units.json")
    return jsonify(patrols)


@app.route("/api/hotspots", methods=["GET"])
def get_hotspots():
    hotspots = load_json("hotspots.json")
    return jsonify(hotspots)


@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    incidents = load_json("incidents.json")
    total = len(incidents)
    
    # Severity & Status breakdown
    critical_count = sum(1 for x in incidents if x.get("severity") == "Critical")
    resolved_count = sum(1 for x in incidents if x.get("status") in ["Chargesheet Filed", "Arrested", "Closed", "Dispatched & Resolved"])
    ongoing_count = sum(1 for x in incidents if x.get("status") in ["Under Investigation", "Patrol Dispatched", "Pending Inquiry", "In Progress"])
    
    # Cases filed specifically through NammaGuard web portal
    web_portal_new = sum(1 for x in incidents if x.get("source") == "nammaportal_web")
    web_filed_count = 142 + web_portal_new
    
    resolution_rate = round((resolved_count / total * 100), 1) if total else 0
    mean_resp_time = round(sum(x.get("response_time_mins", 10) for x in incidents) / max(1, total), 1)
    
    # Hourly distribution
    hourly_counts = {h: 0 for h in range(24)}
    for inc in incidents:
        hourly_counts[inc.get("hour", 0)] = hourly_counts.get(inc.get("hour", 0), 0) + 1

    # Day of week
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_counts = {d: 0 for d in dow_order}
    for inc in incidents:
        dow = inc.get("day_of_week")
        if dow in dow_counts:
            dow_counts[dow] += 1

    # Category counts
    cat_counts = {}
    for inc in incidents:
        c = inc.get("category", "Other")
        cat_counts[c] = cat_counts.get(c, 0) + 1

    # Police station counts
    station_counts = {}
    for inc in incidents:
        ps = inc.get("police_station", "Unknown")
        station_counts[ps] = station_counts.get(ps, 0) + 1
    sorted_stations = sorted(station_counts.items(), key=lambda x: x[1], reverse=True)

    # Lighting condition breakdown
    lighting_counts = {}
    for inc in incidents:
        l = inc.get("lighting", "Standard")
        lighting_counts[l] = lighting_counts.get(l, 0) + 1

    return jsonify({
        "summary": {
            "total_incidents": total,
            "web_cases_filed": web_filed_count,
            "ongoing_cases": ongoing_count,
            "critical_cases": critical_count,
            "resolved_count": resolved_count,
            "resolution_rate_pct": resolution_rate,
            "mean_response_time_mins": mean_resp_time,
            "active_patrol_count": 8,
            "active_cctv_count": 22,
            "identified_dark_spots": 7
        },
        "hourly": hourly_counts,
        "day_of_week": dow_counts,
        "categories": cat_counts,
        "top_police_stations": sorted_stations,
        "lighting_distribution": lighting_counts
    })


@app.route("/api/predict", methods=["POST"])
def predict_risk():
    data = request.get_json(silent=True) or {}
    hour = data.get("hour", datetime.datetime.now().hour)
    dow = data.get("day_of_week", datetime.datetime.now().weekday())
    scenario = data.get("scenario", None)
    
    predictions = ml_engine.predict_sector_risks(target_hour=hour, target_dow=dow, scenario_params=scenario)
    return jsonify({
        "queried_hour": hour,
        "queried_dow": dow,
        "predictions": predictions
    })


@app.route("/api/forecast", methods=["GET"])
def get_forecast():
    dow = request.args.get("dow", default=datetime.datetime.now().weekday(), type=int)
    forecast = ml_engine.get_24h_risk_forecast(target_dow=dow)
    return jsonify(forecast)


@app.route("/api/simulate", methods=["POST"])
def simulate_scenario():
    data = request.get_json(force=True)
    scenario_type = data.get("type", "tourist_surge")
    
    hour = data.get("hour", 22)
    dow = data.get("dow", 5) # Saturday default
    
    # Parameter variations
    scenarios = {
        "weekend_tourist_surge": {
            "name": "Weekend Tourist & Promenade Rush",
            "description": "60% influx of tourists in White Town & beaches, packed bars along Bussy St, heightened evening risk.",
            "params": {"tourist_surge": 1.7, "dark_spot_factor": 1.1, "patrol_coverage": 1.0, "cctv_operational": 1.0}
        },
        "night_burglary_spree": {
            "name": "Monsoon Darkness & Residential Burglary Threat",
            "description": "Power cuts elevate dark spot vulnerability by 80% across Lawspet and Reddiarpalayam residential sectors.",
            "params": {"tourist_surge": 0.8, "dark_spot_factor": 1.8, "patrol_coverage": 0.9, "cctv_operational": 0.7}
        },
        "ecr_midnight_speeding": {
            "name": "ECR Midnight Drag Racing & NDPS Corridor",
            "description": "Weekend late-night traffic on ECR connecting Chennai to Pondy with spike in NDPS smuggling and speed violations.",
            "params": {"tourist_surge": 1.4, "dark_spot_factor": 1.5, "patrol_coverage": 0.85, "cctv_operational": 0.9}
        },
        "enhanced_saturation_patrol": {
            "name": "Operation Suraksha: Full Tactical Patrol Saturation",
            "description": "Police force mobilization: 60% boost in active Cheetah bikes, 100% CCTV uptime, mobile barricades.",
            "params": {"tourist_surge": 1.0, "dark_spot_factor": 0.7, "patrol_coverage": 1.6, "cctv_operational": 1.0}
        }
    }
    
    selected_scen = scenarios.get(scenario_type, scenarios["weekend_tourist_surge"])
    baseline_predictions = ml_engine.predict_sector_risks(target_hour=hour, target_dow=dow)
    simulated_predictions = ml_engine.predict_sector_risks(target_hour=hour, target_dow=dow, scenario_params=selected_scen["params"])
    
    # Calculate deltas
    comparison = []
    for base, sim in zip(baseline_predictions, simulated_predictions):
        delta = round(sim["risk_score"] - base["risk_score"], 1)
        comparison.append({
            "sector_name": base["sector_name"],
            "baseline_risk": base["risk_score"],
            "simulated_risk": sim["risk_score"],
            "delta": delta,
            "threat_level": sim["threat_level"],
            "color": sim["color"],
            "recommended_action": sim["recommended_action"]
        })
        
    return jsonify({
        "scenario_name": selected_scen["name"],
        "description": selected_scen["description"],
        "comparison": comparison,
        "simulated_predictions": simulated_predictions
    })


@app.route("/api/optimize-patrol", methods=["POST"])
def optimize_patrol():
    data = request.get_json(silent=True) or {}
    patrol_id = data.get("patrol_id", "PCR-01")
    plan = ml_engine.optimize_patrol_route(patrol_id=patrol_id)
    return jsonify(plan)


@app.route("/api/dispatch", methods=["POST"])
def dispatch_unit():
    data = request.get_json(force=True)
    lat = float(data.get("lat", 11.9328))
    lng = float(data.get("lng", 79.8352))
    emergency_type = data.get("emergency_type", "Priority 112 SOS Call")
    
    dispatch_plan = ml_engine.dispatch_nearest_unit(incident_lat=lat, incident_lng=lng, emergency_type=emergency_type)
    
    # Send high-priority 112 SOS email alert to siddarthssakthivel@gmail.com
    email_status = send_sos_notification(dispatch_plan)
    dispatch_plan["email_status"] = email_status
    
    return jsonify(dispatch_plan)


ADMIN_PIN = "1122"


@app.route("/api/email-config", methods=["GET", "POST"])
def email_config_endpoint():
    if request.method == "POST":
        return jsonify({
            "status": "error",
            "message": "Please update email settings using Vercel environment variables."
        }), 400

    pin = request.args.get("pin")

    if pin != ADMIN_PIN:
        return jsonify({
            "error": "Unauthorized. Valid Officer Security PIN required."
        }), 401

    return jsonify(load_email_cfg())
    if request.method == "POST":
        data = request.get_json(force=True)
        cfg = load_email_cfg()
        if "target_email" in data and data["target_email"]:
            cfg["target_email"] = data["target_email"].strip()
        if "smtp_user" in data:
            cfg["smtp_user"] = data["smtp_user"].strip()
        if "smtp_pass" in data:
            cfg["smtp_pass"] = data["smtp_pass"].strip()
        save_email_cfg(cfg)
        return jsonify({"status": "success", "config": cfg})
    return jsonify(load_email_cfg())


@app.route("/api/email-logs", methods=["GET"])
def email_logs_endpoint():
    pin = request.args.get("pin")
    if pin != ADMIN_PIN:
        return jsonify({"error": "Unauthorized. Valid Officer Security PIN required."}), 401
    logs = get_recent_email_logs()
    return jsonify({"logs": logs})


@app.route("/api/copilot", methods=["POST"])
def copilot_assistant():
    data = request.get_json(force=True)
    query = data.get("query", "").lower()
    
    # Intelligent domain knowledge responder for Puducherry Police C4I
    if "patrol" in query or "deploy" in query or "pcr" in query:
        response_text = (
            "**Tactical Patrol Recommendation for Puducherry Police:**\n\n"
            "• **Immediate Deployment Priority:** Concentrated night patrols (21:00 - 03:00) along *White Town / Goubert Avenue* and *ECR Tollgate Muthialpet*.\n"
            "• **Unit Allocation:** Dispatch **PCR-01 (Promenade Falcon)** to White Town and assign **Cheetah Motorcycle Units** to inner French Quarter alleys (Rue Suffren & Rue Dumas).\n"
            "• **Suburban Checkpoints:** Establish static vehicle frisking barricades at *Indira Gandhi Square* and *Lawspet Airport Road* from 23:00 onwards to curb residential burglary attempts."
        )
    elif "snatch" in query or "theft" in query or "two-wheeler" in query:
        response_text = (
            "**Pattern Analysis: Snatching & Two-Wheeler Theft in Puducherry:**\n\n"
            "• **Primary Hotspots:** Goubert Market / JN Street, Sunday Market (MG Road), and New Bus Stand periphery.\n"
            "• **Peak Occurrence Window:** 17:30 to 21:30 during peak commercial shopping and tourist footfall.\n"
            "• **Modus Operandi:** 2-wheeler duos targeting pedestrian shoppers and beach tourists carrying unzipped bags.\n"
            "• **Action Plan:** Deploy plainclothes shadow officers near Nehru Street crossings and activate ANPR cameras CAM-04 & CAM-05."
        )
    elif "dark" in query or "light" in query or "infrastructure" in query:
        response_text = (
            "**Puducherry Infrastructure Dark Spot Audit:**\n\n"
            "• **Top Vulnerability:** *New Bus Stand Rear Canal Walkway (DS-02)* with illuminance < 1.8 Lux. Linked to repeated night robbery and NDPS use.\n"
            "• *ECR Kanagachettikulam Coastal Stretch (DS-05)* has 600m without municipal illumination.\n"
            "• **Decision-Support Action:** Forwarded PWD Emergency Electrical Repair Tickets `#PWD-ELEC-2026-871` and `#840` for priority solar high-mast lamp installations."
        )
    elif "tourist" in query or "beach" in query or "promenade" in query:
        response_text = (
            "**Tourist Safety & Promenade Security Briefing:**\n\n"
            "• **Zone:** Rock Beach & Promenade (1.5 km stretch along Goubert Avenue).\n"
            "• **Key Incidents:** Eve-teasing after 22:00, unlicensed hawker harassment, intoxicated brawls near beach parking.\n"
            "• **Mitigation:** Strict enforcement of vehicle ban on Goubert Avenue from 18:00 - 06:00, continuous foot patrols by Coastal Police Station (Insp. Stalin), and operational PTZ surveillance via CAM-01 & CAM-02."
        )
    else:
        response_text = (
            "**Puducherry CRIMEMAP C4I Intelligence Assistant:**\n\n"
            "• The system monitors **12 tactical operational sectors** across Puducherry UT with **1,250+ geo-referenced crime records**.\n"
            "• **Current Overall Safety Index:** 81.4% Resolution Rate with a Mean Emergency Response Time of 8.6 minutes.\n"
            "• You can run What-If simulations in the **PREDICT** tab or trigger instant Computer-Aided Dispatch (CAD) in the **PREVENT** tab."
        )
        
    return jsonify({"answer": response_text})


@app.route("/api/report", methods=["GET"])
def daily_sitrep():
    analytics = get_analytics().json
    sectors = ml_engine.predict_sector_risks(target_hour=21, target_dow=5)
    
    sitrep = {
        "report_id": f"PUDU-SITREP-{datetime.datetime.now().strftime('%Y%m%d')}-01",
        "jurisdiction": "Government of Puducherry - Police Department C4I Center",
        "date_generated": datetime.datetime.now().strftime("%d %B %Y, %H:%M hrs"),
        "commanding_officer": "Senior Superintendent of Police (Law & Order)",
        "executive_summary": "Daily Law & Order Geospatial Situation Report and Tactical Resource Allocation Briefing.",
        "kpis": analytics["summary"],
        "critical_sectors": sectors[:3],
        "top_police_stations": analytics["top_police_stations"][:5],
        "tactical_directives": [
            "Maintain heightened mobile presence across White Town promenade during weekend evening hours.",
            "Conduct synchronized anti-burglary checks in Lawspet and Reddiarpalayam residential layouts from 01:00 to 04:30.",
            "Expedite PWD high-mast illumination repairs along the New Bus Stand canal strip (Ticket #PWD-ELEC-2026-871).",
            "Enforce strict 100% breathalyzer checkpoints at ECR Toll checkpost (Muthialpet)."
        ]
    }
    return jsonify(sitrep)


if __name__ == "__main__":
    print("Starting CRIMEMAP Puducherry Command & Control Center on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
