# Ingestion Cron and Scrapling Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a robust automated ingestion pipeline with APScheduler, Scrapling for advanced extraction, Clubelo data integration, and strict Pydantic + Heuristic validation.

**Architecture:** APScheduler runs in the background of the FastAPI app, triggering daily data ingestion and weekly ML retraining. All scraped data passes through Pydantic schemas and volume thresholds before being persisted.

**Tech Stack:** Python, FastAPI, APScheduler, Scrapling, Pydantic.

---

### Task 1: Update Dependencies

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Add APScheduler and Scrapling**

Add the required packages to the end of `backend/requirements.txt`:
```text
apscheduler
scrapling-playwright
pydantic
```

- [ ] **Step 2: Install dependencies**

```bash
docker exec -it betwise_backend pip install -r requirements.txt
```
*(If running locally outside docker: `cd backend && pip install -r requirements.txt`)*

- [ ] **Step 3: Commit**

```bash
git add backend/requirements.txt
git commit -m "chore: add apscheduler and scrapling dependencies"
```

---

### Task 2: Create Data Validators

**Files:**
- Create: `backend/src/ingestion/validators.py`

- [ ] **Step 1: Write Pydantic schemas and heuristic checks**

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class NewsArticle(BaseModel):
    title: str = Field(..., min_length=5)
    summary: str = Field(..., min_length=10)
    url: str

class MatchOdds(BaseModel):
    home_team: str
    away_team: str
    home_odds: float = Field(..., gt=1.0, lt=100.0)
    away_odds: float = Field(..., gt=1.0, lt=100.0)
    draw_odds: float = Field(..., gt=1.0, lt=100.0)

class EloScore(BaseModel):
    team: str
    elo: float = Field(..., gt=500.0, lt=2500.0)
    date: str

def validate_volume(current_count: int, expected_minimum: int = 1) -> bool:
    """Heuristic check: Ensure we didn't scrape 0 or abnormally few items."""
    if current_count < expected_minimum:
        print(f"Validation Error: Extracted {current_count} items, expected at least {expected_minimum}.")
        return False
    return True
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/validators.py
git commit -m "feat: add pydantic validators for ingestion"
```

---

### Task 3: Create Scrapling Wrapper

**Files:**
- Create: `backend/src/ingestion/scrapers/scrapling_base.py`

- [ ] **Step 1: Write the Scrapling base client**

```python
from scrapling import StealthyFetcher

def fetch_page_content(url: str) -> str:
    """Uses Scrapling to stealthily fetch page content."""
    try:
        fetcher = StealthyFetcher()
        page = fetcher.get(url)
        return page.text
    except Exception as e:
        print(f"Scrapling error for {url}: {e}")
        return ""
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/scrapers/scrapling_base.py
git commit -m "feat: add scrapling base wrapper"
```

---

### Task 4: Create Clubelo Scraper

**Files:**
- Create: `backend/src/ingestion/scrapers/clubelo.py`

- [ ] **Step 1: Write Clubelo scraper with validation**

```python
import csv
import io
import requests
from typing import List
from src.ingestion.validators import EloScore, validate_volume
from src.ingestion.normalizer import TeamNormalizer

def fetch_clubelo_stats() -> List[dict]:
    url = "http://api.clubelo.com/eng" # Example endpoint for English teams
    response = requests.get(url)
    if response.status_code != 200:
        return []
    
    csv_data = response.text
    reader = csv.DictReader(io.StringIO(csv_data))
    
    valid_scores = []
    for row in reader:
        try:
            # Pydantic validation
            score = EloScore(
                team=row.get('Club', ''),
                elo=float(row.get('Elo', 0)),
                date=row.get('To', '')
            )
            valid_scores.append(score.dict())
        except Exception:
            continue
            
    if not validate_volume(len(valid_scores), 10):
        return []
        
    return valid_scores
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/scrapers/clubelo.py
git commit -m "feat: add clubelo scraper with validation"
```

---

### Task 5: Configure APScheduler

**Files:**
- Create: `backend/src/ingestion/scheduler.py`
- Modify: `backend/src/main.py`

- [ ] **Step 1: Write the scheduler logic**

Create `backend/src/ingestion/scheduler.py`:
```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.ingestion.tasks import run_daily_scraping
# from src.ml.train import run_weekly_training  # Placeholder for actual training function

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
    # scheduler.add_job(
    #     run_weekly_training,
    #     trigger=CronTrigger(day_of_week='mon', hour=4, minute=0),
    #     id="weekly_training",
    #     replace_existing=True
    # )
    
    scheduler.start()
    print("APScheduler started.")
```

- [ ] **Step 2: Integrate into FastAPI startup**

Modify `backend/src/main.py`. Add the import and call `start_scheduler` in a startup event (or simply at the module level if you prefer, but startup event is safer).
Find the top imports and add:
```python
from contextlib import asynccontextmanager
from src.ingestion.scheduler import start_scheduler
```

Replace `app = FastAPI(...)` with:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    # Could add shutdown logic here

app = FastAPI(title="BetWise API", lifespan=lifespan)
```

- [ ] **Step 3: Commit**

```bash
git add backend/src/ingestion/scheduler.py backend/src/main.py
git commit -m "feat: integrate apscheduler for cron jobs"
```
