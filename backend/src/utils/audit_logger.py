import os
import json
import threading
from datetime import datetime

AUDIT_FILE = "data/audit/unmatched_teams.json"
_lock = threading.Lock()

def log_unmatched_team(team_name: str, missing_metric: str):
    os.makedirs(os.path.dirname(AUDIT_FILE), exist_ok=True)
    with _lock:
        data = {}
        if os.path.exists(AUDIT_FILE):
            try:
                with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        
        if team_name not in data:
            data[team_name] = {"missing_metrics": [missing_metric], "last_seen": datetime.now().isoformat(), "count": 1}
        else:
            if missing_metric not in data[team_name]["missing_metrics"]:
                data[team_name]["missing_metrics"].append(missing_metric)
            data[team_name]["last_seen"] = datetime.now().isoformat()
            data[team_name]["count"] += 1
            
        with open(AUDIT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def get_unmatched_teams() -> dict:
    if not os.path.exists(AUDIT_FILE):
        return {}
    try:
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}