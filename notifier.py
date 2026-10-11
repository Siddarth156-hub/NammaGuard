"""Email notifications for the CrimeMap/NammaGuard Flask backend.

Required environment variables:
  RESEND_API_KEY   API key from Resend
  ALERT_TO_EMAIL   recipient email address
  ALERT_FROM_EMAIL verified sender, e.g. CrimeMap <alerts@your-verified-domain.com>

For Resend testing, use the sender address allowed by your Resend account and
send only to an address permitted by that account. Never commit API keys.
"""
from dotenv import load_dotenv
load_dotenv()   
import datetime as dt
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
LOG_FILE = DATA_DIR / "email_notifications.log"
RESEND_ENDPOINT = "https://api.resend.com/emails"


def _log(event_type, recipient, subject, status, details=""):
    """Write a best-effort local log; logging must not crash notification flow."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        safe_details = str(details).replace("\n", " ")[:500]
        line = (
            f"[{dt.datetime.now(dt.timezone.utc).isoformat()}] "
            f"[{event_type}] TO: {recipient} | STATUS: {status} | "
            f"SUBJECT: {subject} | DETAILS: {safe_details}\n"
        )
        with LOG_FILE.open("a", encoding="utf-8") as log_file:
            log_file.write(line)
    except OSError as exc:
        print(f"Notification log write failed: {exc}")


def load_config():
    """Load settings from deployment environment variables."""
    return {
        "target_email": os.getenv("ALERT_TO_EMAIL", "").strip(),
        "sender_email": os.getenv("ALERT_FROM_EMAIL", "").strip(),
        "resend_api_key": os.getenv("RESEND_API_KEY", "").strip(),
        "enabled": os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "true").lower() == "true",
    }


def send_email(subject, text_body, fields=None):
    """Send email through Resend; returns a truthful success/error result."""
    config = load_config()
    recipient = config["target_email"]
    sender = config["sender_email"]
    api_key = config["resend_api_key"]

    if not config["enabled"]:
        return {"success": False, "mode": "DISABLED", "message": "Email notifications are disabled."}
    if not recipient or not sender or not api_key:
        missing = [name for name, value in (
            ("ALERT_TO_EMAIL", recipient),
            ("ALERT_FROM_EMAIL", sender),
            ("RESEND_API_KEY", api_key),
        ) if not value]
        message = "Missing deployment environment variable(s): " + ", ".join(missing)
        _log("EMAIL", recipient or "(unset)", subject, "CONFIG_ERROR", message)
        return {"success": False, "mode": "CONFIG_ERROR", "message": message}

    details = "\n".join(f"{key}: {value}" for key, value in (fields or {}).items())
    body = text_body + ("\n\nDetails:\n" + details if details else "")
    payload = {
        "from": sender,
        "to": [recipient],
        "subject": subject,
        "text": body,
    }
    request = urllib.request.Request(
        RESEND_ENDPOINT,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "CrimeMap-Notification-Service/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            response_data = json.loads(response_body) if response_body else {}
        # A successful API response means accepted by provider, not guaranteed inbox delivery.
        email_id = response_data.get("id", "")
        _log("RESEND_API", recipient, subject, "ACCEPTED", f"provider_id={email_id}")
        return {
            "success": True,
            "mode": "RESEND_API",
            "recipient": recipient,
            "provider_id": email_id,
            "message": "Email accepted by the email provider for delivery.",
        }
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        _log("RESEND_API", recipient, subject, "HTTP_ERROR", f"HTTP {exc.code}: {error_body}")
        return {"success": False, "mode": "HTTP_ERROR", "message": f"Email provider returned HTTP {exc.code}: {error_body[:300]}"}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        _log("RESEND_API", recipient, subject, "FAILED", str(exc))
        return {"success": False, "mode": "SEND_ERROR", "message": f"Could not send email: {exc}"}


def send_fir_notification(fir_record):
    fir_id = fir_record.get("id", "Unknown")
    category = fir_record.get("category", "Incident")
    subject = f"CrimeMap complaint registered: {fir_id} - {category}"
    maps_url = f"https://www.google.com/maps?q={fir_record.get('lat', '')},{fir_record.get('lng', '')}"
    fields = {
        "Complaint ID": fir_id,
        "Title": fir_record.get("title", "Not provided"),
        "Category": category,
        "Severity": fir_record.get("severity", "Not specified"),
        "Police station": fir_record.get("police_station", "Not specified"),
        "Location": fir_record.get("location_name", "Not specified"),
        "Coordinates": f"{fir_record.get('lat', '')}, {fir_record.get('lng', '')}",
        "Map": maps_url,
        "Timestamp": fir_record.get("timestamp", dt.datetime.now(dt.timezone.utc).isoformat()),
        "Description": fir_record.get("description", "Not provided"),
    }
    return send_email(subject, "A new complaint was submitted to CrimeMap.", fields)


def send_sos_notification(sos_record):
    emergency_type = sos_record.get("emergency_type", "Emergency SOS")
    coords = sos_record.get("target_coordinates") or {}
    lat, lng = coords.get("lat", ""), coords.get("lng", "")
    unit = sos_record.get("dispatched_unit") or {}
    subject = f"URGENT CrimeMap SOS alert: {emergency_type}"
    fields = {
        "Emergency": emergency_type,
        "Latitude": lat,
        "Longitude": lng,
        "Map": f"https://www.google.com/maps?q={lat},{lng}",
        "Dispatched unit": unit.get("callsign", unit.get("id", "Not specified")),
        "Officer": unit.get("officer", "Not specified"),
        "ETA minutes": sos_record.get("eta_mins", "Not specified"),
        "Distance km": sos_record.get("distance_km", "Not specified"),
        "Timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    return send_email(subject, "An SOS event was submitted to CrimeMap. Verify and respond using your authorized emergency workflow.", fields)


def get_recent_email_logs(limit=20):
    try:
        if not LOG_FILE.exists():
            return []
        with LOG_FILE.open("r", encoding="utf-8") as log_file:
            return [line.rstrip("\n") for line in log_file.readlines()[-max(1, int(limit)):]]
    except OSError as exc:
        print(f"Could not read notification log: {exc}")
        return []





          
   
           
       
        


   
  
       
    
