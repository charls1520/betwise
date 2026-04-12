# ML Training Data & Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a historical data pipeline combining authoritative CSVs from football-data.co.uk with Understat data to retrain the ML models on real historical data.

**Architecture:** A new script `historical.py` will download CSVs and process them into a unified dataset. The `train.py` script will be updated to read this master dataset, apply feature engineering, and train the actual models.

**Tech Stack:** Python 3.10+, `pandas`, `requests`, `scikit-learn`.

---

### Task 1: Create Historical Data Ingestion Script

**Files:**
- Create: `backend/src/ingestion/historical.py`
- Create: `backend/tests/ingestion/test_historical.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/ingestion/test_historical.py
import pytest
from src.ingestion.historical import download_football_data_co_uk

def test_download_football_data_co_uk(monkeypatch):
    class MockResponse:
        @property
        def text(self):
            return "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR\nE0,12/08/2023,Arsenal,Nott'm Forest,2,1,H\n"
        def raise_for_status(self):
            pass
            
    monkeypatch.setattr("requests.get", lambda url, timeout: MockResponse())
    
    df = download_football_data_co_uk(seasons=["2324"])
    assert not df.empty
    assert "HomeTeam" in df.columns
    assert df.iloc[0]["HomeTeam"] == "Arsenal"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ingestion/test_historical.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/ingestion/historical.py
import pandas as pd
import requests
import io

def download_football_data_co_uk(seasons: list = ["2324", "2223", "2122", "2021", "1920"]) -> pd.DataFrame:
    """Downloads historical Premier League CSVs from football-data.co.uk and concatenates them."""
    base_url = "https://www.football-data.co.uk/mmz4281/{}/E0.csv"
    dfs = []
    
    for season in seasons:
        url = base_url.format(season)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            df = pd.read_csv(io.StringIO(response.text))
            
            # Keep only relevant columns to avoid bloat
            cols_to_keep = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "HST", "AST", "HC", "AC"]
            # Some older seasons might lack certain columns, so we intersect
            cols = [c for c in cols_to_keep if c in df.columns]
            
            df = df[cols].copy()
            dfs.append(df)
        except Exception as e:
            print(f"Failed to download season {season}: {e}")
            
    if dfs:
        return pd.concat(dfs, ignore_ignore=True)
    return pd.DataFrame()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ingestion/test_historical.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ingestion/historical.py backend/tests/ingestion/test_historical.py
git commit -m "feat(ingestion): add historical data downloader from football-data.co.uk"
```

### Task 2: Update ML Feature Engineering for Real Data

**Files:**
- Modify: `backend/src/ml/features.py`
- Modify: `backend/tests/ml/test_features.py`

- [ ] **Step 1: Write the failing test**

Modify `backend/tests/ml/test_features.py` to add:
```python
def test_build_features_from_historical():
    data = [
        {"HomeTeam": "Arsenal", "AwayTeam": "Chelsea", "FTHG": 2, "FTAG": 0, "FTR": "H"},
        {"HomeTeam": "Chelsea", "AwayTeam": "Arsenal", "FTHG": 1, "FTAG": 1, "FTR": "D"}
    ]
    df = build_features_for_matches(data)
    # The updated function should map FTR to target_1x2
    assert "target_1x2" in df.columns
    assert df["target_1x2"].iloc[0] == 2  # Home
    assert df["target_1x2"].iloc[1] == 1  # Draw
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ml/test_features.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

Modify `backend/src/ml/features.py` to handle both live inference dicts and historical CSV rows:
```python
import pandas as pd

def build_features_for_matches(raw_matches: list) -> pd.DataFrame:
    """
    Transforms raw match dictionaries into a DataFrame with engineered features.
    Handles both live inference data and historical CSV data.
    """
    df = pd.DataFrame(raw_matches)
    if df.empty:
        return df
        
    # Feature Engineering
    # 1. Expected Goals Difference (if available from Understat)
    if 'home_xg' in df.columns and 'away_xg' in df.columns:
        df['xg_diff'] = df['home_xg'] - df['away_xg']
    else:
        # Fallback for historical data without xG (simplification for V1)
        df['xg_diff'] = 0.0

    # Target Variables (Historical Training)
    # football-data.co.uk uses FTR (H, D, A) and FTHG, FTAG
    if 'FTR' in df.columns:
        # 0: Away, 1: Draw, 2: Home
        ftr_map = {'A': 0, 'D': 1, 'H': 2}
        df['target_1x2'] = df['FTR'].map(ftr_map)
        
    if 'FTHG' in df.columns and 'FTAG' in df.columns:
        df['target_over25'] = ((df['FTHG'] + df['FTAG']) > 2.5).astype(int)
        
    # Target Variables (Live/Mock training fallback)
    elif 'home_goals' in df.columns and 'away_goals' in df.columns:
        def get_1x2(row):
            if row['home_goals'] > row['away_goals']: return 2
            if row['home_goals'] == row['away_goals']: return 1
            return 0
        df['target_1x2'] = df.apply(get_1x2, axis=1)
        df['target_over25'] = ((df['home_goals'] + df['away_goals']) > 2.5).astype(int)
        
    return df
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ml/test_features.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ml/features.py backend/tests/ml/test_features.py
git commit -m "feat(ml): update feature engineering to handle historical CSV structures"
```

### Task 3: Update Training Script and Train Real Models

**Files:**
- Modify: `backend/src/ml/train.py`

- [ ] **Step 1: Write the update**

Modify `backend/src/ml/train.py` to fetch historical data and train on it when run directly:
```python
import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from src.ml.features import build_features_for_matches

def train_and_save_models(df: pd.DataFrame, model_dir: str = "models"):
    """Trains independent models for each market and saves them."""
    os.makedirs(model_dir, exist_ok=True)
    
    # We will use xg_diff as the primary feature
    features = ["xg_diff"]
    
    # Fill missing features with 0 for safety
    X = df[features].fillna(0)
    
    models = {}
    
    if "target_1x2" in df.columns:
        # Drop rows where target is NaN
        valid_idx = df["target_1x2"].notna()
        X_valid = X[valid_idx]
        y_valid = df.loc[valid_idx, "target_1x2"]
        
        if len(X_valid) > 0:
            winner_clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
            winner_clf.fit(X_valid, y_valid)
            joblib.dump(winner_clf, os.path.join(model_dir, "winner_model.joblib"))
            models["winner_model"] = winner_clf
        
    if "target_over25" in df.columns:
        valid_idx = df["target_over25"].notna()
        X_valid = X[valid_idx]
        y_valid = df.loc[valid_idx, "target_over25"]
        
        if len(X_valid) > 0:
            goals_clf = LogisticRegression(random_state=42)
            goals_clf.fit(X_valid, y_valid)
            joblib.dump(goals_clf, os.path.join(model_dir, "goals_model.joblib"))
            models["goals_model"] = goals_clf
        
    return models

if __name__ == "__main__":
    from src.ingestion.historical import download_football_data_co_uk
    print("Downloading historical data...")
    raw_df = download_football_data_co_uk()
    
    if not raw_df.empty:
        print(f"Downloaded {len(raw_df)} historical matches.")
        print("Engineering features...")
        df_features = build_features_for_matches(raw_df.to_dict('records'))
        
        print("Training models...")
        train_and_save_models(df_features)
        print("Models trained and saved successfully.")
    else:
        print("Failed to download historical data.")
```

- [ ] **Step 2: Run the training script**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && python src/ml/train.py`
Expected: Output showing historical matches downloaded and models trained successfully.

- [ ] **Step 3: Commit**

```bash
git add backend/src/ml/train.py
git commit -m "feat(ml): integrate real historical data into training pipeline"
```
````