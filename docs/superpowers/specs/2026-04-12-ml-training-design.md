# Machine Learning Training Data & Model Implementation

## 1. Overview
This spec covers the transition from dummy data modeling to a fully trained, real-world Machine Learning model for BetWise.
We will build a historical data pipeline combining authoritative CSVs from `football-data.co.uk` with historical xG scraped from `Understat`, and retrain our `scikit-learn` algorithms (RandomForest for 1X2, LogisticRegression for Goals).

## 2. Historical Data Sourcing (The "A" Approach)

### 2.1 Core Match Statistics & Closing Odds
*   **Source:** `football-data.co.uk` (Free, Auditable, Gold Standard for betting analytics).
*   **Method:** A Python script (`src/ingestion/historical.py`) that iteratively downloads the `.csv` files for the English Premier League (`E0.csv`) spanning the last 5 completed seasons.
*   **Data Points:** Match Date, Home Team, Away Team, Full Time Result (FTR), Full Time Home Goals (FTHG), Full Time Away Goals (FTAG), Home Shots on Target (HST), Away Shots on Target (AST), Home Corners (HC), Away Corners (AC), and Historical Pinnacle Closing Odds for 1X2.

### 2.2 Advanced Metrics (Historical xG)
*   **Source:** `Understat` (via our existing Playwright scraper framework).
*   **Method:** An extended script that navigates historical season pages on Understat to extract final team xG averages, providing the crucial "Expected Goals" feature for our goal probability model.

## 3. Feature Engineering & Target Variables
Before training, the raw historical data must be transformed.

### 3.1 Derived Features
*   `shots_on_target_diff`: The historical difference in shots on target between the two teams.
*   `corner_diff`: Difference in corner creation.
*   `xg_diff_avg`: The difference in expected goals between the two teams leading into the match (calculated from historical rolling averages, or approximated via final season xG for simplicity in v1).

### 3.2 Target Variables
*   `target_1x2`: 2 (Home Win), 1 (Draw), 0 (Away Win). Derived from `FTR` column in CSV.
*   `target_over25`: 1 (Total Goals > 2.5), 0 (Total Goals <= 2.5). Derived from `FTHG` + `FTAG`.

## 4. Model Training Pipeline Update
*   **Module:** `src/ml/train.py`
*   **Action:** The training script will no longer accept a dummy DataFrame of 6 rows. It will:
    1. Read the combined historical dataset from SQLite or CSV (`data/historical/master.csv`).
    2. Clean `NaN` values and apply the `TeamNormalizer` (crucial: mapping football-data.co.uk names like "Man United" to our canonical "Manchester United").
    3. Split data (80% Train / 20% Test) to evaluate model accuracy.
    4. Train `RandomForestClassifier` (1X2) and `LogisticRegression` (Goals).
    5. Save the robust `.joblib` files to `models/`.

## 5. Execution Workflow
1. Run `python src/ingestion/historical.py` once to build the dataset.
2. Run `python src/ml/train.py` to produce the real models.
3. Restart `uvicorn`. The `/api/dashboard` endpoint will now load these real models, process today's matches, and output genuine probabilities instead of `0.0%`.