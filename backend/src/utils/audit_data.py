import os
import json

def audit_data_lake(base_dir: str = "data/raw") -> dict:
    metrics = {
        "total_files": 0,
        "empty_matches": 0,
        "corrupt_files": 0,
        "total_size_mb": 0.0
    }
    
    if not os.path.exists(base_dir):
        return metrics

    total_bytes = 0
    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.endswith(".json"):
                continue
                
            metrics["total_files"] += 1
            filepath = os.path.join(root, file)
            total_bytes += os.path.getsize(filepath)
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    if isinstance(data, dict) and "matches" in data:
                        if len(data["matches"]) == 0:
                            metrics["empty_matches"] += 1
                    elif isinstance(data, list) and len(data) == 0:
                        metrics["empty_matches"] += 1
                    elif not data: # empty dict {}
                        metrics["empty_matches"] += 1

            except json.JSONDecodeError:
                metrics["corrupt_files"] += 1
            except Exception:
                metrics["corrupt_files"] += 1

    metrics["total_size_mb"] = round(total_bytes / (1024 * 1024), 2)
    return metrics
