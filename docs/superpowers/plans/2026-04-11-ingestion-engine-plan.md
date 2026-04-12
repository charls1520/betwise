# Ingestion and Normalization Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a robust, two-stage Data Lake -> ETL pipeline to scrape, normalize (using fuzzy matching), and ingest sports data into the backend database.

**Architecture:** Python-based scrapers save raw JSON files locally. A separate ETL module reads these files, maps unknown team names to canonical IDs using `thefuzz`, and stores structured data in SQLite.

**Tech Stack:** Python 3.10+, FastAPI (backend context), SQLAlchemy, `requests`, `thefuzz`, `pytest`.

---

### Task 1: Setup Dependencies and Raw Data Storage

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/src/ingestion/__init__.py`
- Create: `backend/src/ingestion/storage.py`
- Create: `backend/tests/ingestion/__init__.py`
- Create: `backend/tests/ingestion/test_storage.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/ingestion/test_storage.py
import os
import json
from src.ingestion.storage import save_raw_data

def test_save_raw_data(tmp_path):
    data = {"test": "data", "teams": ["Arsenal", "Chelsea"]}
    filepath = save_raw_data("stats", data, base_dir=str(tmp_path))
    
    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        loaded = json.load(f)
        assert loaded["test"] == "data"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ingestion/test_storage.py -v`
Expected: FAIL (ModuleNotFoundError or similar)

- [ ] **Step 3: Update dependencies and write minimal implementation**

Modify `backend/requirements.txt`:
Append to the end of the file:
```text
thefuzz
python-Levenshtein
```

```python
# backend/src/ingestion/storage.py
import os
import json
from datetime import datetime

def save_raw_data(source_type: str, data: dict, base_dir: str = "data/raw") -> str:
    """Saves raw data to a local directory partitioned by date."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    dir_path = os.path.join(base_dir, date_str)
    os.makedirs(dir_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{source_type}_{timestamp}.json"
    filepath = os.path.join(dir_path, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    return filepath
```

- [ ] **Step 4: Install new dependencies and run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && pip install -r requirements.txt && set PYTHONPATH=. && pytest tests/ingestion/test_storage.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/requirements.txt backend/src/ingestion/ backend/tests/ingestion/
git commit -m "feat(ingestion): add raw data storage utility and update dependencies"
```

### Task 2: Create Fuzzy Name Normalizer

**Files:**
- Create: `backend/src/ingestion/normalizer.py`
- Create: `backend/tests/ingestion/test_normalizer.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/ingestion/test_normalizer.py
from src.ingestion.normalizer import TeamNormalizer

def test_normalize_team_name():
    canonical_teams = ["Manchester United", "Arsenal", "Chelsea"]
    normalizer = TeamNormalizer(canonical_teams)
    
    assert normalizer.normalize("Man Utd") == "Manchester United"
    assert normalizer.normalize("Arsenal FC") == "Arsenal"
    assert normalizer.normalize("The Blues") is None  # Below confidence threshold
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ingestion/test_normalizer.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/ingestion/normalizer.py
from thefuzz import process
from typing import List, Optional

class TeamNormalizer:
    def __init__(self, canonical_teams: List[str], threshold: int = 80):
        self.canonical_teams = canonical_teams
        self.threshold = threshold
        
        # Hardcoded overrides for common aliases that fuzzy matching might miss
        self.manual_overrides = {
            "man utd": "Manchester United",
            "man city": "Manchester City",
            "spurs": "Tottenham Hotspur"
        }

    def normalize(self, raw_name: str) -> Optional[str]:
        raw_lower = raw_name.lower().strip()
        
        if raw_lower in self.manual_overrides:
            return self.manual_overrides[raw_lower]

        match, score = process.extractOne(raw_name, self.canonical_teams)
        
        if score >= self.threshold:
            return match
        return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ingestion/test_normalizer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ingestion/normalizer.py backend/tests/ingestion/test_normalizer.py
git commit -m "feat(ingestion): implement fuzzy team name normalizer"
```

### Task 3: Dummy Scraper and ETL Pipeline Integration

**Files:**
- Create: `backend/src/ingestion/pipeline.py`
- Create: `backend/tests/ingestion/test_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/ingestion/test_pipeline.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.models import Team
from src.ingestion.pipeline import run_etl_pipeline
import os
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_pipeline.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_run_etl_pipeline(tmp_path):
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Pre-seed canonical team
    db.add(Team(name="Arsenal FC", canonical_name="Arsenal"))
    db.commit()
    
    # Create fake raw data
    raw_data = {"matches": [{"home": "Arsenal FC", "away": "Chelsea", "home_goals": 2}]}
    filepath = os.path.join(tmp_path, "fake_stats.json")
    with open(filepath, "w") as f:
        json.dump(raw_data, f)
        
    # Run pipeline
    results = run_etl_pipeline(db, filepath)
    
    assert len(results["normalized_matches"]) == 1
    assert results["normalized_matches"][0]["home_canonical"] == "Arsenal"
    
    db.close()
    Base.metadata.drop_all(bind=engine)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ingestion/test_pipeline.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/ingestion/pipeline.py
import json
from sqlalchemy.orm import Session
from src.models import Team
from src.ingestion.normalizer import TeamNormalizer

def run_etl_pipeline(db: Session, raw_filepath: str) -> dict:
    with open(raw_filepath, "r") as f:
        raw_data = json.load(f)
        
    # Get canonical teams from DB
    teams = db.query(Team).all()
    canonical_names = [t.canonical_name for t in teams if t.canonical_name]
    
    normalizer = TeamNormalizer(canonical_names)
    normalized_matches = []
    
    for match in raw_data.get("matches", []):
        home_raw = match.get("home")
        home_canonical = normalizer.normalize(home_raw) if home_raw else None
        
        normalized_matches.append({
            "original_home": home_raw,
            "home_canonical": home_canonical,
            "home_goals": match.get("home_goals")
        })
        
    return {"normalized_matches": normalized_matches}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ingestion/test_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ingestion/pipeline.py backend/tests/ingestion/test_pipeline.py
git commit -m "feat(ingestion): add ETL pipeline for json matching"
```