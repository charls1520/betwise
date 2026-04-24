# Data Health Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a read-only Python script (`audit_data.py`) to scan the Data Lake, Historical cache, and databases to generate a comprehensive data health Markdown report.

**Architecture:** A standalone Python script using `pandas`, `os`, `json`, and `sqlalchemy`. It aggregates metrics and writes a timestamped Markdown report to `docs/audits/`.

**Tech Stack:** Python, Pandas, SQLAlchemy, ChromaDB (optional import for size checking).

---

### Task 1: Skeleton and Data Lake Auditor

**Files:**
- Create: `backend/src/utils/audit_data.py`
- Test: `backend/tests/utils/test_audit_data.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/utils/test_audit_data.py
import pytest
from src.utils.audit_data import audit_data_lake

def test_audit_data_lake(tmp_path):
    # Setup dummy data lake
    lake_dir = tmp_path / "data" / "raw" / "2026-01-01"
    lake_dir.mkdir(parents=True)
    
    # 1 valid file
    (lake_dir / "odds_1.json").write_text('{"matches": [{"id": 1}]}')
    # 1 empty file
    (lake_dir / "odds_2.json").write_text('{"matches": []}')
    # 1 corrupt file
    (lake_dir / "odds_3.json").write_text('{corrupt')
    
    metrics = audit_data_lake(base_dir=str(tmp_path / "data" / "raw"))
    
    assert metrics["total_files"] == 3
    assert metrics["empty_matches"] == 1
    assert metrics["corrupt_files"] == 1
    assert "total_size_mb" in metrics
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/utils/test_audit_data.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.utils.audit_data'"

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/utils/audit_data.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/utils/test_audit_data.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/tests/utils/test_audit_data.py backend/src/utils/audit_data.py
git commit -m "feat(audit): add data lake scanner to detect corrupt and empty files"
```

---

### Task 2: Historical Cache Auditor

**Files:**
- Modify: `backend/src/utils/audit_data.py`
- Modify: `backend/tests/utils/test_audit_data.py`

- [ ] **Step 1: Write the failing test**

```python
# Add to backend/tests/utils/test_audit_data.py
import pandas as pd
from src.utils.audit_data import audit_historical_cache

def test_audit_historical_cache(tmp_path):
    cache_file = tmp_path / "merged_history_cache.csv"
    
    df = pd.DataFrame({
        "Date": ["2026-01-01", "2026-01-01", "2026-01-02"],
        "HomeTeam": ["A", "A", "B"],
        "AwayTeam": ["B", "B", "C"],
        "Home_xG": [1.0, 1.0, None], # 1 missing, 1 duplicate row
        "Away_xG": [0.0, 0.0, 1.5],  # 2 zeros
        "Home_Elo": [1500, 1500, 0], # 1 zero elo
        "Away_Elo": [1400, 1400, 1600]
    })
    df.to_csv(cache_file, index=False)
    
    metrics = audit_historical_cache(str(cache_file))
    
    assert metrics["total_rows"] == 3
    assert metrics["duplicates"] == 1
    assert metrics["missing_xg"] == 1
    assert metrics["zero_xg"] == 2
    assert metrics["zero_elo"] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/utils/test_audit_data.py::test_audit_historical_cache -v`
Expected: FAIL (function not imported/defined)

- [ ] **Step 3: Write minimal implementation**

```python
# Add to backend/src/utils/audit_data.py
import pandas as pd

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/utils/test_audit_data.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/utils/audit_data.py backend/tests/utils/test_audit_data.py
git commit -m "feat(audit): add historical cache scanner to detect NaN and zero values"
```

---

### Task 3: Database & Report Generator

**Files:**
- Modify: `backend/src/utils/audit_data.py`
- Modify: `backend/tests/utils/test_audit_data.py`

- [ ] **Step 1: Write minimal implementation**

```python
# Add to backend/src/utils/audit_data.py
from datetime import datetime

def audit_databases(db_path: str = "test.db", chroma_path: str = "data/chromadb") -> dict:
    metrics = {"teams_count": 0, "chroma_size_mb": 0.0}
    
    # SQLite check (basic file existence and size for now, to avoid sqlalchemy context issues in simple script)
    if os.path.exists(db_path):
        # We can just count lines or use sqlite3 directly for a lightweight check
        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM teams")
            metrics["teams_count"] = cursor.fetchone()[0]
            conn.close()
        except Exception:
            pass

    # ChromaDB check
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
*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*

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
    filename = f"../docs/audits/{datetime.utcnow().strftime('%Y-%m-%d')}-data-health-report.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Audit complete. Report saved to {filename}")
    if red_alerts:
        print("WARNING: Red alerts detected. Check the report.")

if __name__ == "__main__":
    generate_audit_report()
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/utils/audit_data.py
git commit -m "feat(audit): add database scanner and markdown report generator"
```
