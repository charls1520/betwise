# Backend Hardcodes & Mocks Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate hardcoded fallback keys, temporary mocks in ML reliability checks, and clean up environment variables in the backend.

**Architecture:** We will replace the fallback "DEMO_KEY" with a strict environment variable check in the ETL tasks, remove the default true behavior in data thresholds, and prune outdated config files to ensure deterministic and safe behavior in production.

**Tech Stack:** Python 3.11+, FastAPI, pytest

---

### Task 1: Enforce API Key in Ingestion Tasks

**Files:**
- Create: `backend/tests/ingestion/test_tasks.py`
- Modify: `backend/src/ingestion/tasks.py:16-20`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/ingestion/test_tasks.py
import pytest
import os
from src.ingestion.tasks import run_daily_scraping

def test_run_daily_scraping_requires_api_key(monkeypatch):
    # Ensure ODDS_API_KEY is not set
    monkeypatch.delenv("ODDS_API_KEY", raising=False)
    
    with pytest.raises(ValueError, match="ODDS_API_KEY is not set in environment variables"):
        run_daily_scraping()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/ingestion/test_tasks.py -v`
Expected: FAIL because `run_daily_scraping` falls back to "DEMO_KEY" instead of raising an error.

- [ ] **Step 3: Write minimal implementation**

```python
# Modify backend/src/ingestion/tasks.py lines 16-20
def run_daily_scraping(odds_api_key: str = None):
    if odds_api_key is None:
        odds_api_key = os.environ.get("ODDS_API_KEY")
        if not odds_api_key or odds_api_key == "DEMO_KEY":
            raise ValueError("ODDS_API_KEY is not set in environment variables")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/ingestion/test_tasks.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/tests/ingestion/test_tasks.py backend/src/ingestion/tasks.py
git commit -m "refactor(backend): enforce ODDS_API_KEY and remove DEMO_KEY fallback"
```

---

### Task 2: Remove Mock Logic in Reliability Data Thresholds

**Files:**
- Modify: `backend/tests/ml/test_reliability.py:14-22`
- Modify: `backend/src/ml/reliability.py:21-28`

- [ ] **Step 1: Update the test to expect strict validation**

```python
# Modify backend/tests/ml/test_reliability.py lines 14-22
def test_data_threshold():
    # Strict validation: matches_played must exist and be >= 10
    stats = {"Arsenal": {"xg_for_avg": 2.1, "matches_played": 15}}
    assert meets_data_threshold("Arsenal", stats) is True

    stats_low = {"Ipswich": {"xg_for_avg": 1.1, "matches_played": 5}}
    assert meets_data_threshold("Ipswich", stats_low) is False

    stats_mocked = {"Chelsea": {"xg_for_avg": 1.5}}
    # Should now fail because matches_played is missing
    assert meets_data_threshold("Chelsea", stats_mocked) is False

    assert meets_data_threshold("Unknown Team", stats) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/ml/test_reliability.py -v`
Expected: FAIL because `meets_data_threshold` currently returns True if data exists but `matches_played` is missing.

- [ ] **Step 3: Update implementation to remove mock logic**

```python
# Modify backend/src/ml/reliability.py lines 21-28
    team_data = xg_stats[team_name]
    
    # Require explicit 'matches_played' key and enforce threshold
    if "matches_played" not in team_data:
        return False
        
    return team_data["matches_played"] >= min_matches
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/ml/test_reliability.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/tests/ml/test_reliability.py backend/src/ml/reliability.py
git commit -m "refactor(backend): remove mock logic in meets_data_threshold validation"
```

---

### Task 3: Clean up environment files

**Files:**
- Delete: `backend/.env.old`
- Modify: `backend/.env.example`

- [ ] **Step 1: Delete outdated environment file**

Run: `rm backend/.env.old`

- [ ] **Step 2: Update example environment variables**

```bash
# Modify backend/.env.example to remove DEMO_KEY
# Change line 24 (or wherever ODDS_API_KEY is) to:
ODDS_API_KEY=tu_api_key_aqui
```

*(Note: Since `.env.example` is short, just search for `ODDS_API_KEY=DEMO_KEY` and replace it with `ODDS_API_KEY=tu_api_key_aqui`)*

- [ ] **Step 3: Commit**

```bash
git add backend/.env.old backend/.env.example
git commit -m "chore(backend): clean up environment files and remove DEMO_KEY"
```