# Continuous ML Training Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable continuous ML training by updating the historical extraction script to include the current season and scheduling a weekly re-training job.

**Architecture:** `historical.py` will fetch current active seasons. `train.py` will expose a callable function that orchestrates fetching and training. `scheduler.py` will trigger this function every Monday at 4:00 AM.

**Tech Stack:** Python, pandas, APScheduler, scikit-learn.

---

### Task 1: Update Historical Ingestion to Current Seasons

**Files:**
- Modify: `backend/src/ingestion/historical.py`
- Test: `backend/tests/ingestion/test_historical.py`

- [ ] **Step 1: Write/Update the failing test**
In `backend/tests/ingestion/test_historical.py`, check if `download_football_data_co_uk` defaults are updated.

```python
# Add to backend/tests/ingestion/test_historical.py if not present, or modify existing to check arguments.
from unittest.mock import patch
from src.ingestion.historical import download_football_data_co_uk

@patch("src.ingestion.historical.pd.read_csv")
@patch("src.ingestion.historical.fetch_with_retry")
@patch("src.ingestion.historical.LEAGUES_CONFIG", [])
def test_download_football_data_co_uk_defaults(mock_fetch, mock_read):
    import inspect
    sig = inspect.signature(download_football_data_co_uk)
    seasons_default = sig.parameters['seasons'].default
    assert "2425" in seasons_default
    assert "2526" in seasons_default
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/ingestion/test_historical.py -v`
Expected: FAIL because defaults don't contain 2425.

- [ ] **Step 3: Write minimal implementation**

Modify `backend/src/ingestion/historical.py` around line 38:

```python
# Change default seasons
def download_football_data_co_uk(seasons: list = ["2526", "2425", "2324", "2223", "2122"]) -> pd.DataFrame:
    base_url = "https://www.football-data.co.uk/mmz4281/{}/{}.csv"
    
    # ... further down inside the function around line 57
    season_to_year = {
        "2526": "2025",
        "2425": "2024",
        "2324": "2023",
        "2223": "2022",
        "2122": "2021",
        "2021": "2020",
        "1920": "2019"
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/ingestion/test_historical.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ingestion/historical.py backend/tests/ingestion/test_historical.py
git commit -m "feat(ingestion): expand historical ingestion to support current active seasons"
```

---

### Task 2: Create `run_weekly_training` Orchestrator

**Files:**
- Modify: `backend/src/ml/train.py`
- Test: `backend/tests/ml/test_train.py`

- [ ] **Step 1: Write the failing test**

```python
# In backend/tests/ml/test_train.py add:
from src.ml.train import run_weekly_training

@patch("src.ml.train.train_and_save_models")
@patch("src.ml.train.build_features_for_matches")
@patch("src.ml.train.download_football_data_co_uk")
def test_run_weekly_training(mock_download, mock_build, mock_train):
    mock_download.return_value = pd.DataFrame([{"dummy": "data"}])
    mock_build.return_value = pd.DataFrame([{"feat": 1}])
    
    run_weekly_training()
    
    mock_download.assert_called_once()
    mock_build.assert_called_once()
    mock_train.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/ml/test_train.py::test_run_weekly_training -v`
Expected: FAIL because `run_weekly_training` doesn't exist.

- [ ] **Step 3: Write minimal implementation**

Modify `backend/src/ml/train.py`. Remove the `if __name__ == "__main__":` logic and move it to `run_weekly_training`:

```python
# Add at the bottom of backend/src/ml/train.py
def run_weekly_training():
    from src.rag.config import init_llama_index
    init_llama_index()

    from src.ingestion.historical import download_football_data_co_uk
    from src.utils.logger import get_logger

    logger = get_logger()

    logger.info("Starting weekly ML continuous training...")
    logger.info("Downloading historical/live data...")
    raw_df = download_football_data_co_uk()

    if not raw_df.empty:
        logger.info(f"Downloaded {len(raw_df)} historical/live matches.")
        logger.info("Engineering features...")
        df_features = build_features_for_matches(raw_df.to_dict("records"))

        logger.info("Training models...")
        train_and_save_models(df_features)
        logger.info("Continuous models trained and saved successfully.")
    else:
        logger.error("Failed to download historical data. Aborting training.")

if __name__ == "__main__":
    run_weekly_training()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/ml/test_train.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ml/train.py backend/tests/ml/test_train.py
git commit -m "feat(ml): extract weekly training orchestrator to run_weekly_training function"
```

---

### Task 3: Enable Weekly Training in APScheduler

**Files:**
- Modify: `backend/src/ingestion/scheduler.py`
- Test: `backend/tests/ingestion/test_tasks.py` (or manually verify)

- [ ] **Step 1: Write minimal implementation**

Modify `backend/src/ingestion/scheduler.py` around line 5:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.ingestion.tasks import run_daily_scraping
from src.utils.logger import get_logger
from src.ml.train import run_weekly_training

logger = get_logger()

scheduler = BackgroundScheduler()

def start_scheduler():
    # Run scraping every day at 02:00 AM
    scheduler.add_job(
        run_daily_scraping,
        trigger=CronTrigger(hour=2, minute=0),
        id="daily_scraping",
        replace_existing=True
    )
    
    # Run ML retraining every Monday at 04:00 AM
    scheduler.add_job(
        run_weekly_training,
        trigger=CronTrigger(day_of_week='mon', hour=4, minute=0),
        id="weekly_training",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("APScheduler started with daily ingestion and weekly ML training.")
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/scheduler.py
git commit -m "feat(ingestion): enable automatic weekly ML training job via APScheduler"
```
