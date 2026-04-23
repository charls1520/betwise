# Data Ingestion, ML Validation, and Real-Time Frontend Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement delta data ingestion to avoid duplicates, add ML model validation thresholds to prevent regression, and enable short-polling on the frontend for real-time updates.

**Architecture:** 
1. `ingestion_state.json` tracks last fetch times for origin filters.
2. `train.py` uses `train_test_split` to evaluate the model on holdout data and compares metrics against a stored `model_metrics.json`.
3. `DashboardPanel.tsx` uses a `useEffect` with `setInterval` to fetch `/api/dashboard` data every 60s.

**Tech Stack:** Python, scikit-learn, React, Vite, Tailwind.

---

### Task 1: Ingestion State Cache & Origin Filter

**Files:**
- Create: `backend/src/ingestion/state.py`
- Modify: `backend/src/ingestion/tasks.py`

- [ ] **Step 1: Create State Manager**

```python
# backend/src/ingestion/state.py
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
```

- [ ] **Step 2: Update Tasks to Use State**

Modify `backend/src/ingestion/tasks.py` around line 58 where the loop for `LEAGUES_CONFIG` is:

```python
# In tasks.py: Add imports
# from src.ingestion.state import get_last_run, update_last_run

# Before the loop
    last_odds_run = get_last_run("odds_api")
    last_xg_run = get_last_run("understat")

    for league in LEAGUES_CONFIG:
        logger.info(f"Fetching data for {league['name']}...")
        
        try:
            # We assume fetch_premier_league_odds can optionally take commence_time_from
            # If the API wrapper doesn't support it, we filter the results here.
            odds = fetch_premier_league_odds(api_key=odds_api_key, sport_key=league["odds_api_id"])
            
            if last_odds_run:
                # Filter odds that commence AFTER last_odds_run
                odds = [o for o in odds if o.get("commence_time", "") > last_odds_run]

            if validate_volume(len(odds), expected_minimum=1):
                all_odds.extend(odds)
            else:
                logger.info(f"No new odds or volume too low for {league['name']}.")
        except Exception as e:
            logger.error(f"Failed odds for {league['name']}: {e}")
            
        try:
            xg_stats = fetch_current_xg_stats(league_id=league["understat_id"])
            # Filter if needed (simplified since understat doesn't have easily filterable timestamps per match in the raw payload unless parsed)
            if validate_volume(len(xg_stats), expected_minimum=1):
                all_xg.update(xg_stats)
            else:
                logger.error(f"xG volume validation failed for {league['name']}.")
        except Exception as e:
            logger.error(f"Failed xG for {league['name']}: {e}")

    # After saving raw data successfully
    if len(all_odds) > 0:
        update_last_run("odds_api")
    if len(all_xg) > 0:
        update_last_run("understat")
```

- [ ] **Step 3: Commit Task 1**

```bash
git add backend/src/ingestion/state.py backend/src/ingestion/tasks.py
git commit -m "feat(ingestion): add delta fetching using ingestion state cache"
```

---

### Task 2: ML Model Validation

**Files:**
- Modify: `backend/src/ml/train.py`

- [ ] **Step 1: Add train_test_split and metrics to train.py**

Modify `backend/src/ml/train.py` to evaluate models before saving.

```python
# Add to imports:
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score
# import json

# Inside train_and_save_models(df, model_dir):
# ...
    X = df[features]
    models = {}
    metrics_file = os.path.join(model_dir, "model_metrics.json")
    
    current_metrics = {}
    if os.path.exists(metrics_file):
        with open(metrics_file, "r") as f:
            current_metrics = json.load(f)

    if "target_1x2" in df.columns:
        valid_idx = df["target_1x2"].notna()
        X_valid = X[valid_idx]
        y_valid = df.loc[valid_idx, "target_1x2"]

        if len(X_valid) > 0:
            X_train, X_test, y_train, y_test = train_test_split(X_valid, y_valid, test_size=0.2, random_state=42)
            
            winner_clf = Pipeline([
                ('imputer', imputer),
                ('rf', RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42))
            ])
            winner_clf.fit(X_train, y_train)
            
            y_pred = winner_clf.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            
            prev_acc = current_metrics.get("winner_model_acc", 0)
            
            if acc >= 0.50 and (acc >= prev_acc - 0.02):
                joblib.dump(winner_clf, os.path.join(model_dir, "winner_model.joblib"))
                models["winner_model"] = winner_clf
                current_metrics["winner_model_acc"] = acc
                print(f"Winner model deployed. Acc: {acc:.4f}")
            else:
                print(f"Winner model REJECTED. New Acc: {acc:.4f}, Prev: {prev_acc:.4f}")

    # Apply similar logic for goals_model (target_over25)
    if "target_over25" in df.columns:
        valid_idx = df["target_over25"].notna()
        X_valid = X[valid_idx]
        y_valid = df.loc[valid_idx, "target_over25"]

        if len(X_valid) > 0:
            X_train, X_test, y_train, y_test = train_test_split(X_valid, y_valid, test_size=0.2, random_state=42)
            goals_clf = Pipeline([
                ('imputer', imputer),
                ('lr', LogisticRegression(random_state=42))
            ])
            goals_clf.fit(X_train, y_train)
            
            y_pred = goals_clf.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            
            prev_acc = current_metrics.get("goals_model_acc", 0)
            
            if acc >= 0.50 and (acc >= prev_acc - 0.02):
                joblib.dump(goals_clf, os.path.join(model_dir, "goals_model.joblib"))
                models["goals_model"] = goals_clf
                current_metrics["goals_model_acc"] = acc
                print(f"Goals model deployed. Acc: {acc:.4f}")
            else:
                print(f"Goals model REJECTED. New Acc: {acc:.4f}, Prev: {prev_acc:.4f}")

    # Save new metrics
    with open(metrics_file, "w") as f:
        json.dump(current_metrics, f)

    return models
```

- [ ] **Step 2: Commit Task 2**

```bash
git add backend/src/ml/train.py
git commit -m "feat(ml): add evaluation thresholds and prevent model regression"
```

---

### Task 3: Frontend Short-Polling

**Files:**
- Modify: `frontend/src/components/DashboardPanel.tsx`

- [ ] **Step 1: Add setInterval to DashboardPanel**

Update the `useEffect` inside `DashboardPanel` to run the fetch every 60 seconds.

```tsx
// Inside frontend/src/components/DashboardPanel.tsx

  useEffect(() => {
    const fetchData = () => {
      fetch(`${apiUrl}/api/dashboard`)
        .then(res => res.json())
        .then(fetchedData => {
          if (Array.isArray(fetchedData) && fetchedData.length > 0 && fetchedData[0].error) {
             setData({ matches: [], suggestions: [], error: fetchedData[0].error });
          } else {
             setData(fetchedData as DashboardPayload);
          }
        })
        .catch(err => {
          console.error("Error fetching dashboard data", err);
          setData({ matches: [], suggestions: [], error: "No se pudo conectar con el servidor." });
        });
    };

    // Initial fetch
    fetchData();

    // Set up short-polling interval (60 seconds)
    const intervalId = setInterval(fetchData, 60000);

    // Cleanup interval on unmount
    return () => clearInterval(intervalId);
  }, [apiUrl]); // Re-run if apiUrl changes
```

- [ ] **Step 2: Commit Task 3**

```bash
git add frontend/src/components/DashboardPanel.tsx
git commit -m "feat(ui): implement short-polling in dashboard for real-time updates"
```

---
