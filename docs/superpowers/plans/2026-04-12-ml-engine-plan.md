# ML Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the foundational Machine Learning Engine with scikit-learn to train and run inference for the Match Winner (1X2) and Total Goals (Over/Under) markets.

**Architecture:** A set of Python modules within `backend/src/ml` for feature engineering, training (which outputs serialized models), and inference. We use `scikit-learn` algorithms for simplicity and speed.

**Tech Stack:** Python 3.10+, `scikit-learn`, `pandas`, `numpy`, `joblib`.

---

### Task 1: Install ML Dependencies

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Update requirements.txt**

Modify `backend/requirements.txt`:
Append to the end:
```text
pandas
numpy
scikit-learn
joblib
```

- [ ] **Step 2: Install dependencies**

Run: `cd backend && .\venv\Scripts\activate && pip install -r requirements.txt`

- [ ] **Step 3: Commit**

```bash
git add backend/requirements.txt
git commit -m "build(ml): add machine learning dependencies"
```

### Task 2: Implement Feature Engineering and Data Extraction

**Files:**
- Create: `backend/src/ml/__init__.py`
- Create: `backend/src/ml/features.py`
- Create: `backend/tests/ml/__init__.py`
- Create: `backend/tests/ml/test_features.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/ml/test_features.py
import pandas as pd
from src.ml.features import build_features_for_matches

def test_build_features_for_matches():
    # Mock some raw match data
    data = [
        {"home_team": "Arsenal", "away_team": "Chelsea", "home_xg": 2.1, "away_xg": 0.8, "home_goals": 2, "away_goals": 0},
        {"home_team": "Chelsea", "away_team": "Arsenal", "home_xg": 1.2, "away_xg": 1.5, "home_goals": 1, "away_goals": 1}
    ]
    
    df = build_features_for_matches(data)
    assert not df.empty
    assert "xg_diff" in df.columns
    assert "target_1x2" in df.columns
    assert "target_over25" in df.columns
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ml/test_features.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/ml/features.py
import pandas as pd

def build_features_for_matches(raw_matches: list) -> pd.DataFrame:
    """
    Transforms raw match dictionaries into a DataFrame with engineered features 
    and target variables suitable for training.
    """
    df = pd.DataFrame(raw_matches)
    if df.empty:
        return df
        
    # Feature Engineering
    # In a real scenario, this would use rolling averages. We use raw xg diff for simplicity here.
    df['xg_diff'] = df.get('home_xg', 0) - df.get('away_xg', 0)
    
    # Target Variables
    if 'home_goals' in df.columns and 'away_goals' in df.columns:
        # Match Winner Target (0: Away, 1: Draw, 2: Home)
        def get_1x2(row):
            if row['home_goals'] > row['away_goals']: return 2
            if row['home_goals'] == row['away_goals']: return 1
            return 0
        df['target_1x2'] = df.apply(get_1x2, axis=1)
        
        # Over/Under Target (1: Over 2.5, 0: Under 2.5)
        df['target_over25'] = ((df['home_goals'] + df['away_goals']) > 2.5).astype(int)
        
    return df
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ml/test_features.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ml/ backend/tests/ml/
git commit -m "feat(ml): implement feature engineering and target variable generation"
```

### Task 3: Create Model Training Module

**Files:**
- Create: `backend/src/ml/train.py`
- Create: `backend/tests/ml/test_train.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/ml/test_train.py
import os
import pandas as pd
from src.ml.train import train_and_save_models

def test_train_and_save_models(tmp_path):
    # Dummy data
    df = pd.DataFrame({
        "xg_diff": [1.0, -0.5, 0.2, 2.5, -1.5, 0.0],
        "target_1x2": [2, 0, 1, 2, 0, 1],
        "target_over25": [1, 0, 0, 1, 1, 0]
    })
    
    model_dir = str(tmp_path)
    models = train_and_save_models(df, model_dir)
    
    assert "winner_model" in models
    assert "goals_model" in models
    assert os.path.exists(os.path.join(model_dir, "winner_model.joblib"))
    assert os.path.exists(os.path.join(model_dir, "goals_model.joblib"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ml/test_train.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/ml/train.py
import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

def train_and_save_models(df: pd.DataFrame, model_dir: str = "models"):
    """Trains independent models for each market and saves them."""
    os.makedirs(model_dir, exist_ok=True)
    features = ["xg_diff"]
    X = df[features]
    
    models = {}
    
    # 1. Match Winner (1X2) Model
    if "target_1x2" in df.columns:
        winner_clf = RandomForestClassifier(n_estimators=10, random_state=42)
        winner_clf.fit(X, df["target_1x2"])
        joblib.dump(winner_clf, os.path.join(model_dir, "winner_model.joblib"))
        models["winner_model"] = winner_clf
        
    # 2. Total Goals (Over/Under 2.5) Model
    if "target_over25" in df.columns:
        goals_clf = LogisticRegression(random_state=42)
        goals_clf.fit(X, df["target_over25"])
        joblib.dump(goals_clf, os.path.join(model_dir, "goals_model.joblib"))
        models["goals_model"] = goals_clf
        
    return models
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ml/test_train.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ml/train.py backend/tests/ml/test_train.py
git commit -m "feat(ml): implement independent model training and saving"
```

### Task 4: Implement Inference Pipeline

**Files:**
- Create: `backend/src/ml/inference.py`
- Create: `backend/tests/ml/test_inference.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/ml/test_inference.py
import pandas as pd
from src.ml.train import train_and_save_models
from src.ml.inference import predict_matches

def test_predict_matches(tmp_path):
    # Train dummy models
    df_train = pd.DataFrame({
        "xg_diff": [1.0, -0.5, 0.2, 2.5, -1.5, 0.0],
        "target_1x2": [2, 0, 1, 2, 0, 1],
        "target_over25": [1, 0, 0, 1, 1, 0]
    })
    model_dir = str(tmp_path)
    train_and_save_models(df_train, model_dir)
    
    # Inference data
    df_infer = pd.DataFrame([
        {"home_team": "Arsenal", "away_team": "Chelsea", "home_xg": 2.0, "away_xg": 0.5}
    ])
    
    predictions = predict_matches(df_infer, model_dir)
    
    assert len(predictions) == 1
    assert "prob_home_win" in predictions[0]
    assert "prob_over25" in predictions[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ml/test_inference.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/ml/inference.py
import os
import joblib
import pandas as pd
from src.ml.features import build_features_for_matches

def predict_matches(raw_matches: list, model_dir: str = "models") -> list:
    """Loads trained models and predicts probabilities for new matches."""
    df = build_features_for_matches(raw_matches)
    if df.empty:
        return []
        
    features = ["xg_diff"]
    X = df[features]
    
    winner_model_path = os.path.join(model_dir, "winner_model.joblib")
    goals_model_path = os.path.join(model_dir, "goals_model.joblib")
    
    winner_clf = joblib.load(winner_model_path) if os.path.exists(winner_model_path) else None
    goals_clf = joblib.load(goals_model_path) if os.path.exists(goals_model_path) else None
    
    results = []
    for i in range(len(df)):
        row = df.iloc[i:i+1]
        x_row = X.iloc[i:i+1]
        match_pred = {"match_index": i}
        
        if winner_clf:
            probs_1x2 = winner_clf.predict_proba(x_row)[0]
            # Assuming classes are [0, 1, 2] -> [Away, Draw, Home]
            classes = list(winner_clf.classes_)
            match_pred["prob_away_win"] = probs_1x2[classes.index(0)] if 0 in classes else 0.0
            match_pred["prob_draw"] = probs_1x2[classes.index(1)] if 1 in classes else 0.0
            match_pred["prob_home_win"] = probs_1x2[classes.index(2)] if 2 in classes else 0.0
            
        if goals_clf:
            probs_goals = goals_clf.predict_proba(x_row)[0]
            # Assuming classes are [0, 1] -> [Under, Over]
            classes = list(goals_clf.classes_)
            match_pred["prob_under25"] = probs_goals[classes.index(0)] if 0 in classes else 0.0
            match_pred["prob_over25"] = probs_goals[classes.index(1)] if 1 in classes else 0.0
            
        results.append(match_pred)
        
    return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ml/test_inference.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ml/inference.py backend/tests/ml/test_inference.py
git commit -m "feat(ml): add inference pipeline for probability predictions"
```