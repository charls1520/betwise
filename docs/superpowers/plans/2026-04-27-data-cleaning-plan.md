# Data Cleaning Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up the historical dataset and ML features by filtering out unnecessary columns and keeping missing data as `NaN` instead of artificially filling with `0`.

**Architecture:** 
1. `historical.py`: Introduce a whitelist of required columns when processing football-data.co.uk CSVs to drastically reduce cached dataset size.
2. `features.py`: Stop computing obsolete target variables like `target_over25`, purge intermediate columns before returning the features DataFrame, and preserve `NaN`s in fallback logic.

**Tech Stack:** Python, Pandas

---

### Task 1: Historical Data Ingestion Cleanup (Whitelist)

**Files:**
- Modify: `backend/src/ingestion/historical.py`

- [ ] **Step 1: Apply whitelist column filter in `download_football_data_co_uk`**

In `backend/src/ingestion/historical.py`, find the section where the CSV is read (around line 79-80):
```python
                csv_text = fetch_with_retry(url)
                df = pd.read_csv(io.StringIO(csv_text))
                df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
                df = df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam'])
                df = df.copy()
```

Modify it to include the whitelist filter:
```python
                csv_text = fetch_with_retry(url)
                df = pd.read_csv(io.StringIO(csv_text))
                df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
                df = df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam'])
                
                # Apply column whitelist
                whitelist_cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HST', 'AST', 'B365H', 'B365D', 'B365A']
                existing_whitelist = [col for col in whitelist_cols if col in df.columns]
                df = df[existing_whitelist].copy()
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/historical.py
git commit -m "refactor(ingestion): apply column whitelist to historical data CSV downloads"
```

### Task 2: Remove Obsolete Variables and Purge Intermediate Features

**Files:**
- Modify: `backend/src/ml/features.py`
- Modify: `backend/tests/ml/test_features.py`

- [ ] **Step 1: Write failing/updated tests**

In `backend/tests/ml/test_features.py`, modify `test_build_features_for_matches` to check for removal of `target_over25` and intermediate columns:
```python
def test_build_features_for_matches():
    # Mock some raw match data
    data = [
        {
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "home_xg": 2.1,
            "away_xg": 0.8,
            "home_goals": 2,
            "away_goals": 0,
            "FTR": "H",
            "FTHG": 2,
            "FTAG": 0
        }
    ]

    df = build_features_for_matches(data)
    assert not df.empty
    assert "xg_diff" not in df.columns
    assert "target_1x2" in df.columns
    # Check target_over25 is removed
    assert "target_over25" not in df.columns
    # Check intermediate columns are dropped
    assert "home_rest_days" not in df.columns
    assert "away_rest_days" not in df.columns
    assert "home_avg_shots_on_target" not in df.columns
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/ml/test_features.py::test_build_features_for_matches -v`
Expected: FAIL because `target_over25` and `home_rest_days` are still present.

- [ ] **Step 3: Modify `features.py` to remove `target_over25` and intermediate columns**

In `backend/src/ml/features.py`, remove the `target_over25` calculation (around line 193):
```python
    if "FTHG" in df.columns and "FTAG" in df.columns:
        df["target_over25"] = ((df["FTHG"] + df["FTAG"]) > 2.5).astype(int)
```
-> DELETE those lines.

Then, at the very end of the function (before `return df`), add the purge logic:
```python
    # Drop intermediate and unneeded base columns
    cols_to_drop = [
        'home_rest_days', 'away_rest_days',
        'home_avg_shots_on_target', 'away_avg_shots_on_target',
        'home_end_of_season', 'away_end_of_season',
        'home_avg_goals_scored_general', 'away_avg_goals_scored_general',
        'home_avg_goals_conceded_general', 'away_avg_goals_conceded_general',
        'home_avg_goals_scored_home', 'away_avg_goals_scored_home',
        'home_avg_goals_conceded_home', 'away_avg_goals_conceded_home',
        'home_avg_goals_scored_away', 'away_avg_goals_scored_away',
        'home_avg_goals_conceded_away', 'away_avg_goals_conceded_away',
        'home_offensive_efficiency', 'away_offensive_efficiency',
        'home_defensive_efficiency', 'away_defensive_efficiency',
        'home_implied_prob', 'away_implied_prob'
    ]
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest backend/tests/ml/test_features.py -v`
Expected: PASS. (Note: other tests might fail if they explicitly check for the dropped columns like `home_rest_days`. Fix them in the next task).

- [ ] **Step 5: Commit**

```bash
git add backend/src/ml/features.py backend/tests/ml/test_features.py
git commit -m "refactor(ml): drop intermediate columns and obsolete target_over25 feature"
```

### Task 3: Stop Injecting Fake Zeros in Fallback logic

**Files:**
- Modify: `backend/src/ml/features.py`
- Modify: `backend/tests/ml/test_features.py`

- [ ] **Step 1: Write test for NaN preservation**

Add to `backend/tests/ml/test_features.py`:
```python
def test_fallback_preserves_nans():
    # If a dataframe lacks the required base columns for efficiency/rest_days
    # the fallback logic shouldn't inject 0, it should be np.nan
    df = build_features_for_matches([{"Date": "2024-01-01"}])
    # The columns will just be missing or if they are created, they should be NaN
    # Since we drop them anyway, let's just check the final diff columns:
    assert pd.isna(df.loc[0, "rest_days_diff"])
    assert pd.isna(df.loc[0, "offensive_efficiency_diff"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/ml/test_features.py::test_fallback_preserves_nans -v`
Expected: FAIL because fallbacks currently inject `0`.

- [ ] **Step 3: Modify `features.py` fallback logic**

In `backend/src/ml/features.py`, find the fallback section (around line 186):
```python
    else:
        # Fallbacks si no hay suficientes columnas
        for col in ['home_rest_days', 'away_rest_days', 'rest_days_diff', 'shots_on_target_diff', 'is_end_of_season', 'offensive_efficiency_diff', 'defensive_efficiency_diff']:
            if col not in df.columns:
                df[col] = 0
```

Change it to:
```python
    else:
        # Fallbacks si no hay suficientes columnas
        for col in ['home_rest_days', 'away_rest_days', 'rest_days_diff', 'shots_on_target_diff', 'is_end_of_season', 'offensive_efficiency_diff', 'defensive_efficiency_diff']:
            if col not in df.columns:
                df[col] = np.nan
```

- [ ] **Step 4: Fix broken tests**

Since we dropped `home_rest_days` etc., any test in `test_features.py` that asserts `assert "home_rest_days" in df.columns` will fail.
In `test_new_ml_features()`, change:
```python
    assert "home_rest_days" in df.columns
    assert "away_rest_days" in df.columns
    # ...
    assert df.loc[2, "home_rest_days"] == 10.0
```
to assert on the diffs instead or don't assert on dropped intermediate columns:
```python
    # Assert on final features instead of dropped intermediate ones
    assert "rest_days_diff" in df.columns
    assert "shots_on_target_diff" in df.columns
```
Remove `assert df.loc[2, "home_rest_days"] == 10.0` or replace it with an assertion on `rest_days_diff`. Since TeamA had 10 rest days and TeamD had missing/default 10, the diff would be 0. So just drop the `home_rest_days` assertion.

- [ ] **Step 5: Run tests**

Run: `pytest backend/tests/ml/ -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/src/ml/features.py backend/tests/ml/test_features.py
git commit -m "fix(ml): preserve NaNs in fallback logic instead of injecting zeros"
```
