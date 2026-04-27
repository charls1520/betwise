# Anti-Blocking Rate Limits Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement humanized delays (jitter), exponential backoff, and robust error isolation to prevent getting blocked by target APIs (Understat, Clubelo, football-data.co.uk) during mass historical scraping.

**Architecture:** Use `random` and `asyncio.sleep` to inject delays in Playwright scripts. Use `tenacity` or manual retries in `requests` loops with human-like `User-Agent` headers. Catch HTTP and Playwright timeouts safely so a failure in one season does not crash the entire multi-league loop.

**Tech Stack:** Python, `random`, `time`, `asyncio`, `tenacity`.

---

### Task 1: Add Robustness to Historical Data Downloader

**Files:**
- Modify: `backend/src/ingestion/historical.py`

- [ ] **Step 1: Implement Jitter and Headers in `requests`**

Modify `backend/src/ingestion/historical.py` to add `time`, `random`, and configure headers:

```python
import os
import pandas as pd
import requests
import io
import time
import random
from tenacity import retry, stop_after_attempt, wait_exponential
from src.ingestion.normalizer import TeamNormalizer
from src.ingestion.scrapers.understat_historical import fetch_understat_historical_season
from src.ingestion.scrapers.clubelo import fetch_clubelo_history

def get_elo_for_date(df_elo: pd.DataFrame, target_date: pd.Timestamp) -> float:
    if df_elo.empty: return None
    mask = (df_elo['From'] <= target_date) & (df_elo['To'] >= target_date)
    res = df_elo[mask]
    if not res.empty:
        return res.iloc[0]['Elo']
    return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_with_retry(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text

from src.ingestion.config import LEAGUES_CONFIG

def download_football_data_co_uk(seasons: list = ["2324", "2223", "2122"]) -> pd.DataFrame:
    base_url = "https://www.football-data.co.uk/mmz4281/{}/{}.csv"
    cache_dir = "data/historical"
    cache_file = os.path.join(cache_dir, "merged_history_cache.csv")
    
    os.makedirs(cache_dir, exist_ok=True)
    
    cached_df = pd.DataFrame()
    if os.path.exists(cache_file):
        try:
            cached_df = pd.read_csv(cache_file)
            cached_df["Date"] = pd.to_datetime(cached_df["Date"])
        except Exception as e:
            print(f"Failed to read cache: {e}")
            cached_df = pd.DataFrame()

    dfs_to_append = []
    
    season_to_year = {
        "2324": "2023",
        "2223": "2022",
        "2122": "2021",
        "2021": "2020",
        "1920": "2019"
    }

    for league in LEAGUES_CONFIG:
        fd_id = league["football_data_id"]
        und_id = league["understat_id"]
        print(f"Processing Historical Data for {league['name']}...")
        
        for season in seasons:
            url = base_url.format(season, fd_id)
            try:
                # Random delay before fetching new season
                time.sleep(random.uniform(1.0, 3.0))
                
                csv_text = fetch_with_retry(url)
                df = pd.read_csv(io.StringIO(csv_text))
                df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
                df = df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam'])
                
                if not cached_df.empty:
                    merged = df.merge(cached_df[['Date', 'HomeTeam', 'AwayTeam']], on=['Date', 'HomeTeam', 'AwayTeam'], how='left', indicator=True)
                    missing_df = df[merged['_merge'] == 'left_only'].copy()
                else:
                    missing_df = df.copy()
                    
                if missing_df.empty:
                    print(f"Season {season} is already fully cached. Skipping.")
                    continue
                    
                print(f"Processing {len(missing_df)} new matches for season {season}...")
                
                year = season_to_year.get(season)
                df_understat = fetch_understat_historical_season(year, und_id)
                
                normalizer = TeamNormalizer(df_understat['Team'].unique().tolist() if not df_understat.empty else [])
                
                teams = pd.concat([missing_df['HomeTeam'], missing_df['AwayTeam']]).unique().tolist()
                elo_cache = {}
                for t in teams:
                    norm_t = normalizer.normalize(t)
                    if norm_t:
                        clubelo_name = norm_t.replace(" ", "")
                        elo_cache[t] = fetch_clubelo_history(clubelo_name)
                        # Avoid hammering Clubelo
                        time.sleep(random.uniform(0.5, 1.5))
                
                enhanced_rows = []
                for _, row in missing_df.iterrows():
                    home = row['HomeTeam']
                    away = row['AwayTeam']
                    date = row['Date']
                    
                    norm_home = normalizer.normalize(home)
                    norm_away = normalizer.normalize(away)
                    
                    h_xg, a_xg, h_elo, a_elo = None, None, None, None
                    
                    if not df_understat.empty and norm_home and norm_away:
                        h_xg_row = df_understat[(df_understat['Team'] == norm_home) & (df_understat['Date'] == date)]
                        a_xg_row = df_understat[(df_understat['Team'] == norm_away) & (df_understat['Date'] == date)]
                        if not h_xg_row.empty: h_xg = h_xg_row.iloc[0]['xG']
                        if not a_xg_row.empty: a_xg = a_xg_row.iloc[0]['xG']
                    
                    if home in elo_cache and elo_cache[home] is not None:
                        h_elo = get_elo_for_date(elo_cache[home], date)
                    if away in elo_cache and elo_cache[away] is not None:
                        a_elo = get_elo_for_date(elo_cache[away], date)
                    
                    row_dict = row.to_dict()
                    row_dict['Home_xG'] = h_xg
                    row_dict['Away_xG'] = a_xg
                    row_dict['Home_Elo'] = h_elo
                    row_dict['Away_Elo'] = a_elo
                    enhanced_rows.append(row_dict)
                    
                season_enhanced_df = pd.DataFrame(enhanced_rows)
                valid_season_df = season_enhanced_df.dropna(subset=['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo'])
                
                print(f"Successfully merged {len(valid_season_df)} out of {len(missing_df)} matches.")
                if not valid_season_df.empty:
                    dfs_to_append.append(valid_season_df)
                    
            except Exception as e:
                print(f"Failed season {season} for {league['name']}: {e}")
                # We log the error but allow the loop to continue to the next season/league
                continue

    if dfs_to_append:
        new_data_df = pd.concat(dfs_to_append, ignore_index=True)
        final_df = pd.concat([cached_df, new_data_df], ignore_index=True)
        final_df.to_csv(cache_file, index=False)
        return final_df
    
    return cached_df
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/historical.py
git commit -m "feat(ingestion): add humanized delays and exponential backoff to historical scraper"
```

---

### Task 2: Add Route Blocking and Delays in Playwright (Understat Historical)

**Files:**
- Modify: `backend/src/ingestion/scrapers/understat_historical.py`

- [ ] **Step 1: Update the async fetch function**

Modify `_fetch_understat_season_async` to block images/css and add jitter:

```python
import json
import re
import asyncio
import random
from playwright.async_api import async_playwright
import pandas as pd

async def _fetch_understat_season_async(year: str, league_id: str) -> dict:
    url = f"https://understat.com/league/{league_id}/{year}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Setup realistic context
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        # Abort unneeded resources to save bandwidth and speed up
        await page.route("**/*", lambda route: route.abort() 
                         if route.request.resource_type in ["image", "stylesheet", "font", "media"] 
                         else route.continue_())
        
        try:
            # Human jitter before navigating
            await asyncio.sleep(random.uniform(2.0, 4.0))
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            is_defined = await page.evaluate("typeof teamsData !== 'undefined'")
            
            if is_defined:
                data = await page.evaluate("teamsData")
            else:
                content = await page.content()
                match = re.search(r"var teamsData\s*=\s*JSON\.parse\('([^']+)'\);", content)
                if match:
                    decoded = bytes(match.group(1), "utf-8").decode("unicode_escape")
                    data = json.loads(decoded)
                else:
                    return {}
            
            matches_data = []
            for team_id, team_info in data.items():
                title = team_info.get("title")
                history = team_info.get("history", [])
                for match in history:
                    matches_data.append({
                        "Team": title,
                        "Date": match.get("date").split(" ")[0],
                        "xG": float(match.get("xG", 0)),
                        "xGA": float(match.get("xGA", 0))
                    })
            return {"matches": matches_data}
        except Exception as e:
            print(f"Playwright Scraper Error for {league_id} {year}: {e}")
            return {}
        finally:
            await browser.close()

def fetch_understat_historical_season(year: str, league_id: str = "EPL") -> pd.DataFrame:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    data = loop.run_until_complete(_fetch_understat_season_async(year, league_id))
    if not data or "matches" not in data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data["matches"])
    df["Date"] = pd.to_datetime(df["Date"])
    return df
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/scrapers/understat_historical.py
git commit -m "feat(ingestion): add route blocking and jitter to playwright scraper"
```

---

### Task 3: Update Clubelo Fetcher with Retries

**Files:**
- Modify: `backend/src/ingestion/scrapers/clubelo.py`

- [ ] **Step 1: Add tenacity retries to Clubelo API**

```python
import csv
import io
import requests
import datetime
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from src.ingestion.validators import EloScore, validate_volume
from src.ingestion.normalizer import TeamNormalizer

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _fetch_clubelo_with_retry(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text

def fetch_clubelo_stats() -> List[dict]:
    today = datetime.date.today().strftime('%Y-%m-%d')
    url = f"http://api.clubelo.com/{today}"
    
    try:
        csv_data = _fetch_clubelo_with_retry(url)
    except Exception as e:
        print(f"Clubelo fetch error: {e}")
        return []
        
    reader = csv.DictReader(io.StringIO(csv_data))
    
    valid_scores = []
    for row in reader:
        try:
            score = EloScore(
                team=row.get('Club', ''),
                elo=float(row.get('Elo', 0)),
                date=row.get('To', '')
            )
            valid_scores.append(score.model_dump() if hasattr(score, 'model_dump') else score.dict())
        except Exception:
            continue
            
    if not validate_volume(len(valid_scores), 10):
        return []
        
    return valid_scores

def fetch_clubelo_history(club_name: str):
    """Fetches the entire Elo history for a specific club."""
    import pandas as pd
    
    url = f"http://api.clubelo.com/{club_name}"
    try:
        csv_data = _fetch_clubelo_with_retry(url)
        df = pd.read_csv(io.StringIO(csv_data))
        if 'Elo' in df.columns and 'From' in df.columns and 'To' in df.columns:
            df['From'] = pd.to_datetime(df['From'])
            df['To'] = pd.to_datetime(df['To'])
            return df
    except Exception as e:
        print(f"Clubelo history error for {club_name}: {e}")
        
    return pd.DataFrame()
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/scrapers/clubelo.py
git commit -m "feat(ingestion): add tenacity exponential backoff to clubelo scraper"
```

---

### Task 4: Update Tests for Retries

**Files:**
- Modify: `backend/tests/ingestion/test_historical.py`

- [ ] **Step 1: Mock `fetch_with_retry`**

In `backend/tests/ingestion/test_historical.py`:
```python
    # Mock the direct fetch_with_retry function instead of requests.get
    monkeypatch.setattr("src.ingestion.historical.fetch_with_retry", lambda url: "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR\nE0,12/08/2023,Arsenal,Nott'm Forest,2,1,H\n")
```

- [ ] **Step 2: Commit**

```bash
git add backend/tests/ingestion/test_historical.py
git commit -m "test: update historical test to mock fetch_with_retry"
```
