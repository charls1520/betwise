# Spec: Continuous ML Training with Live Data

## Context
BetWise requires the Machine Learning models to learn continuously from new matches played in the current season, as opposed to remaining static after the initial training on past seasons. 
Although the daily `data/raw/` (Data Lake) stores odds and some pre-match xG statistics, the cleanest and most reliable source for completed match results and post-match xG is `football-data.co.uk` and Understat's historical endpoints.

## 1. Updating the Historical Ingestion Engine
### Design
- **Support for Current Seasons**: The `download_football_data_co_uk` function in `backend/src/ingestion/historical.py` will be modified to include the current active seasons by default (e.g., "2425" for 2024-2025 and "2526" for 2025-2026).
- **Year Mapping Extension**: The `season_to_year` dictionary within that function will be updated to map these new season strings to their starting years (e.g., `"2425": "2024"`, `"2526": "2025"`).
- **Incremental Data Merge**: As `historical.py` already includes logic to identify `left_only` missing rows between newly downloaded CSVs and the existing `merged_history_cache.csv`, it will organically fetch only the recently completed matches, query Understat and Clubelo for the specific dates, and append them to the cache cleanly.

## 2. Weekly Automated Re-training Job
### Design
- **Scheduler Integration**: A new job will be added to `backend/src/ingestion/scheduler.py` using APScheduler to trigger the `train.py` script automatically every week.
- **Execution Window**: The re-training will occur on **Mondays at 04:00 AM (UTC-5)**, ensuring all weekend matches are finalized and published by the data providers.
- **Pipeline Execution**: The scheduled job will invoke a function that:
  1. Calls `download_football_data_co_uk()` to download recent matches and append them to the cache.
  2. Builds the engineered features from the updated cache.
  3. Calls `train_and_save_models()` to train a new generation of models on the expanded dataset.
  4. Relies on the already implemented validation mechanisms in `train.py` to prevent performance regression (checking Accuracy against the previous model) before saving the new `.joblib` files.

## 3. Operational Impact
- **Simplicity over Complexity**: By leveraging the existing historical extraction script, we avoid creating a brittle, complex reconciliation engine that attempts to piece together match results from raw pre-match API payloads.
- **Data Integrity**: `football-data.co.uk` acts as the definitive source of truth for results, maintaining the strict data quality needed for robust ML.
- **Self-Sustaining**: The application becomes fully autonomous, improving its predictions week-over-week without manual intervention.