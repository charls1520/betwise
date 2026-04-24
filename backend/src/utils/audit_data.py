import os
import json
import pandas as pd

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

def audit_historical_cache(filepath: str = "data/historical/merged_history_cache.csv") -> dict:
    metrics = {
        "total_rows": 0,
        "duplicates": 0,
        "missing_xg": 0,
        "zero_xg": 0,
        "zero_elo": 0
    }
    
    if not os.path.exists(filepath):
        return metrics
        
    try:
        df = pd.read_csv(filepath)
        metrics["total_rows"] = len(df)
        
        # Duplicates based on match signature
        if "Date" in df.columns and "HomeTeam" in df.columns and "AwayTeam" in df.columns:
            metrics["duplicates"] = int(df.duplicated(subset=["Date", "HomeTeam", "AwayTeam"]).sum())
            
        # Missing xG
        if "Home_xG" in df.columns and "Away_xG" in df.columns:
            missing_home = df["Home_xG"].isna().sum()
            missing_away = df["Away_xG"].isna().sum()
            metrics["missing_xg"] = int(missing_home + missing_away)
            
            zero_home = (df["Home_xG"] == 0.0).sum()
            zero_away = (df["Away_xG"] == 0.0).sum()
            metrics["zero_xg"] = int(zero_home + zero_away)
            
        # Zero Elo
        if "Home_Elo" in df.columns and "Away_Elo" in df.columns:
            zero_h_elo = (df["Home_Elo"] == 0).sum()
            zero_a_elo = (df["Away_Elo"] == 0).sum()
            metrics["zero_elo"] = int(zero_h_elo + zero_a_elo)
            
    except Exception as e:
        print(f"Error reading historical cache: {e}")
        
    return metrics
