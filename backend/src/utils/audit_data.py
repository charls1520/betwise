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

from datetime import datetime, timezone

def audit_databases(db_path: str = "test.db", chroma_path: str = "data/chromadb") -> dict:
    metrics = {"teams_count": 0, "chroma_size_mb": 0.0}
    
    if os.path.exists(db_path):
        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM teams")
            metrics["teams_count"] = cursor.fetchone()[0]
            conn.close()
        except Exception:
            pass

    if os.path.exists(chroma_path):
        total_bytes = sum(os.path.getsize(os.path.join(dirpath, filename)) 
                          for dirpath, _, filenames in os.walk(chroma_path) 
                          for filename in filenames)
        metrics["chroma_size_mb"] = round(total_bytes / (1024 * 1024), 2)
        
    return metrics

def generate_audit_report():
    lake_metrics = audit_data_lake()
    hist_metrics = audit_historical_cache()
    db_metrics = audit_databases()
    
    red_alerts = []
    
    if lake_metrics["corrupt_files"] > 0:
        red_alerts.append(f"**Data Lake:** {lake_metrics['corrupt_files']} corrupt JSON files detected.")
    if lake_metrics["empty_matches"] > 0:
        red_alerts.append(f"**Data Lake:** {lake_metrics['empty_matches']} empty JSON files detected.")
    if hist_metrics["missing_xg"] > 0:
        red_alerts.append(f"**Historical Cache:** {hist_metrics['missing_xg']} missing xG values detected.")
    if hist_metrics["duplicates"] > 0:
        red_alerts.append(f"**Historical Cache:** {hist_metrics['duplicates']} duplicated matches detected.")

    alerts_md = "\n".join([f"- 🔴 {alert}" for alert in red_alerts]) if red_alerts else "- ✅ No critical alerts. Data is healthy."

    report = f"""# Data Health & Storage Audit
*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC*

## 🚨 Red Alerts
{alerts_md}

## 📊 1. Data Lake (`data/raw/`)
- **Total Files:** {lake_metrics['total_files']}
- **Total Size:** {lake_metrics['total_size_mb']} MB
- **Corrupt Files:** {lake_metrics['corrupt_files']}
- **Empty Files:** {lake_metrics['empty_matches']}

## 📈 2. Historical Cache
- **Total Matches:** {hist_metrics['total_rows']}
- **Duplicates:** {hist_metrics['duplicates']}
- **Missing xG (NaN):** {hist_metrics['missing_xg']}
- **Zero xG (0.0):** {hist_metrics['zero_xg']}
- **Zero Elo (0):** {hist_metrics['zero_elo']}

## 🗄️ 3. Databases
- **Teams Canonicalized:** {db_metrics['teams_count']}
- **ChromaDB Size:** {db_metrics['chroma_size_mb']} MB
"""
    
    os.makedirs("../docs/audits", exist_ok=True)
    filename = f"../docs/audits/{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-data-health-report.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Audit complete. Report saved to {filename}")
    if red_alerts:
        print("WARNING: Red alerts detected. Check the report.")

if __name__ == "__main__":
    generate_audit_report()
