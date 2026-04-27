# Temporal Filter (48h) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a strict 48-hour time filter (UTC-5) at the scraper level so only matches occurring today or tomorrow are ingested and predicted.

**Architecture:** Modify `odds_api.py` to parse `commence_time` using python's built-in `datetime` and `timezone` to filter out matches beyond 48 hours in the `America/Bogota` timezone.

**Tech Stack:** Python, `datetime`, `zoneinfo`.

---

### Task 1: Implement Time Filter in Odds Scraper

**Files:**
- Modify: `backend/src/ingestion/scrapers/odds_api.py`

- [ ] **Step 1: Write the filtering logic**

Update `backend/src/ingestion/scrapers/odds_api.py` to parse the ISO 8601 string and apply the timezone filter:

```python
import requests
from typing import List
import datetime
import zoneinfo

def fetch_premier_league_odds(api_key: str) -> List[dict]:
    """Fetches upcoming Premier League odds, strictly filtered to the next 48 hours in UTC-5."""
    url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds"
    params = {
        "apiKey": api_key,
        "regions": "uk,eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    raw_matches = response.json()
    
    # Timezone filtering logic
    tz = zoneinfo.ZoneInfo("America/Bogota")
    now_utc5 = datetime.datetime.now(tz)
    limit_utc5 = now_utc5 + datetime.timedelta(hours=48)
    
    filtered_matches = []
    for match in raw_matches:
        commence_time_str = match.get("commence_time")
        if not commence_time_str:
            continue
            
        # Parse UTC time from API (e.g., '2026-04-20T19:00:00Z')
        try:
            # Replace Z with +00:00 for fromisoformat
            commence_time_utc = datetime.datetime.fromisoformat(commence_time_str.replace('Z', '+00:00'))
            commence_time_utc5 = commence_time_utc.astimezone(tz)
            
            if now_utc5 <= commence_time_utc5 <= limit_utc5:
                filtered_matches.append(match)
        except ValueError:
            # If date format is weird, keep it just in case, but usually odds API is strict ISO
            filtered_matches.append(match)
            
    return filtered_matches
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/scrapers/odds_api.py
git commit -m "feat(ingestion): restrict odds scraper to strictly 48 hours (UTC-5) matches"
```

---

### Task 2: Update Tests for Temporal Filter

**Files:**
- Modify: `backend/tests/ingestion/test_odds_api.py`

- [ ] **Step 1: Mock the time filter in test**

Update `backend/tests/ingestion/test_odds_api.py` to ensure it passes with the new datetime logic:

```python
import pytest
import datetime
import zoneinfo
from src.ingestion.scrapers.odds_api import fetch_premier_league_odds

def test_fetch_premier_league_odds(monkeypatch):
    # We mock requests.get to not hit the real API in tests
    class MockResponse:
        status_code = 200

        def json(self):
            # Return one match inside 48h and one outside
            tz = zoneinfo.ZoneInfo("America/Bogota")
            now = datetime.datetime.now(tz)
            match_in_24h = (now + datetime.timedelta(hours=24)).astimezone(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
            match_in_72h = (now + datetime.timedelta(hours=72)).astimezone(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
            
            return [
                {
                    "home_team": "Arsenal",
                    "away_team": "Chelsea",
                    "commence_time": match_in_24h,
                    "bookmakers": []
                },
                {
                    "home_team": "Liverpool",
                    "away_team": "Everton",
                    "commence_time": match_in_72h,
                    "bookmakers": []
                }
            ]

        def raise_for_status(self):
            pass

    monkeypatch.setattr("requests.get", lambda url, params: MockResponse())

    odds = fetch_premier_league_odds(api_key="dummy")
    # Should only return the Arsenal match (inside 48h window)
    assert len(odds) == 1
    assert odds[0]["home_team"] == "Arsenal"
```

- [ ] **Step 2: Commit**

```bash
git add backend/tests/ingestion/test_odds_api.py
git commit -m "test: update odds scraper test to mock 48h time window"
```
