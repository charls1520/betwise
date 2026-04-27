# ML Features Bugfix (Data Leakage and Cross-Contamination) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix critical data leakage (`xg_diff` calculation with future data) and cross-contamination (global `ffill` instead of grouping by team) in the Machine Learning inference pipeline.

**Architecture:** 
1. Remove `xg_diff` entirely from training and inference pipelines. 
2. Modify the Elo and xG imputation logic in `build_features_for_matches` to ensure values are carried forward correctly per team rather than globally across all rows.

**Tech Stack:** Python, Pandas, Scikit-learn, XGBoost

---

### Task 1: Fix Cross-Contamination in `features.py` (Per-Team Imputation)

**Files:**
- Modify: `backend/src/ml/features.py`

- [ ] **Step 1: Modify imputation logic in `features.py`**
Replace the global `ffill()` with a grouped approach or simply rely on the historical merge we already do. Actually, the most robust way to handle Elo/xG carry-forward for teams is to do it *after* we build the long-format `team_matches` dataframe, but the script currently tries to do it at the top. Let's fix the top-level imputation to be per-team. However, `Home_xG` and `Away_xG` for future matches are fundamentally flawed if we just carry forward the last match's xG (a team's xG varies wildly per match). Elo *can* be carried forward per team. 
Wait, the easiest and most robust way to fix the `ffill()` bug for `Home_Elo` and `Away_Elo` is to create a temporary long dataframe, sort by date, ffill by team, and map back, OR just use `groupby`.

In `backend/src/ml/features.py`, replace lines 14-17:
```python
    # Impute NaNs with forward fill per team, then global median
    for col in ['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo', 'home_xg', 'away_xg', 'home_elo', 'away_elo']:
        if col in df.columns:
            df[col] = df[col].ffill().fillna(df[col].median()).fillna(0)
```
with a robust per-team Elo imputation. Wait, `Home_Elo` and `Away_Elo` are tied to the *team*. 

```python
    # Impute Elo per team. xG should NOT be ffill'd (it will be removed from diffs anyway)
    if all(col in df.columns for col in ['HomeTeam', 'AwayTeam', 'Date']):
        # Create a long format just for Elo imputation
        temp_home = df[['Date', 'HomeTeam', 'Home_Elo']].rename(columns={'HomeTeam': 'Team', 'Home_Elo': 'Elo'})
        temp_away = df[['Date', 'AwayTeam', 'Away_Elo']].rename(columns={'AwayTeam': 'Team', 'Away_Elo': 'Elo'})
        # Also handle lowercase variants if they exist
        if 'home_elo' in df.columns:
            temp_home['Elo'] = df['home_elo']
            temp_away['Elo'] = df['away_elo']
            
        temp_elo = pd.concat([temp_home, temp_away]).sort_values('Date')
        temp_elo['Elo'] = temp_elo.groupby('Team')['Elo'].ffill()
        
        # Merge back to get the most recent Elo
        df = df.merge(temp_elo.drop_duplicates(['Date', 'Team'], keep='last'), left_on=['Date', 'HomeTeam'], right_on=['Date', 'Team'], how='left', suffixes=('', '_home_imp'))
        df = df.merge(temp_elo.drop_duplicates(['Date', 'Team'], keep='last'), left_on=['Date', 'AwayTeam'], right_on=['Date', 'Team'], how='left', suffixes=('', '_away_imp'))
        
        df['Home_Elo'] = df['Elo'].fillna(df['Home_Elo'] if 'Home_Elo' in df.columns else df['home_elo']).fillna(df['Home_Elo'].median() if 'Home_Elo' in df.columns else 1500)
        df['Away_Elo'] = df['Elo_away_imp'].fillna(df['Away_Elo'] if 'Away_Elo' in df.columns else df['away_elo']).fillna(df['Away_Elo'].median() if 'Away_Elo' in df.columns else 1500)
        
        df = df.drop(columns=['Team', 'Elo', 'Team_away_imp', 'Elo_away_imp'], errors='ignore')
    else:
        # Fallback if no team columns (should not happen in standard flow)
        for col in ['Home_Elo', 'Away_Elo', 'home_elo', 'away_elo']:
            if col in df.columns:
                df[col] = df[col].ffill().fillna(df[col].median()).fillna(0)
```
Wait, the above is too complex and error-prone. A simpler way without breaking everything:
Since we are removing `xg_diff`, we only care about `elo_diff`.
Let's modify `features.py` to fix the imputation properly.

```python
    # Impute NaNs for Elo with forward fill PER TEAM
    if "HomeTeam" in df.columns and "AwayTeam" in df.columns:
        # Create mapping of last known Elo per team
        # We assume the dataframe is already sorted by Date
        last_elo = {}
        home_elo_col = 'Home_Elo' if 'Home_Elo' in df.columns else 'home_elo' if 'home_elo' in df.columns else None
        away_elo_col = 'Away_Elo' if 'Away_Elo' in df.columns else 'away_elo' if 'away_elo' in df.columns else None
        
        if home_elo_col and away_elo_col:
            global_median_elo = pd.concat([df[home_elo_col], df[away_elo_col]]).median()
            if pd.isna(global_median_elo): global_median_elo = 1500.0
            
            home_elos_imputed = []
            away_elos_imputed = []
            
            for idx, row in df.iterrows():
                h_team = row['HomeTeam']
                a_team = row['AwayTeam']
                
                h_elo = row[home_elo_col]
                a_elo = row[away_elo_col]
                
                if pd.notna(h_elo) and h_elo != 0:
                    last_elo[h_team] = h_elo
                elif h_team in last_elo:
                    h_elo = last_elo[h_team]
                else:
                    h_elo = global_median_elo
                    
                if pd.notna(a_elo) and a_elo != 0:
                    last_elo[a_team] = a_elo
                elif a_team in last_elo:
                    a_elo = last_elo[a_team]
                else:
                    a_elo = global_median_elo
                    
                home_elos_imputed.append(h_elo)
                away_elos_imputed.append(a_elo)
                
            df['Home_Elo'] = home_elos_imputed
            df['Away_Elo'] = away_elos_imputed
            df['elo_diff'] = df['Home_Elo'] - df['Away_Elo']
```

- [ ] **Step 2: Remove `xg_diff` calculation from `features.py`**
In `backend/src/ml/features.py`, remove lines 19-28:
```python
    # We now expect 'Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo' instead of shots/corners
    if all(col in df.columns for col in ['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo']):
        df["xg_diff"] = df["Home_xG"] - df["Away_xG"]
        df["elo_diff"] = df["Home_Elo"] - df["Away_Elo"]
    else:
        # Fallback for inference format
        if "home_xg" in df.columns and "away_xg" in df.columns:
            df["xg_diff"] = df["home_xg"] - df["away_xg"]
        if "home_elo" in df.columns and "away_elo" in df.columns:
            df["elo_diff"] = df["home_elo"] - df["away_elo"]
```
And replace with just the Elo diff (which is handled in Step 1 now). We just need to make sure `xg_diff` is NOT created. We can safely delete these lines if we use the logic from Step 1.

- [ ] **Step 3: Run existing tests to ensure they fail/pass appropriately**
```bash
pytest backend/tests/ml/test_features.py -v
```
(Some tests might fail if they explicitly check for `xg_diff`. We will fix them in Task 4).

### Task 2: Remove `xg_diff` from Training Pipeline

**Files:**
- Modify: `backend/src/ml/train.py`

- [ ] **Step 1: Remove `xg_diff` from `features` list**
In `backend/src/ml/train.py`, locate the `features` list (around line 93):
```python
    features = [
        "xg_diff", "elo_diff", "rest_days_diff", "shots_on_target_diff", 
        "is_end_of_season", "goals_scored_general_diff", "goals_conceded_general_diff",
        "offensive_efficiency_diff", "defensive_efficiency_diff"
    ]
```
Change it to:
```python
    features = [
        "elo_diff", "rest_days_diff", "shots_on_target_diff", 
        "is_end_of_season", "goals_scored_general_diff", "goals_conceded_general_diff",
        "offensive_efficiency_diff", "defensive_efficiency_diff"
    ]
```

- [ ] **Step 2: Commit**
```bash
git add backend/src/ml/features.py backend/src/ml/train.py
git commit -m "fix(ml): remove xg_diff to prevent data leakage and fix elo cross-contamination"
```

### Task 3: Remove `xg_diff` from Inference Pipeline

**Files:**
- Modify: `backend/src/ml/inference.py`

- [ ] **Step 1: Remove `xg_diff` from `features` list in `inference.py`**
In `backend/src/ml/inference.py`, locate the `features` list (around line 44):
```python
    features = [
        "xg_diff", "elo_diff", "rest_days_diff", "shots_on_target_diff", 
        "is_end_of_season", "goals_scored_general_diff", "goals_conceded_general_diff",
        "offensive_efficiency_diff", "defensive_efficiency_diff"
    ]
```
Change it to:
```python
    features = [
        "elo_diff", "rest_days_diff", "shots_on_target_diff", 
        "is_end_of_season", "goals_scored_general_diff", "goals_conceded_general_diff",
        "offensive_efficiency_diff", "defensive_efficiency_diff"
    ]
```

- [ ] **Step 2: Commit**
```bash
git add backend/src/ml/inference.py
git commit -m "fix(ml): remove xg_diff from inference pipeline"
```

### Task 4: Fix Unit Tests

**Files:**
- Modify: `backend/tests/ml/test_features.py`
- Modify: `backend/tests/ml/test_inference.py` (if necessary)

- [ ] **Step 1: Run tests to find breakages**
```bash
pytest backend/tests/ml/ -v
```

- [ ] **Step 2: Fix `test_features.py`**
If `test_features.py` asserts that `xg_diff` is in the output columns, remove that assertion. 
Also, add a test to verify per-team Elo imputation:
```python
def test_elo_imputation_per_team():
    matches = [
        {"Date": "2024-01-01", "HomeTeam": "TeamA", "AwayTeam": "TeamB", "Home_Elo": 1600, "Away_Elo": 1400},
        {"Date": "2024-01-02", "HomeTeam": "TeamC", "AwayTeam": "TeamD", "Home_Elo": 1500, "Away_Elo": 1500},
        {"Date": "2024-01-03", "HomeTeam": "TeamA", "AwayTeam": "TeamC", "Home_Elo": None, "Away_Elo": None} # Should inherit 1600 and 1500
    ]
    df = build_features_for_matches(matches)
    assert df.iloc[2]["Home_Elo"] == 1600
    assert df.iloc[2]["Away_Elo"] == 1500
    assert "xg_diff" not in df.columns
```

- [ ] **Step 3: Fix `test_inference.py`**
Ensure the mock data used in `test_predict_matches` does not rely on `xg_diff` being passed to the model. Update the mock models to expect 8 features instead of 9.

- [ ] **Step 4: Run tests to verify passes**
```bash
pytest backend/tests/ml/ -v
```
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add backend/tests/ml/test_features.py backend/tests/ml/test_inference.py
git commit -m "test(ml): update tests for removed xg_diff and new elo imputation"
```
