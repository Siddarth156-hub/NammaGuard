"""
Puducherry CRIMEMAP - Geospatial Intelligence Data Engine
Generates realistic, accurate geospatial crime records, police stations,
CCTV networks, dark spots, and patrol units across Puducherry UT.
"""

import json
import random
import datetime
from pathlib import Path

# Puducherry Police Stations
POLICE_STATIONS = [
    {
        "id": "PS-01",
        "name": "Grand Bazaar Police Station",
        "division": "Puducherry North",
        "lat": 11.9348,
        "lng": 79.8315,
        "contact": "+91 413 2224001",
        "inspector": "Insp. K. Rajendran",
        "coverage_sqkm": 4.2,
        "personnel": 48
    },
    {
        "id": "PS-02",
        "name": "Muthialpet Police Station",
        "division": "Puducherry North",
        "lat": 11.9515,
        "lng": 79.8302,
        "contact": "+91 413 2235002",
        "inspector": "Insp. M. Selvam",
        "coverage_sqkm": 6.8,
        "personnel": 42
    },
    {
        "id": "PS-03",
        "name": "Lawspet Police Station",
        "division": "Puducherry North",
        "lat": 11.9634,
        "lng": 79.8189,
        "contact": "+91 413 2252103",
        "inspector": "Insp. S. Baskaran",
        "coverage_sqkm": 9.5,
        "personnel": 52
    },
    {
        "id": "PS-04",
        "name": "Orleanpet Police Station",
        "division": "Puducherry South",
        "lat": 11.9288,
        "lng": 79.8205,
        "contact": "+91 413 2201304",
        "inspector": "Insp. V. Anbazhagan",
        "coverage_sqkm": 5.1,
        "personnel": 45
    },
    {
        "id": "PS-05",
        "name": "Mudaliarpet Police Station",
        "division": "Puducherry South",
        "lat": 11.9184,
        "lng": 79.8143,
        "contact": "+91 413 2356205",
        "inspector": "Insp. R. Murugan",
        "coverage_sqkm": 7.4,
        "personnel": 38
    },
    {
        "id": "PS-06",
        "name": "Reddiarpalayam Police Station",
        "division": "Puducherry West",
        "lat": 11.9351,
        "lng": 79.7942,
        "contact": "+91 413 2291406",
        "inspector": "Insp. D. Sivakumar",
        "coverage_sqkm": 8.9,
        "personnel": 40
    },
    {
        "id": "PS-07",
        "name": "D'Nagar Police Station",
        "division": "Puducherry West",
        "lat": 11.9472,
        "lng": 79.8080,
        "contact": "+91 413 2273107",
        "inspector": "Insp. P. Thanigaivel",
        "coverage_sqkm": 6.0,
        "personnel": 36
    },
    {
        "id": "PS-08",
        "name": "Villianur Police Station",
        "division": "Puducherry Rural",
        "lat": 11.9161,
        "lng": 79.7571,
        "contact": "+91 413 2666108",
        "inspector": "Insp. E. Jayakumar",
        "coverage_sqkm": 24.3,
        "personnel": 55
    },
    {
        "id": "PS-09",
        "name": "Ariyankuppam Police Station",
        "division": "Puducherry South",
        "lat": 11.8950,
        "lng": 79.8125,
        "contact": "+91 413 2600209",
        "inspector": "Insp. T. Manikandan",
        "coverage_sqkm": 14.8,
        "personnel": 41
    },
    {
        "id": "PS-10",
        "name": "Kalapet Police Station",
        "division": "Puducherry Coastal/North",
        "lat": 12.0305,
        "lng": 79.8596,
        "contact": "+91 413 2655110",
        "inspector": "Insp. B. Chandran",
        "coverage_sqkm": 18.2,
        "personnel": 39
    },
    {
        "id": "PS-11",
        "name": "Bahour Police Station",
        "division": "Puducherry South Rural",
        "lat": 11.8028,
        "lng": 79.7423,
        "contact": "+91 413 2633211",
        "inspector": "Insp. G. Vetrivel",
        "coverage_sqkm": 31.5,
        "personnel": 35
    },
    {
        "id": "PS-12",
        "name": "Coastal & Marine Police Station",
        "division": "Coastal Security",
        "lat": 11.9315,
        "lng": 79.8355,
        "contact": "+91 413 2229912",
        "inspector": "Insp. S. Stalin",
        "coverage_sqkm": 12.0,
        "personnel": 30
    }
]

# Real landmarks and hotspot zones in Puducherry
LOCAL_HOTSPOTS = [
    # White Town & Promenade
    {"name": "Goubert Avenue (Promenade Beach)", "lat": 11.9328, "lng": 79.8352, "ps": "Grand Bazaar Police Station", "risk": "High"},
    {"name": "Rock Beach French War Memorial", "lat": 11.9312, "lng": 79.8358, "ps": "Grand Bazaar Police Station", "risk": "Medium"},
    {"name": "Rue Romain Rolland & Suffren St", "lat": 11.9332, "lng": 79.8335, "ps": "Grand Bazaar Police Station", "risk": "Medium"},
    {"name": "Sri Aurobindo Ashram Zone", "lat": 11.9372, "lng": 79.8345, "ps": "Grand Bazaar Police Station", "risk": "Low"},
    {"name": "Goubert Market / Nehru Street", "lat": 11.9355, "lng": 79.8290, "ps": "Grand Bazaar Police Station", "risk": "Critical"},
    {"name": "Bussy Street (Lal Bahadur Shastri St)", "lat": 11.9305, "lng": 79.8285, "ps": "Grand Bazaar Police Station", "risk": "High"},
    {"name": "Sunday Market (MG Road Stretch)", "lat": 11.9360, "lng": 79.8270, "ps": "Grand Bazaar Police Station", "risk": "Critical"},
    # Commercial & Transit Hubs
    {"name": "New Bus Stand (Maraimalai Adigal)", "lat": 11.9275, "lng": 79.8180, "ps": "Orleanpet Police Station", "risk": "Critical"},
    {"name": "Puducherry Railway Station", "lat": 11.9242, "lng": 79.8268, "ps": "Orleanpet Police Station", "risk": "High"},
    {"name": "Indira Gandhi Square (400ft Ring)", "lat": 11.9320, "lng": 79.8050, "ps": "Orleanpet Police Station", "risk": "High"},
    {"name": "Nellithope Market Junction", "lat": 11.9310, "lng": 79.8140, "ps": "Orleanpet Police Station", "risk": "Medium"},
    {"name": "Mudaliarpet 100 Feet Road", "lat": 11.9165, "lng": 79.8120, "ps": "Mudaliarpet Police Station", "risk": "High"},
    {"name": "Cuddalore Road / Ariyankuppam Bridge", "lat": 11.8980, "lng": 79.8135, "ps": "Ariyankuppam Police Station", "risk": "Medium"},
    {"name": "Chunnambar Boat House Road", "lat": 11.8820, "lng": 79.8055, "ps": "Ariyankuppam Police Station", "risk": "High"},
    # Suburbs & Institutional
    {"name": "Lawspet Airport Road Junction", "lat": 11.9680, "lng": 79.8150, "ps": "Lawspet Police Station", "risk": "High"},
    {"name": "PIMS Hospital & Medical Zone", "lat": 12.0120, "lng": 79.8520, "ps": "Kalapet Police Station", "risk": "Medium"},
    {"name": "Pondicherry University Gate (Kalapet)", "lat": 12.0250, "lng": 79.8550, "ps": "Kalapet Police Station", "risk": "High"},
    {"name": "ECR Tollgate (Kottakkuppam Border)", "lat": 11.9620, "lng": 79.8370, "ps": "Muthialpet Police Station", "risk": "Critical"},
    {"name": "Muthialpet Clock Tower & Bazaar", "lat": 11.9540, "lng": 79.8310, "ps": "Muthialpet Police Station", "risk": "High"},
    {"name": "Gorimedu JIPMER Main Gate", "lat": 11.9540, "lng": 79.7990, "ps": "D'Nagar Police Station", "risk": "Medium"},
    {"name": "D'Nagar Housing Board Sector", "lat": 11.9450, "lng": 79.8090, "ps": "D'Nagar Police Station", "risk": "Medium"},
    {"name": "Reddiarpalayam Kanuvapet Junction", "lat": 11.9380, "lng": 79.7910, "ps": "Reddiarpalayam Police Station", "risk": "High"},
    {"name": "Villianur Temple Car Street & Bus Stand", "lat": 11.9150, "lng": 79.7560, "ps": "Villianur Police Station", "risk": "High"},
    {"name": "Ariyankuppam Veerampattinam Beach Rd", "lat": 11.8920, "lng": 79.8220, "ps": "Ariyankuppam Police Station", "risk": "Medium"},
    {"name": "Bahour Lake & Market Cross", "lat": 11.8010, "lng": 79.7410, "ps": "Bahour Police Station", "risk": "Low"}
]

CRIME_CATEGORIES = [
    {
        "category": "Two-Wheeler Theft & Snatching",
        "ipc": "IPC 379 / BNS 303",
        "severity": "High",
        "weight": 3,
        "peak_hours": [17, 18, 19, 20, 21, 22],
        "descriptions": [
            "Motorcycle stolen from public parking outside commercial complex",
            "Gold chain snatched from walking tourist by two suspects on bike",
            "Moped parked near market stolen using master key",
            "Handbag snatching targeting pedestrian near beach promenade"
        ]
    },
    {
        "category": "Night House Burglary & Trespass",
        "ipc": "IPC 457/380 / BNS 305",
        "severity": "Critical",
        "weight": 4,
        "peak_hours": [1, 2, 3, 4, 23],
        "descriptions": [
            "Locked independent residence broken into; gold and cash looted",
            "Front door lock dismantled while occupants were traveling",
            "Midnight trespass and theft of electronic equipment and cash",
            "Godown break-in and inventory theft"
        ]
    },
    {
        "category": "Tourist Harassment & Women Safety",
        "ipc": "IPC 354/509 / BNS 74/79",
        "severity": "High",
        "weight": 3,
        "peak_hours": [19, 20, 21, 22, 23, 0],
        "descriptions": [
            "Eve-teasing and stalking incident reported near beach promenade",
            "Unruly miscreants passing obscene remarks to foreign tourists",
            "Inappropriate behavior by motorcycle riders near heritage cafes",
            "Harassment and verbal altercation reported near unlit walkway"
        ]
    },
    {
        "category": "Alcohol-Fueled Brawl & Assault",
        "ipc": "IPC 160/324 / BNS 115",
        "severity": "High",
        "weight": 3,
        "peak_hours": [21, 22, 23, 0, 1],
        "descriptions": [
            "Violent clash between two groups outside resto-bar over parking dispute",
            "Intoxicated individuals engaged in brawl causing public nuisance",
            "Assault with blunt object following heated argument near tasmac shop",
            "Group clash causing disturbance to peace and minor injuries"
        ]
    },
    {
        "category": "Traffic Rash Driving & Hit-and-Run",
        "ipc": "IPC 279/337 / BNS 281",
        "severity": "Medium",
        "weight": 2,
        "peak_hours": [18, 19, 20, 21, 22, 23],
        "descriptions": [
            "Over-speeding car hit pedestrian near ECR junction and sped away",
            "Rash driving under influence of alcohol endangering public safety",
            "Multiple vehicle collision caused by illegal street drag racing",
            "Commercial mini-truck driving on wrong side causing collision"
        ]
    },
    {
        "category": "Narcotics (NDPS) Trafficking & Peddling",
        "ipc": "NDPS Act Sec 20/21",
        "severity": "Critical",
        "weight": 5,
        "peak_hours": [22, 23, 0, 1, 2],
        "descriptions": [
            "Interception of illicit ganja consignments intended for weekend parties",
            "Suspect apprehended carrying synthetic contraband pills near beach",
            "Drug peddling network busted operating near coastal guest houses",
            "Seizure of contraband packets during random midnight vehicle frisking"
        ]
    },
    {
        "category": "Cyber Crime & Financial Phishing",
        "ipc": "IT Act 66D / IPC 420",
        "severity": "Medium",
        "weight": 2,
        "peak_hours": [10, 11, 14, 15, 16],
        "descriptions": [
            "Senior citizen defrauded of Rs. 1.2 Lakh via fake electricity bill link",
            "Credit card cloning complaint registered from White Town boutique",
            "Digital arrest scam extorting money through fraudulent police threat",
            "Social media identity impersonation and extortion complaint"
        ]
    },
    {
        "category": "Commercial Extortion & Shop Vandalism",
        "ipc": "IPC 384/427 / BNS 308",
        "severity": "High",
        "weight": 3,
        "peak_hours": [15, 16, 17, 18, 19],
        "descriptions": [
            "Local goons demanding illegal 'mamool' protection money from vendor",
            "Vandalism of fruit stall following refusal to pay extortion sum",
            "Threats issued to hotel manager demanding free banquet services",
            "Damage to shop storefront following dispute between trade rivals"
        ]
    }
]

# CCTV Surveillance Network across Puducherry
CCTV_LOCATIONS = [
    {"id": "CAM-01", "name": "Goubert Ave North Watch", "lat": 11.9360, "lng": 79.8355, "type": "PTZ 360", "status": "ONLINE", "zone": "White Town"},
    {"id": "CAM-02", "name": "Rock Beach Memorial", "lat": 11.9315, "lng": 79.8358, "type": "Fixed 4K", "status": "ONLINE", "zone": "White Town"},
    {"id": "CAM-03", "name": "French Consulate Junction", "lat": 11.9325, "lng": 79.8340, "type": "PTZ 360", "status": "ONLINE", "zone": "White Town"},
    {"id": "CAM-04", "name": "Grand Bazaar East Gate", "lat": 11.9358, "lng": 79.8305, "type": "Dome ANPR", "status": "ONLINE", "zone": "Town Center"},
    {"id": "CAM-05", "name": "Nehru St / MG Road Signal", "lat": 11.9365, "lng": 79.8275, "type": "ANPR 4K", "status": "ONLINE", "zone": "Town Center"},
    {"id": "CAM-06", "name": "Bussy St Clock Crossing", "lat": 11.9300, "lng": 79.8270, "type": "PTZ 360", "status": "OFFLINE", "zone": "Town Center"},
    {"id": "CAM-07", "name": "New Bus Stand Bay 1", "lat": 11.9280, "lng": 79.8185, "type": "Dome ANPR", "status": "ONLINE", "zone": "Orleanpet"},
    {"id": "CAM-08", "name": "New Bus Stand Exit Road", "lat": 11.9270, "lng": 79.8175, "type": "Fixed 4K", "status": "ONLINE", "zone": "Orleanpet"},
    {"id": "CAM-09", "name": "Railway Station Main Porch", "lat": 11.9240, "lng": 79.8270, "type": "PTZ 360", "status": "ONLINE", "zone": "Railway Zone"},
    {"id": "CAM-10", "name": "Indira Gandhi Circle West", "lat": 11.9325, "lng": 79.8045, "type": "ANPR 4K", "status": "ONLINE", "zone": "Boulevard Ring"},
    {"id": "CAM-11", "name": "Nellithope Signal Post", "lat": 11.9315, "lng": 79.8135, "type": "Fixed 4K", "status": "MAINTENANCE", "zone": "Nellithope"},
    {"id": "CAM-12", "name": "100ft Road Rajiv Gandhi Sq", "lat": 11.9210, "lng": 79.8080, "type": "ANPR 4K", "status": "ONLINE", "zone": "Mudaliarpet"},
    {"id": "CAM-13", "name": "Lawspet Cluny Signal", "lat": 11.9620, "lng": 79.8210, "type": "Fixed 4K", "status": "ONLINE", "zone": "Lawspet"},
    {"id": "CAM-14", "name": "Airport Road Roundabout", "lat": 11.9690, "lng": 79.8140, "type": "PTZ 360", "status": "ONLINE", "zone": "Lawspet"},
    {"id": "CAM-15", "name": "ECR Toll Checkpost", "lat": 11.9630, "lng": 79.8375, "type": "ANPR 4K", "status": "ONLINE", "zone": "Muthialpet"},
    {"id": "CAM-16", "name": "Muthialpet Market Tower", "lat": 11.9535, "lng": 79.8305, "type": "Dome ANPR", "status": "ONLINE", "zone": "Muthialpet"},
    {"id": "CAM-17", "name": "JIPMER Gorimedu Main Gate", "lat": 11.9545, "lng": 79.7985, "type": "PTZ 360", "status": "ONLINE", "zone": "Gorimedu"},
    {"id": "CAM-18", "name": "Reddiarpalayam Main Jn", "lat": 11.9360, "lng": 79.7935, "type": "Fixed 4K", "status": "ONLINE", "zone": "Reddiarpalayam"},
    {"id": "CAM-19", "name": "Villianur Temple North Gate", "lat": 11.9165, "lng": 79.7565, "type": "Fixed 4K", "status": "ONLINE", "zone": "Villianur"},
    {"id": "CAM-20", "name": "Chunnambar Boat House Rd", "lat": 11.8830, "lng": 79.8060, "type": "PTZ 360", "status": "OFFLINE", "zone": "Ariyankuppam"},
    {"id": "CAM-21", "name": "Pondicherry Univ Gate 2", "lat": 12.0260, "lng": 79.8540, "type": "ANPR 4K", "status": "ONLINE", "zone": "Kalapet"},
    {"id": "CAM-22", "name": "Bahour Market Entrance", "lat": 11.8015, "lng": 79.7405, "type": "Fixed 4K", "status": "ONLINE", "zone": "Bahour"}
]

# Dark Spots and Vulnerability Infrastructure Audit
DARK_SPOTS = [
    {
        "id": "DS-01",
        "name": "Rue Suffren - Dumas Connecting Alley",
        "lat": 11.9320,
        "lng": 79.8342,
        "lux_level": 4.2,
        "defect": "Burnt street sodium lamps; obscured by banyan canopy",
        "crime_history": "3 Tourist bag snatches in past 45 days",
        "priority": "HIGH",
        "pwd_ticket": "PWD-ELEC-2026-904"
    },
    {
        "id": "DS-02",
        "name": "New Bus Stand Rear Canal Walkway",
        "lat": 11.9262,
        "lng": 79.8168,
        "lux_level": 1.8,
        "defect": "Missing poles, dense overgrowth, open drain",
        "crime_history": "NDPS use, mobile phone snatchings at night",
        "priority": "CRITICAL",
        "pwd_ticket": "PWD-ELEC-2026-871"
    },
    {
        "id": "DS-03",
        "name": "Railway Goods Shed Service Lane",
        "lat": 11.9225,
        "lng": 79.8252,
        "lux_level": 2.5,
        "defect": "Industrial stretch with unpowered high masts",
        "crime_history": "Assault and illegal liquor consumption",
        "priority": "HIGH",
        "pwd_ticket": "PWD-ELEC-2026-892"
    },
    {
        "id": "DS-04",
        "name": "Lawspet Navalar Nedunchezhian St Alley",
        "lat": 11.9655,
        "lng": 79.8170,
        "lux_level": 3.1,
        "defect": "Flickering halogen fixtures, dead bulb cluster",
        "crime_history": "House break-in attempts, 2-wheeler theft",
        "priority": "MEDIUM",
        "pwd_ticket": "PWD-ELEC-2026-915"
    },
    {
        "id": "DS-05",
        "name": "ECR Kanagachettikulam Beach Approach",
        "lat": 12.0280,
        "lng": 79.8610,
        "lux_level": 1.2,
        "defect": "Zero municipal lighting for 600m coastal stretch",
        "crime_history": "NDPS contraband exchange, harassment",
        "priority": "CRITICAL",
        "pwd_ticket": "PWD-ELEC-2026-840"
    },
    {
        "id": "DS-06",
        "name": "Ariyankuppam Veerampattinam Fishing Trail",
        "lat": 11.8900,
        "lng": 79.8190,
        "lux_level": 2.9,
        "defect": "Damaged cabling post-monsoon",
        "crime_history": "Eve teasing, drunken squabbles",
        "priority": "HIGH",
        "pwd_ticket": "PWD-ELEC-2026-888"
    },
    {
        "id": "DS-07",
        "name": "Villianur Bypass Dark Curve",
        "lat": 11.9120,
        "lng": 79.7620,
        "lux_level": 3.5,
        "defect": "Highway median lights non-functional",
        "crime_history": "Highway robbery, night hit-and-runs",
        "priority": "HIGH",
        "pwd_ticket": "PWD-ELEC-2026-930"
    }
]

# Live Police Patrol Units (PCR Vans / Cheetah Bikes)
PATROL_UNITS = [
    {
        "id": "PCR-01",
        "callsign": "Promenade Falcon",
        "vehicle": "Mahindra Bolero 4WD",
        "sector": "White Town & Promenade",
        "officer": "SI Arumugam & 2 Constables",
        "lat": 11.9335,
        "lng": 79.8348,
        "status": "ON_PATROL",
        "battery": 92,
        "speed_kmh": 24,
        "phone": "+91 94884 10001"
    },
    {
        "id": "PCR-02",
        "callsign": "Boulevard Eagle",
        "vehicle": "Tata Xenon Command",
        "sector": "Grand Bazaar & MG Road",
        "officer": "SI Karthikeyan & 2 Constables",
        "lat": 11.9350,
        "lng": 79.8280,
        "status": "ON_PATROL",
        "battery": 88,
        "speed_kmh": 18,
        "phone": "+91 94884 10002"
    },
    {
        "id": "PCR-03",
        "callsign": "Transit Guardian",
        "vehicle": "Mahindra Scorpio",
        "sector": "New Bus Stand & Railway Stn",
        "officer": "SI Vijayakumar & 2 Constables",
        "lat": 11.9265,
        "lng": 79.8210,
        "status": "RESPONDING",
        "battery": 79,
        "speed_kmh": 42,
        "phone": "+91 94884 10003"
    },
    {
        "id": "PCR-04",
        "callsign": "North Hawk",
        "vehicle": "Tata Xenon",
        "sector": "Lawspet & Airport Road",
        "officer": "SI Saravanan & 2 Constables",
        "lat": 11.9640,
        "lng": 79.8160,
        "status": "ON_PATROL",
        "battery": 95,
        "speed_kmh": 30,
        "phone": "+91 94884 10004"
    },
    {
        "id": "PCR-05",
        "callsign": "Coastal Interceptor",
        "vehicle": "Mahindra Bolero",
        "sector": "Muthialpet & ECR Toll",
        "officer": "SI Natarajan & 2 Constables",
        "lat": 11.9560,
        "lng": 79.8330,
        "status": "ON_PATROL",
        "battery": 84,
        "speed_kmh": 28,
        "phone": "+91 94884 10005"
    },
    {
        "id": "PCR-06",
        "callsign": "Rural Shield",
        "vehicle": "Tata Xenon 4WD",
        "sector": "Villianur & Suburbs",
        "officer": "SI Danassegarane & 2 Constables",
        "lat": 11.9170,
        "lng": 79.7600,
        "status": "STANDBY",
        "battery": 90,
        "speed_kmh": 0,
        "phone": "+91 94884 10006"
    },
    {
        "id": "PCR-07",
        "callsign": "South Tiger",
        "vehicle": "Mahindra Scorpio",
        "sector": "Ariyankuppam & Chunnambar",
        "officer": "SI Ganesan & 2 Constables",
        "lat": 11.8960,
        "lng": 79.8110,
        "status": "ON_PATROL",
        "battery": 87,
        "speed_kmh": 32,
        "phone": "+91 94884 10007"
    },
    {
        "id": "PCR-08",
        "callsign": "University Cheetah",
        "vehicle": "Bajaj Pulsar Interceptor (Bike 1 & 2)",
        "sector": "Kalapet & Pondy University",
        "officer": "HC Pandian & HC Kumar",
        "lat": 12.0270,
        "lng": 79.8560,
        "status": "ON_PATROL",
        "battery": 91,
        "speed_kmh": 35,
        "phone": "+91 94884 10008"
    }
]


def generate_crime_dataset(num_records=1200):
    """Generates realistic Puducherry crime dataset over 90 days with spatial/temporal weights."""
    random.seed(42)
    incidents = []
    
    base_date = datetime.datetime.now() - datetime.timedelta(days=90)
    
    for i in range(1, num_records + 1):
        # Pick hotspot with weighted risk
        hotspot = random.choice(LOCAL_HOTSPOTS)
        if hotspot["risk"] == "Critical" and random.random() < 0.4:
            pass
        
        # Pick crime category
        category_meta = random.choice(CRIME_CATEGORIES)
        
        # Determine realistic hour based on category's peak hours
        if random.random() < 0.75:
            hour = random.choice(category_meta["peak_hours"])
        else:
            hour = random.randint(0, 23)
            
        minute = random.randint(0, 59)
        days_offset = random.randint(0, 89)
        incident_time = base_date + datetime.timedelta(days=days_offset, hours=hour, minutes=minute)
        
        # Add slight jitter to coordinates (+/- 300 meters)
        lat_jitter = random.uniform(-0.0035, 0.0035)
        lng_jitter = random.uniform(-0.0035, 0.0035)
        
        incident_lat = round(hotspot["lat"] + lat_jitter, 5)
        incident_lng = round(hotspot["lng"] + lng_jitter, 5)
        
        # Status
        statuses = ["Chargesheet Filed", "Arrested", "Under Investigation", "Dispatched & Resolved", "Closed"]
        status_weights = [0.25, 0.30, 0.25, 0.15, 0.05]
        status = random.choices(statuses, weights=status_weights)[0]
        
        # Lighting condition
        if hour in [20, 21, 22, 23, 0, 1, 2, 3, 4]:
            lighting = random.choice(["Poorly Lit Alley", "Unlit Dark Spot", "Dim Sodium Lighting", "Commercial Bright"])
        else:
            lighting = "Bright Daylight"
            
        desc = random.choice(category_meta["descriptions"])
        
        incidents.append({
            "id": f"PY-2026-FIR-{1000 + i}",
            "title": f"{category_meta['category']} at {hotspot['name']}",
            "category": category_meta["category"],
            "ipc_section": category_meta["ipc"],
            "severity": category_meta["severity"],
            "weight": category_meta["weight"],
            "police_station": hotspot["ps"],
            "location_name": hotspot["name"],
            "lat": incident_lat,
            "lng": incident_lng,
            "timestamp": incident_time.strftime("%Y-%m-%d %H:%M:%S"),
            "date": incident_time.strftime("%Y-%m-%d"),
            "hour": hour,
            "day_of_week": incident_time.strftime("%A"),
            "is_weekend": incident_time.weekday() >= 5,
            "status": status,
            "lighting": lighting,
            "response_time_mins": random.randint(4, 18),
            "description": desc
        })
        
    return incidents


def save_initial_data(output_dir: Path):
    """Saves generated dataset, stations, CCTVs, dark spots, and patrols as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    incidents = generate_crime_dataset(1250)
    
    with open(output_dir / "incidents.json", "w", encoding="utf-8") as f:
        json.dump(incidents, f, indent=2)
        
    with open(output_dir / "police_stations.json", "w", encoding="utf-8") as f:
        json.dump(POLICE_STATIONS, f, indent=2)
        
    with open(output_dir / "cctv_network.json", "w", encoding="utf-8") as f:
        json.dump(CCTV_LOCATIONS, f, indent=2)
        
    with open(output_dir / "dark_spots.json", "w", encoding="utf-8") as f:
        json.dump(DARK_SPOTS, f, indent=2)
        
    with open(output_dir / "patrol_units.json", "w", encoding="utf-8") as f:
        json.dump(PATROL_UNITS, f, indent=2)
        
    print(f"Puducherry dataset generated: {len(incidents)} incidents saved to {output_dir}")


if __name__ == "__main__":
    base_path = Path(__file__).parent / "data"
    save_initial_data(base_path)
