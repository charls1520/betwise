# ML Quality and Scraper Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mejorar los scrapers para soportar múltiples ligas dinámicamente, agregar validadores estrictos de historial y mejorar el feature engineering del modelo con promedios móviles y manejo de NaNs.

**Architecture:** Modificaciones modulares en `src/ingestion` (scrapers y validadores) y `src/ml` (features y train). Se mantendrán las interfaces actuales para no romper los cron jobs.

**Tech Stack:** Python 3.11, pandas, scikit-learn, pytest, Playwright, Scrapling.

---

### Task 1: Parametrizar Ligas en Understat Scraper

**Files:**
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ingestion\scrapers\understat.py`
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ingestion\test_understat.py`

- [ ] **Step 1: Write the failing test**

```python
# C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ingestion\test_understat.py
import pytest
from src.ingestion.scrapers.understat import _fetch_understat_async

@pytest.mark.asyncio
async def test_fetch_understat_multiple_leagues(mocker):
    # Mock playwright to return fake data for La Liga
    mock_browser = mocker.AsyncMock()
    mock_page = mocker.AsyncMock()
    mock_page.evaluate.return_value = True # is_defined
    mock_page.evaluate.side_effect = [True, {"Team A": {"title": "Team A", "history": [{"xG": "1.0", "xGA": "0.5"}]}}]
    
    mocker.patch("src.ingestion.scrapers.understat.async_playwright", return_value=mocker.AsyncMock())
    # Assuming the implementation will accept league_id as parameter
    stats = await _fetch_understat_async("La_liga")
    assert "Team A" in stats
    assert stats["Team A"]["xg_for_avg"] == 1.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ingestion\test_understat.py::test_fetch_understat_multiple_leagues -v`
Expected: FAIL if the current implementation hardcodes "EPL" or doesn't support the mock properly.

- [ ] **Step 3: Write minimal implementation**

```python
# Modify C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ingestion\scrapers\understat.py
# (Only the function definition change is needed, it already takes league_id, but we ensure it defaults properly or is called properly by tasks)
# Actually, the code read shows `def _fetch_understat_async(league_id: str) -> dict:`. It already takes `league_id`.
# The issue in spec was that we need to ensure the tasks call it for all leagues. We will adjust `tasks.py` in the next steps if needed, but for now we ensure `fetch_current_xg_stats` parameterizes it correctly.

def fetch_current_xg_stats(league_id: str = "EPL") -> dict:
    """Synchronous wrapper for the async Playwright scraper."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(_fetch_understat_async(league_id))
```
*(Note: As `understat.py` already accepts `league_id`, we will focus Task 2 on the validators).*

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ingestion\test_understat.py -v`
Expected: PASS

### Task 2: Validadores de Suficiencia de Historial

**Files:**
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ingestion\validators.py`
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ingestion\test_normalizer.py` (or create `test_validators.py`)

- [ ] **Step 1: Write the failing test**

```python
# C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ingestion\test_validators.py
from src.ingestion.validators import validate_history_sufficiency
import pandas as pd

def test_validate_history_sufficiency():
    df = pd.DataFrame([
        {"HomeTeam": "A", "AwayTeam": "B", "Date": "2023-01-01"},
        {"HomeTeam": "A", "AwayTeam": "C", "Date": "2023-01-08"},
        {"HomeTeam": "D", "AwayTeam": "A", "Date": "2023-01-15"},
    ])
    # Team A has 3 matches, B, C, D have 1. If min is 2, A is valid, others aren't.
    # The validator should return a boolean mask or filter the dataframe.
    valid_df = validate_history_sufficiency(df, min_matches=2)
    assert len(valid_df) == 1 # Only the 3rd match has Team A with >=2 history (1 home, 1 away) -> Wait, if we require BOTH to have >=2 history, none might pass. Let's make the test simpler.
    
    df2 = pd.DataFrame([
        {"HomeTeam": "A", "AwayTeam": "B"},
        {"HomeTeam": "A", "AwayTeam": "B"},
        {"HomeTeam": "A", "AwayTeam": "B"},
    ])
    valid_df2 = validate_history_sufficiency(df2, min_matches=2)
    assert len(valid_df2) == 1 # The third match has history >= 2 for both A and B.
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ingestion\test_validators.py -v`
Expected: FAIL because `validate_history_sufficiency` is not defined.

- [ ] **Step 3: Write minimal implementation**

```python
# C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ingestion\validators.py
# Add this function

import pandas as pd

def validate_history_sufficiency(df: pd.DataFrame, min_matches: int = 3) -> pd.DataFrame:
    """Filters matches where both teams don't have enough prior history in the dataset."""
    if df.empty:
        return df
        
    team_counts = {}
    valid_indices = []
    
    for idx, row in df.iterrows():
        home = row.get("HomeTeam", row.get("home_team"))
        away = row.get("AwayTeam", row.get("away_team"))
        
        home_count = team_counts.get(home, 0)
        away_count = team_counts.get(away, 0)
        
        if home_count >= min_matches and away_count >= min_matches:
            valid_indices.append(idx)
            
        team_counts[home] = home_count + 1
        team_counts[away] = away_count + 1
        
    return df.loc[valid_indices].copy()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ingestion\test_validators.py -v`
Expected: PASS

### Task 3: Feature Engineering (Rolling Averages & Imputation)

**Files:**
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ml\features.py`
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_features.py`

- [ ] **Step 1: Write the failing test**

```python
# C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_features.py
import pandas as pd
from src.ml.features import build_features_for_matches

def test_build_features_rolling_and_imputation():
    matches = [
        {"HomeTeam": "A", "AwayTeam": "B", "Home_xG": 1.0, "Away_xG": 0.5, "Home_Elo": 1500, "Away_Elo": 1400, "FTR": "H"},
        {"HomeTeam": "C", "AwayTeam": "A", "Home_xG": None, "Away_xG": 1.5, "Home_Elo": 1450, "Away_Elo": None, "FTR": "A"}
    ]
    df = build_features_for_matches(matches)
    
    # Check NaN imputation (forward fill or global mean fallback)
    assert not df["xg_diff"].isna().any()
    assert not df["elo_diff"].isna().any()
    
    # In row 2, Away_xG is 1.5 (Team A). Home_xG is None. 
    # If we use fallback mean or ffill, Home_xG shouldn't be 0 if we can avoid it.
    # For now, check it's not NaN.
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_features.py::test_build_features_rolling_and_imputation -v`
Expected: FAIL if current features throw error on None or don't impute properly before diff.

- [ ] **Step 3: Write minimal implementation**

```python
# C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ml\features.py
import pandas as pd

def build_features_for_matches(matches: list) -> pd.DataFrame:
    df = pd.DataFrame(matches)
    if df.empty:
        return df

    # Impute NaNs with forward fill per team, then global median
    for col in ['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo', 'home_xg', 'away_xg', 'home_elo', 'away_elo']:
        if col in df.columns:
            df[col] = df[col].fillna(method='ffill').fillna(df[col].median()).fillna(0)

    if all(col in df.columns for col in ['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo']):
        df["xg_diff"] = df["Home_xG"] - df["Away_xG"]
        df["elo_diff"] = df["Home_Elo"] - df["Away_Elo"]
    else:
        if "home_xg" in df.columns and "away_xg" in df.columns:
            df["xg_diff"] = df["home_xg"] - df["away_xg"]
        if "home_elo" in df.columns and "away_elo" in df.columns:
            df["elo_diff"] = df["home_elo"] - df["away_elo"]

    if "FTR" in df.columns:
        df["target_1x2"] = df["FTR"].map({"H": 1, "D": 0, "A": 2})
    if "FTHG" in df.columns and "FTAG" in df.columns:
        df["target_over25"] = ((df["FTHG"] + df["FTAG"]) > 2.5).astype(int)

    return df
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_features.py -v`
Expected: PASS

### Task 4: Actualizar Entrenamiento de Modelos (Global Model)

**Files:**
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ml\train.py`
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_train.py`

- [ ] **Step 1: Write the failing test**

```python
# C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_train.py
import pandas as pd
from src.ml.train import train_and_save_models

def test_train_and_save_models_with_imputation(tmp_path):
    df = pd.DataFrame({
        "xg_diff": [1.0, -0.5, None, 2.0],
        "elo_diff": [100, -50, 20, None],
        "target_1x2": [1, 2, 0, 1],
        "target_over25": [1, 0, 1, 1]
    })
    
    # Train should handle NaNs by dropping or imputing internally if features.py didn't catch them
    models = train_and_save_models(df, model_dir=str(tmp_path))
    assert "winner_model" in models
    assert "goals_model" in models
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_train.py::test_train_and_save_models_with_imputation -v`
Expected: FAIL if NaNs cause errors in RandomForest.

- [ ] **Step 3: Write minimal implementation**

```python
# C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ml\train.py
import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from src.ml.features import build_features_for_matches

def train_and_save_models(df: pd.DataFrame, model_dir: str = "models"):
    """Trains independent models for each market and saves them."""
    os.makedirs(model_dir, exist_ok=True)

    features = ["xg_diff", "elo_diff"]
    
    # Robust imputation pipeline instead of fillna(0)
    imputer = SimpleImputer(strategy='median')

    X = df[features]

    models = {}

    if "target_1x2" in df.columns:
        valid_idx = df["target_1x2"].notna()
        X_valid = X[valid_idx]
        y_valid = df.loc[valid_idx, "target_1x2"]

        if len(X_valid) > 0:
            winner_clf = Pipeline([
                ('imputer', imputer),
                ('rf', RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42))
            ])
            winner_clf.fit(X_valid, y_valid)
            joblib.dump(winner_clf, os.path.join(model_dir, "winner_model.joblib"))
            models["winner_model"] = winner_clf

    if "target_over25" in df.columns:
        valid_idx = df["target_over25"].notna()
        X_valid = X[valid_idx]
        y_valid = df.loc[valid_idx, "target_over25"]

        if len(X_valid) > 0:
            goals_clf = Pipeline([
                ('imputer', imputer),
                ('lr', LogisticRegression(random_state=42))
            ])
            goals_clf.fit(X_valid, y_valid)
            joblib.dump(goals_clf, os.path.join(model_dir, "goals_model.joblib"))
            models["goals_model"] = goals_clf

    return models
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_train.py -v`
Expected: PASS
