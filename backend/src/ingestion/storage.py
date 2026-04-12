import os
import json
from datetime import datetime


def save_raw_data(source_type: str, data: dict, base_dir: str = "data/raw") -> str:
    """Saves raw data to a local directory partitioned by date."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    dir_path = os.path.join(base_dir, date_str)
    os.makedirs(dir_path, exist_ok=True)

    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{source_type}_{timestamp}.json"
    filepath = os.path.join(dir_path, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filepath
