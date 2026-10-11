"""
Puducherry CRIMEMAP - Machine Learning & Predictive Risk Analytics Engine
Provides spatio-temporal risk forecasting, what-if scenario simulations,
and decision-support patrol optimization algorithms.
"""

import json
import math
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

class CrimePredictiveEngine:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.load_data()
        self.build_sector_definitions()
        self.train_risk_model()

    def load_data(self):
        with open(self.data_dir / "incidents.json", "r", encoding="utf-8") as f:
            self.incidents = json.load(f)
        with open(self.data_dir / "police_stations.json", "r", encoding="utf-8") as f:
            self.stations = json.load(f)
        with open(self.data_dir / "cctv_network.json", "r", encoding="utf-8") as f:
            self.cctvs = json.load(f)
        with open(self.data_dir / "dark_spots.json", "r", encoding="utf-8") as f:
            self.dark_spots = json.load(f)
        with open(self.data_dir / "patrol_units.json", "r", encoding="utf-8") as f:
            self.patrol_units = json.load(f)

    def build_sector_definitions(self):
        """Divides Puducherry into tactical operational sectors."""
        self.sectors = [
            {
                "id": "SEC-01",
                "name": "White Town & Promenade Coastal",
                "center_lat": 11.9335,
                "center_lng": 79.8350,
                "radius_km": 1.2,
                "tourist_factor": 1.8,
                "nightlife_factor": 1.9,
                "station": "Grand Bazaar Police Station",
                "primary_threat": "Tourist Harassment & Snatching"
            },
            {
                "id": "SEC-02",
                "name": "Grand Bazaar & Commercial Core",
                "center_lat": 11.9355,
                "center_lng": 79.8285,
                "radius_km": 1.0,
                "tourist_factor": 1.5,
                "nightlife_factor": 1.3,
                "station": "Grand Bazaar Police Station",
                "primary_threat": "Two-Wheeler Theft & Extortion"
            },
            {
                "id": "SEC-03",
                "name": "New Bus Stand & Transit Belt",
                "center_lat": 11.9270,
                "center_lng": 79.8185,
                "radius_km": 1.4,
                "tourist_factor": 1.4,
                "nightlife_factor": 1.6,
                "station": "Orleanpet Police Station",
                "primary_threat": "Pickpocketing & Night Robbery"
            },
            {
                "id": "SEC-04",
                "name": "Lawspet & Airport Urban Ring",
                "center_lat": 11.9640,
                "center_lng": 79.8180,
                "radius_km": 2.0,
                "tourist_factor": 0.8,
                "nightlife_factor": 1.1,
                "station": "Lawspet Police Station",
                "primary_threat": "Residential House Burglary"
            },
            {
                "id": "SEC-05",
                "name": "Muthialpet & ECR Toll Checkpost",
                "center_lat": 11.9560,
                "center_lng": 79.8330,
                "radius_km": 1.8,
                "tourist_factor": 1.3,
                "nightlife_factor": 1.7,
                "station": "Muthialpet Police Station",
                "primary_threat": "Rash Driving & NDPS Contraband"
            },
            {
                "id": "SEC-06",
                "name": "Reddiarpalayam & West Suburban",
                "center_lat": 11.9360,
                "center_lng": 79.7940,
                "radius_km": 2.2,
                "tourist_factor": 0.6,
                "nightlife_factor": 1.0,
                "station": "Reddiarpalayam Police Station",
                "primary_threat": "Burglary & Vehicle Theft"
            },
            {
                "id": "SEC-07",
                "name": "Gorimedu JIPMER & D'Nagar Zone",
                "center_lat": 11.9520,
                "center_lng": 79.8020,
                "radius_km": 1.6,
                "tourist_factor": 0.9,
                "nightlife_factor": 1.1,
                "station": "D'Nagar Police Station",
                "primary_threat": "Public Brawls & Student Clashes"
            },
            {
                "id": "SEC-08",
                "name": "Mudaliarpet 100-Ft Corridor",
                "center_lat": 11.9180,
                "center_lng": 79.8130,
                "radius_km": 1.8,
                "tourist_factor": 0.7,
                "nightlife_factor": 1.3,
                "station": "Mudaliarpet Police Station",
                "primary_threat": "Assault & Traffic Incidents"
            },
            {
                "id": "SEC-09",
                "name": "Ariyankuppam & Chunnambar Coastal",
                "center_lat": 11.8900,
                "center_lng": 79.8100,
                "radius_km": 3.0,
                "tourist_factor": 1.6,
                "nightlife_factor": 1.2,
                "station": "Ariyankuppam Police Station",
                "primary_threat": "Coastal NDPS & Snatching"
            },
            {
                "id": "SEC-10",
                "name": "Villianur Heritage & Rural Belt",
                "center_lat": 11.9160,
                "center_lng": 79.7570,
                "radius_km": 3.5,
                "tourist_factor": 0.9,
                "nightlife_factor": 0.8,
                "station": "Villianur Police Station",
                "primary_threat": "Temple Crowd Thefts & Robbery"
            },
            {
                "id": "SEC-11",
                "name": "Kalapet & Pondicherry University",
                "center_lat": 12.0280,
                "center_lng": 79.8560,
                "radius_km": 3.2,
                "tourist_factor": 1.4,
                "nightlife_factor": 1.5,
                "station": "Kalapet Police Station",
                "primary_threat": "Highway Speeding & NDPS Activity"
            },
            {
                "id": "SEC-12",
                "name": "Bahour Agrarian South Border",
                "center_lat": 11.8020,
                "center_lng": 79.7420,
                "radius_km": 4.5,
                "tourist_factor": 0.4,
                "nightlife_factor": 0.6,
                "station": "Bahour Police Station",
                "primary_threat": "Property Trespass & Disputes"
            }
        ]

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculates distance between two coordinates in kilometers."""
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def train_risk_model(self):
        """Trains a machine learning regression model for spatio-temporal risk."""
        # Calculate historical incident densities per sector
        for sector in self.sectors:
            sec_incidents = [
                inc for inc in self.incidents
                if self._haversine_distance(sector["center_lat"], sector["center_lng"], inc["lat"], inc["lng"]) <= sector["radius_km"]
            ]
            sector["total_incidents"] = len(sec_incidents)
            sector["mean_weight"] = np.mean([inc.get("weight", 3) for inc in sec_incidents]) if sec_incidents else 3.0
            
            # Count local dark spots and CCTVs
            sector["dark_spot_count"] = sum(
                1 for ds in self.dark_spots
                if self._haversine_distance(sector["center_lat"], sector["center_lng"], ds["lat"], ds["lng"]) <= sector["radius_km"] + 0.5
            )
            sector["cctv_count"] = sum(
                1 for cam in self.cctvs
                if self._haversine_distance(sector["center_lat"], sector["center_lng"], cam["lat"], cam["lng"]) <= sector["radius_km"] + 0.5
            )

        # Build synthetic training samples across all 24 hours x 7 days x 12 sectors
        X = []
        y = []
        for sec_idx, sec in enumerate(self.sectors):
            base_vol = (sec["total_incidents"] / max(1, len(self.incidents))) * 100.0
            for hour in range(24):
                for dow in range(7):
                    is_weekend = 1 if dow in [5, 6] else 0
                    sin_hour = math.sin(2 * math.pi * hour / 24)
                    cos_hour = math.cos(2 * math.pi * hour / 24)
                    sin_dow = math.sin(2 * math.pi * dow / 7)
                    cos_dow = math.cos(2 * math.pi * dow / 7)
                    
                    # Risk heuristic ground-truth based on local crime behavior
                    night_mult = 1.6 if (hour >= 21 or hour <= 4) else (0.7 if 6 <= hour <= 15 else 1.2)
                    weekend_mult = sec["tourist_factor"] if is_weekend else 1.0
                    infra_mult = 1.0 + (sec["dark_spot_count"] * 0.12) - (sec["cctv_count"] * 0.05)
                    
                    calculated_risk = base_vol * night_mult * weekend_mult * infra_mult * 0.15
                    # Bound risk between 0.1 and 0.98
                    normalized_risk = min(0.98, max(0.12, calculated_risk))
                    
                    features = [
                        sec_idx,
                        hour,
                        sin_hour,
                        cos_hour,
                        dow,
                        sin_dow,
                        cos_dow,
                        is_weekend,
                        sec["tourist_factor"],
                        sec["nightlife_factor"],
                        sec["dark_spot_count"],
                        sec["cctv_count"]
                    ]
                    X.append(features)
                    y.append(normalized_risk)

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        self.rf_model = RandomForestRegressor(n_estimators=45, random_state=42)
        self.rf_model.fit(X_scaled, y)
        print("Puducherry Crime ML Model trained successfully.")

    def predict_sector_risks(self, target_hour: int, target_dow: int, scenario_params: dict = None):
        """
        Predicts crime risk score (0-100) and threat levels for each sector
        under baseline or custom simulation conditions.
        """
        if scenario_params is None:
            scenario_params = {
                "tourist_surge": 1.0,
                "dark_spot_factor": 1.0,
                "patrol_coverage": 1.0,
                "cctv_operational": 1.0
            }

        is_weekend = 1 if target_dow in [5, 6] else 0
        sin_hour = math.sin(2 * math.pi * target_hour / 24)
        cos_hour = math.cos(2 * math.pi * target_hour / 24)
        sin_dow = math.sin(2 * math.pi * target_dow / 7)
        cos_dow = math.cos(2 * math.pi * target_dow / 7)

        predictions = []
        for sec_idx, sec in enumerate(self.sectors):
            # Apply scenario modifiers
            adj_dark_spots = sec["dark_spot_count"] * scenario_params.get("dark_spot_factor", 1.0)
            adj_cctv = sec["cctv_count"] * scenario_params.get("cctv_operational", 1.0)
            adj_tourist = sec["tourist_factor"] * scenario_params.get("tourist_surge", 1.0)
            
            features = [
                sec_idx,
                target_hour,
                sin_hour,
                cos_hour,
                target_dow,
                sin_dow,
                cos_dow,
                is_weekend,
                adj_tourist,
                sec["nightlife_factor"],
                adj_dark_spots,
                adj_cctv
            ]
            
            scaled_feat = self.scaler.transform([features])
            base_pred = float(self.rf_model.predict(scaled_feat)[0])
            
            # Patrol deterrence modifier
            patrol_mod = 1.0 - ((scenario_params.get("patrol_coverage", 1.0) - 1.0) * 0.35)
            final_risk = min(0.99, max(0.08, base_pred * patrol_mod))
            risk_score = round(final_risk * 100, 1)

            # Categorize alert status
            if risk_score >= 70:
                threat_level = "CRITICAL"
                color = "#EF4444"
                action = "Deploy Fixed Picket & Immediate PCR Interceptor"
            elif risk_score >= 50:
                threat_level = "HIGH"
                color = "#F59E0B"
                action = "Intensify Cheetah Mobile Patrols & Dark Alley Checks"
            elif risk_score >= 30:
                threat_level = "MODERATE"
                color = "#3B82F6"
                action = "Routine Vehicle Frisking & CCTV Surveillance"
            else:
                threat_level = "LOW"
                color = "#10B981"
                action = "Standard Area Vigilance"

            predictions.append({
                "sector_id": sec["id"],
                "sector_name": sec["name"],
                "police_station": sec["station"],
                "lat": sec["center_lat"],
                "lng": sec["center_lng"],
                "radius_km": sec["radius_km"],
                "risk_score": risk_score,
                "threat_level": threat_level,
                "color": color,
                "recommended_action": action,
                "primary_threat": sec["primary_threat"]
            })

        # Sort descending by risk score
        predictions.sort(key=lambda x: x["risk_score"], reverse=True)
        return predictions

    def get_24h_risk_forecast(self, target_dow: int = 5):
        """Returns 24-hour crime trend curve across Puducherry."""
        hourly_forecast = []
        for h in range(24):
            sec_preds = self.predict_sector_risks(target_hour=h, target_dow=target_dow)
            avg_risk = round(float(np.mean([p["risk_score"] for p in sec_preds])), 1)
            max_risk = round(float(np.max([p["risk_score"] for p in sec_preds])), 1)
            highest_risk_sec = sec_preds[0]["sector_name"]
            
            hourly_forecast.append({
                "hour": h,
                "time_label": f"{h:02d}:00",
                "average_city_risk": avg_risk,
                "peak_sector_risk": max_risk,
                "critical_sector": highest_risk_sec
            })
        return hourly_forecast

    def optimize_patrol_route(self, patrol_id: str = "PCR-01"):
        """
        Decision support: Computes the optimal patrol itinerary for a PCR van
        by solving TSP / Nearest Neighbor over the top predicted danger zones.
        """
        # Find patrol starting coordinates
        p_unit = next((p for p in self.patrol_units if p["id"] == patrol_id), self.patrol_units[0])
        start_coord = (p_unit["lat"], p_unit["lng"])

        # Pick top 6 vulnerable checkpoints based on recent predictions and dark spots
        top_sectors = self.predict_sector_risks(target_hour=22, target_dow=5)[:5]
        
        checkpoints = []
        for sec in top_sectors:
            checkpoints.append({
                "name": sec["sector_name"],
                "lat": sec["lat"],
                "lng": sec["lng"],
                "risk_score": sec["risk_score"],
                "threat": sec["primary_threat"],
                "station": sec["police_station"]
            })

        # Add top priority dark spots
        for ds in self.dark_spots[:2]:
            checkpoints.append({
                "name": f"Dark Spot: {ds['name']}",
                "lat": ds["lat"],
                "lng": ds["lng"],
                "risk_score": 85.0,
                "threat": "Infrastructure Blind Alley",
                "station": "Town Division"
            })

        # Greedy Nearest Neighbor routing
        unvisited = checkpoints.copy()
        current_loc = start_coord
        route = [{
            "step": 1,
            "name": f"Origin: {p_unit['callsign']} Base ({p_unit['sector']})",
            "lat": current_loc[0],
            "lng": current_loc[1],
            "cum_distance_km": 0.0,
            "eta_mins": 0,
            "action": "Patrol Rollout & Radio Check"
        }]

        total_distance = 0.0
        step_idx = 2
        while unvisited:
            # find closest
            unvisited.sort(key=lambda cp: self._haversine_distance(current_loc[0], current_loc[1], cp["lat"], cp["lng"]))
            nearest = unvisited.pop(0)
            dist = self._haversine_distance(current_loc[0], current_loc[1], nearest["lat"], nearest["lng"])
            total_distance += dist
            current_loc = (nearest["lat"], nearest["lng"])
            eta = round(total_distance * 2.8) # ~25 km/h urban speed
            
            route.append({
                "step": step_idx,
                "name": nearest["name"],
                "lat": nearest["lat"],
                "lng": nearest["lng"],
                "threat": nearest["threat"],
                "risk_score": nearest["risk_score"],
                "distance_from_prev_km": round(dist, 2),
                "cum_distance_km": round(total_distance, 2),
                "eta_mins": eta,
                "action": f"15-Min Strobe Vigilance & Pedestrian Frisking"
            })
            step_idx += 1

        return {
            "patrol_id": p_unit["id"],
            "callsign": p_unit["callsign"],
            "officer": p_unit["officer"],
            "vehicle": p_unit["vehicle"],
            "total_route_distance_km": round(total_distance, 2),
            "estimated_circuit_mins": round(total_distance * 2.8 + (len(route) - 1) * 15),
            "checkpoints": route
        }

    def dispatch_nearest_unit(self, incident_lat: float, incident_lng: float, emergency_type: str = "Urgent 112 Call"):
        """
        CAD (Computer Aided Dispatch): Finds the closest patrol unit,
        computes ETA, and returns dispatch payload with routing line.
        """
        ranked_units = []
        for unit in self.patrol_units:
            dist = self._haversine_distance(unit["lat"], unit["lng"], incident_lat, incident_lng)
            # Urban speed assumption: 35 km/h for urgent response
            eta_mins = max(2, round((dist / 35.0) * 60))
            ranked_units.append({
                "unit": unit,
                "distance_km": round(dist, 2),
                "eta_mins": eta_mins
            })

        ranked_units.sort(key=lambda x: x["distance_km"])
        best = ranked_units[0]

        # Generate waypoint interpolation for map trajectory
        steps = 5
        trajectory = []
        for i in range(steps + 1):
            t = i / steps
            interp_lat = best["unit"]["lat"] + t * (incident_lat - best["unit"]["lat"])
            interp_lng = best["unit"]["lng"] + t * (incident_lng - best["unit"]["lng"])
            trajectory.append([round(interp_lat, 5), round(interp_lng, 5)])

        return {
            "dispatched_unit": best["unit"],
            "distance_km": best["distance_km"],
            "eta_mins": best["eta_mins"],
            "emergency_type": emergency_type,
            "target_coordinates": {"lat": incident_lat, "lng": incident_lng},
            "trajectory": trajectory,
            "nearby_backup": ranked_units[1]["unit"] if len(ranked_units) > 1 else None
        }
