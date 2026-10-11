"""
Puducherry CRIMEMAP - Real-Time Emergency Notification Engine
Delivers real emails to siddarthssakthivel@gmail.com via FormSubmit Email API
and direct Gmail SMTP, plus instant live push notifications.
"""

import json
import smtplib
import datetime
import urllib.request
import urllib.error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
CONFIG_FILE = DATA_DIR / "email_config.json"
LOG_FILE = DATA_DIR / "email_notifications.log"


def load_config():
    if not CONFIG_FILE.exists():
        return {
            "target_email": "siddarthssakthivel@gmail.com",
            "sender_email": "c4i.puducherry.police@gmail.com",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_user": "",
            "smtp_pass": "",
            "enabled": True
        }
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def append_to_log(entry_type, recipient, subject, preview, status):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{now_str}] [{entry_type}] TO: {recipient} | STATUS: {status} | SUBJECT: {subject}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)


def send_ntfy_push(title, message, priority="urgent", tags="rotating_light,police_car"):
    """Sends instant live push notification via ntfy.sh public push broker."""
    try:
        topic_url = "https://ntfy.sh/puducherry-police-c4i-secure-alert"
        req = urllib.request.Request(
            topic_url,
            data=message.encode("utf-8"),
            headers={
                "Title": title,
                "Priority": priority,
                "Tags": tags,
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print("ntfy push error (non-fatal):", e)


def send_formsubmit_email(to_email, subject, payload_fields):
    """
    Delivers a real email to the user's inbox using the FormSubmit API.
    Does not require server SMTP or Gmail credentials.
    """
    try:
        url = f"https://formsubmit.co/ajax/{to_email}"
        data_dict = {
            "_subject": subject,
            "_template": "box",
            "_captcha": "false",
            "Department": "Puducherry Police C4I Center",
            **payload_fields
        }
        json_data = json.dumps(data_dict).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=json_data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
                "Origin": "http://127.0.0.1:5000",
                "Referer": "http://127.0.0.1:5000/"
            }
        )
        res = urllib.request.urlopen(req, timeout=10)
        res_text = res.read().decode("utf-8")
        res_json = json.loads(res_text)

        if res_json.get("success") == "true" or res_json.get("success") is True:
            append_to_log("FORMSUBMIT_API", to_email, subject, "Delivered to inbox", "DELIVERED_SUCCESS")
            return {
                "success": True,
                "mode": "REAL_EMAIL",
                "recipient": to_email,
                "message": f"Real email dispatched directly to {to_email} inbox!"
            }
        else:
            msg = res_json.get("message", "Pending activation")
            append_to_log("FORMSUBMIT_API", to_email, subject, msg, "ACTIVATION_REQUIRED")
            return {
                "success": True,
                "mode": "ACTIVATION_REQUIRED",
                "recipient": to_email,
                "message": msg
            }
    except Exception as e:
        err_msg = str(e)
        append_to_log("FORMSUBMIT_ERROR", to_email, subject, err_msg, "FAILED")
        return {
            "success": False,
            "mode": "ERROR",
            "recipient": to_email,
            "message": f"FormSubmit error: {err_msg}"
        }


def attempt_smtp_send(config, to_email, subject, plain_text, html_content):
    """Attempts direct SMTP if credentials provided."""
    smtp_user = config.get("smtp_user", "").strip()
    smtp_pass = config.get("smtp_pass", "").strip()
    sender = config.get("sender_email", "c4i.puducherry.police@gmail.com")

    if not smtp_user or not smtp_pass:
        return None  # Will fallback to FormSubmit API

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Puducherry Police C4I <{sender}>"
        msg["To"] = to_email

        part1 = MIMEText(plain_text, "plain")
        part2 = MIMEText(html_content, "html")
        msg.attach(part1)
        msg.attach(part2)

        server = smtplib.SMTP(config.get("smtp_server", "smtp.gmail.com"), config.get("smtp_port", 587), timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(sender, [to_email], msg.as_string())
        server.quit()

        append_to_log("LIVE_SMTP", to_email, subject, plain_text[:80], "DELIVERED_SUCCESS")
        return {
            "success": True,
            "mode": "LIVE_SMTP",
            "recipient": to_email,
            "message": f"Live email successfully delivered to {to_email} via Gmail SMTP!"
        }
    except Exception as e:
        err_msg = str(e)
        append_to_log("SMTP_ERROR", to_email, subject, err_msg, "FALLBACK_TRIGGERED")
        return None


def send_fir_notification(fir_record):
    """Sends notification when a new Live FIR is registered."""
    config = load_config()
    to_email = config.get("target_email", "siddarthssakthivel@gmail.com")

    subject = f"🚨 [PUDUCHERRY POLICE C4I] LIVE FIR REGISTERED: {fir_record['id']} - {fir_record.get('category', 'Incident')}"
    gmaps_url = f"https://www.google.com/maps?q={fir_record.get('lat')},{fir_record.get('lng')}"

    # Also send instant push
    push_title = f"🚨 FIR REGISTERED: {fir_record.get('id')}"
    push_body = f"{fir_record.get('title')} | Station: {fir_record.get('police_station')} | Severity: {fir_record.get('severity')}"
    send_ntfy_push(push_title, push_body, priority="high", tags="memo,police_officer")

    # Try SMTP first if configured
    smtp_res = attempt_smtp_send(config, to_email, subject, push_body, f"<p>{push_body}</p>")
    if smtp_res:
        return smtp_res

    # Use FormSubmit email API to deliver to real inbox
    fields = {
        "FIR_Reference_ID": fir_record.get("id"),
        "Incident_Title": fir_record.get("title"),
        "Crime_Category": fir_record.get("category"),
        "IPC_Section": fir_record.get("ipc_section", "IPC 379"),
        "Severity": fir_record.get("severity", "High"),
        "Police_Station": fir_record.get("police_station"),
        "Location": fir_record.get("location_name", "Puducherry"),
        "Coordinates": f"Lat {fir_record.get('lat')}, Lng {fir_record.get('lng')}",
        "Google_Maps_Link": gmaps_url,
        "Timestamp": fir_record.get("timestamp"),
        "Officer_Action": fir_record.get("description", "Immediate response team dispatched")
    }

    return send_formsubmit_email(to_email, subject, fields)


def send_sos_notification(sos_record):
    """Sends immediate high-priority alert when a 112 CAD Emergency SOS is dispatched."""
    config = load_config()
    to_email = config.get("target_email", "siddarthssakthivel@gmail.com")

    emergency_type = sos_record.get("emergency_type", "Priority 112 SOS Call")
    target_coords = sos_record.get("target_coordinates", {})
    lat = target_coords.get("lat", 11.9328)
    lng = target_coords.get("lng", 79.8352)
    unit = sos_record.get("dispatched_unit", {})
    callsign = unit.get("callsign", "PCR-01")
    unit_id = unit.get("id", "PCR-01")
    vehicle = unit.get("vehicle", "Mahindra Bolero")
    officer = unit.get("officer", "Duty SI")
    eta_mins = sos_record.get("eta_mins", 4)
    dist_km = sos_record.get("distance_km", 0.8)
    backup = sos_record.get("nearby_backup")

    subject = f"🚨 [PUDUCHERRY POLICE C4I] URGENT 112 SOS DISPATCH: {emergency_type} (ETA: {eta_mins} mins)"
    gmaps_url = f"https://www.google.com/maps?q={lat},{lng}"

    # Send instant push
    push_title = f"🚨 112 SOS EMERGENCY DISPATCH: {callsign}"
    push_body = f"Incident: {emergency_type} | ETA: {eta_mins} mins ({dist_km} km) | Officer: {officer}"
    send_ntfy_push(push_title, push_body, priority="urgent", tags="rotating_light,fire_engine")

    # Try SMTP first if configured
    smtp_res = attempt_smtp_send(config, to_email, subject, push_body, f"<p>{push_body}</p>")
    if smtp_res:
        return smtp_res

    # Use FormSubmit email API to deliver to real inbox
    fields = {
        "EMERGENCY_INCIDENT": emergency_type,
        "ALERT_LEVEL": "CODE RED / PRIORITY 1 DISPATCH",
        "Assigned_Patrol_Van": f"{callsign} ({unit_id})",
        "Vehicle_Type": vehicle,
        "Officer_in_Command": officer,
        "Estimated_ETA": f"{eta_mins} Minutes",
        "Distance_to_Scene": f"{dist_km} km",
        "Sector": unit.get("sector", "Puducherry Central"),
        "Backup_Unit": backup.get("callsign") if backup else "None in immediate sector",
        "GPS_Coordinates": f"Lat {lat}, Lng {lng}",
        "Google_Maps_Direct_Link": gmaps_url,
        "Dispatch_Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return send_formsubmit_email(to_email, subject, fields)


def get_recent_email_logs(limit=20):
    """Returns recent lines from the email log file."""
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [line.strip() for line in lines[-limit:]]
