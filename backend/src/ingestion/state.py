import json
import os
from datetime import datetime

STATE_FILE = "data/ingestion_state.json"

def get_last_run(source: str) -> str:
    """Returns ISO format string of last run, or None if never run."""
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
    return data.get(source)

def update_last_run(source: str):
    """Updates the last run timestamp for a source to now."""
    data = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
    
    data[source] = datetime.utcnow().isoformat()
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)
