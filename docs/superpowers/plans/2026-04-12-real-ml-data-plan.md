# Real ML Engine & Scraping Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement strict team normalization, historical data fetching (via Understat), and retrain the ML engine solely on real, auditable data.

**Architecture:** Extend the current `TeamNormalizer` to enforce strict confidence thresholds. Create an `understat_scraper.py` to get real xG data. Update `inference.py` and `train.py` to use this real data instead of mock values.

**Tech Stack:** Python 3.10+, `requests`, `beautifulsoup4`, `scikit-learn`, `thefuzz`.

---

### Task 1: Strict Team Normalizer Update

**Files:**
- Modify: `backend/src/ingestion/normalizer.py`
- Modify: `backend/tests/ingestion/test_normalizer.py`

- [ ] **Step 1: Write the failing test**

Modify `backend/tests/ingestion/test_normalizer.py`:
```python
# backend/tests/ingestion/test_normalizer.py
from src.ingestion.normalizer import TeamNormalizer

def test_strict_normalize_team_name():
    canonical_teams = ["Manchester United", "Arsenal", "Chelsea"]
    normalizer = TeamNormalizer(canonical_teams, threshold=95)
    
    assert normalizer.normalize("Man Utd") == "Manchester United" # via manual override
    assert normalizer.normalize("Arsenal FC") is None # Fails 95% threshold without override
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ingestion/test_normalizer.py -v`
Expected: FAIL (Arsenal FC matches with high enough score in old threshold, fails here if old logic applies, but we want it to return None unless explicitly in overrides or exact match >95%)

- [ ] **Step 3: Write minimal implementation**

Modify `backend/src/ingestion/normalizer.py`:
```python
# backend/src/ingestion/normalizer.py
from thefuzz import process
from typing import List, Optional

class TeamNormalizer:
    def __init__(self, canonical_teams: List[str], threshold: int = 95):
        self.canonical_teams = canonical_teams
        self.threshold = threshold
        
        # Hardcoded, exhaustive overrides for strict matching
        self.manual_overrides = {
            "man utd": "Manchester United",
            "manchester utd": "Manchester United",
            "man city": "Manchester City",
            "manchester city": "Manchester City",
            "spurs": "Tottenham Hotspur",
            "tottenham": "Tottenham Hotspur",
            "arsenal fc": "Arsenal",
            "chelsea fc": "Chelsea"
        }

    def normalize(self, raw_name: str) -> Optional[str]:
        raw_lower = raw_name.lower().strip()
        
        if raw_lower in self.manual_overrides:
            return self.manual_overrides[raw_lower]

        match_result = process.extractOne(raw_name, self.canonical_teams)
        if not match_result:
            return None
            
        match, score = match_result[:2]
        
        if score >= self.threshold:
            return match
            
        # Log unmapped team exception here in a real scenario
        print(f"WARNING: Unmapped team name '{raw_name}' (Score: {score}). Needs manual override.")
        return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ingestion/test_normalizer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ingestion/normalizer.py backend/tests/ingestion/test_normalizer.py
git commit -m "feat(ingestion): enforce strict 95% threshold on fuzzy team normalization"
```

### Task 2: Implement Understat Scraper (xG Data)

**Files:**
- Create: `backend/src/ingestion/scrapers/understat.py`
- Create: `backend/tests/ingestion/test_understat.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/ingestion/test_understat.py`:
```python
import pytest
from src.ingestion.scrapers.understat import fetch_current_xg_stats

def test_fetch_current_xg_stats(monkeypatch):
    class MockResponse:
        @property
        def text(self):
            return '<html><body><script>var teamsData = {"1": {"title": "Arsenal", "history": [{"xG": 2.1, "xGA": 0.5}]}};</script></body></html>'
        def raise_for_status(self):
            pass

    monkeypatch.setattr("requests.get", lambda url: MockResponse())
    
    stats = fetch_current_xg_stats()
    assert "Arsenal" in stats
    assert stats["Arsenal"]["xg_for_avg"] == 2.1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ingestion/test_understat.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

Create `backend/src/ingestion/scrapers/understat.py`:
```python
import requests
import re
import json
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_current_xg_stats() -> dict:
    """Scrapes Understat for current season xG averages per team."""
    url = "https://understat.com/league/EPL"
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.find_all('script')
    
    team_data_script = None
    for script in scripts:
        if script.string and "var teamsData" in script.string:
            team_data_script = script.string
            break
            
    if not team_data_script:
        return {}
        
    # Extract JSON string from script
    json_match = re.search(r"var teamsData\s*=\s*JSON\.parse\('([^']+)'\);", team_data_script)
    if json_match:
        # Understat uses hex-encoded JSON in JS
        decoded = bytes(json_match.group(1), "utf-8").decode("unicode_escape")
        try:
            data = json.loads(decoded)
        except:
            return {}
    else:
        # Try direct assignment pattern just in case
        json_match = re.search(r"var teamsData\s*=\s*({.*?});", team_data_script)
        if not json_match:
            return {}
        data = json.loads(json_match.group(1))

    stats = {}
    for team_id, team_info in data.items():
        title = team_info.get("title")
        history = team_info.get("history", [])
        if not history:
            continue
            
        # Calculate simple averages from history
        total_xg = sum(float(match.get("xG", 0)) for match in history)
        total_xga = sum(float(match.get("xGA", 0)) for match in history)
        matches_played = len(history)
        
        stats[title] = {
            "xg_for_avg": total_xg / matches_played if matches_played else 0,
            "xg_against_avg": total_xga / matches_played if matches_played else 0
        }
        
    return stats
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && set PYTHONPATH=. && pytest tests/ingestion/test_understat.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/ingestion/scrapers/understat.py backend/tests/ingestion/test_understat.py
git commit -m "feat(ingestion): add Understat scraper for real xG data extraction"
```

### Task 3: Integrate Real Data into Dashboard Inference

**Files:**
- Modify: `backend/src/main.py`
- Modify: `backend/src/ingestion/tasks.py`

- [ ] **Step 1: Update API Dashboard Endpoint**

Modify `backend/src/main.py` to use real `fetch_current_xg_stats` and `TeamNormalizer`:
```python
# Insert imports at top of backend/src/main.py
from src.ingestion.scrapers.understat import fetch_current_xg_stats
from src.ingestion.normalizer import TeamNormalizer

# Inside get_dashboard_data() replace the dummy xG loop:
@app.get("/api/dashboard")
def get_dashboard_data():
    try:
        raw_odds = fetch_premier_league_odds(api_key="DEMO_KEY")
        
        # 1. Fetch real xG data
        xg_stats = fetch_current_xg_stats()
        
        # 2. Normalize and merge
        # Mocking a canonical list for V1 (ideally this comes from DB)
        canonical_teams = list(xg_stats.keys()) if xG_stats else ["Arsenal", "Chelsea", "Manchester City", "Manchester United", "Liverpool"]
        normalizer = TeamNormalizer(canonical_teams)
        
        for match in raw_odds:
            home_norm = normalizer.normalize(match.get("home_team", ""))
            away_norm = normalizer.normalize(match.get("away_team", ""))
            
            # Apply real xG if found, else fallback to 1.0
            match["home_xg"] = xg_stats.get(home_norm, {}).get("xg_for_avg", 1.0) if home_norm else 1.0
            match["away_xg"] = xg_stats.get(away_norm, {}).get("xg_for_avg", 1.0) if away_norm else 1.0

        predictions = predict_matches(raw_odds, model_dir="models")
        
        dashboard_data = []
        for idx, match in enumerate(raw_odds):
            pred = predictions[idx] if idx < len(predictions) else {}
            dashboard_data.append({
                "id": idx,
                "home_team": match.get("home_team"),
                "away_team": match.get("away_team"),
                "prob_home_win": pred.get("prob_home_win", 0.33),
                "prob_draw": pred.get("prob_draw", 0.33),
                "prob_away_win": pred.get("prob_away_win", 0.34),
            })
        return dashboard_data
    except Exception as e:
        return [{"error": str(e)}]
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/main.py
git commit -m "feat(api): integrate real Understat xG data and strict normalizer into inference pipeline"
```
````