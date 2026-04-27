# Historical xG and Elo Training Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the machine learning training pipeline to download, merge, and utilize historical xG (Understat) and Elo (Clubelo) data instead of relying solely on shots/corners.

**Architecture:** Create new historical scrapers for Understat and Clubelo. Modify `src/ingestion/historical.py` to merge these new sources with the base `football-data.co.uk` CSVs using dates and the existing `TeamNormalizer`. Update the ML feature engineering to train on the new `xg_diff` and `elo_diff` features.

**Tech Stack:** Python, Pandas, Scrapling, Requests, Scikit-Learn.

---

### Task 1: Historical Clubelo Scraper

**Files:**
- Modify: `backend/src/ingestion/scrapers/clubelo.py`

- [ ] **Step 1: Add function to fetch full club history**

Modify `backend/src/ingestion/scrapers/clubelo.py` to add a new function that downloads the full CSV history for a specific club.

```python
def fetch_clubelo_history(club_name: str) -> pd.DataFrame:
    """Fetches the entire Elo history for a specific club."""
    import pandas as pd
    import requests
    import io
    
    url = f"http://api.clubelo.com/{club_name}"
    response = requests.get(url)
    if response.status_code != 200:
        return pd.DataFrame()
        
    df = pd.read_csv(io.StringIO(response.text))
    if 'Elo' in df.columns and 'From' in df.columns and 'To' in df.columns:
        df['From'] = pd.to_datetime(df['From'])
        df['To'] = pd.to_datetime(df['To'])
        return df
    return pd.DataFrame()
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/scrapers/clubelo.py
git commit -m "feat: add historical clubelo scraper"
```

---

### Task 3: Historical Understat Scraper

**Files:**
- Create: `backend/src/ingestion/scrapers/understat_historical.py`

- [ ] **Step 1: Create historical scraper for Understat**

Create `backend/src/ingestion/scrapers/understat_historical.py`:

```python
import json
import re
import asyncio
from playwright.async_api import async_playwright
import pandas as pd

async def _fetch_understat_season_async(year: str) -> dict:
    url = f"https://understat.com/league/EPL/{year}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=15000)
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
        finally:
            await browser.close()

def fetch_understat_historical_season(year: str) -> pd.DataFrame:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    data = loop.run_until_complete(_fetch_understat_season_async(year))
    if not data or "matches" not in data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data["matches"])
    df["Date"] = pd.to_datetime(df["Date"])
    return df
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/scrapers/understat_historical.py
git commit -m "feat: add historical understat scraper"
```

---

### Task 4: Merge Historical Data

**Files:**
- Modify: `backend/src/ingestion/historical.py`

- [ ] **Step 1: Rewrite historical ingestion to merge sources**

Replace the contents of `backend/src/ingestion/historical.py` with a script that downloads football-data, understat, and clubelo, and merges them:

```python
import pandas as pd
import requests
import io
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

def download_football_data_co_uk(seasons: list = ["2324", "2223", "2122"]) -> pd.DataFrame:
    base_url = "https://www.football-data.co.uk/mmz4281/{}/E0.csv"
    dfs = []
    
    # Map football-data seasons to understat years (e.g. "2324" -> "2023")
    season_to_year = {
        "2324": "2023",
        "2223": "2022",
        "2122": "2021"
    }

    for season in seasons:
        url = base_url.format(season)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            df = pd.read_csv(io.StringIO(response.text))
            
            df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
            
            # Fetch Understat
            year = season_to_year.get(season)
            df_understat = fetch_understat_historical_season(year)
            
            normalizer = TeamNormalizer(df_understat['Team'].unique().tolist() if not df_understat.empty else [])
            
            # Prepare Elo cache
            teams = df['HomeTeam'].unique().tolist()
            elo_cache = {}
            for t in teams:
                norm_t = normalizer.normalize(t)
                if norm_t:
                    clubelo_name = norm_t.replace(" ", "")
                    elo_cache[t] = fetch_clubelo_history(clubelo_name)
            
            # Iterate and enrich
            enhanced_rows = []
            for _, row in df.iterrows():
                home = row['HomeTeam']
                away = row['AwayTeam']
                date = row['Date']
                
                norm_home = normalizer.normalize(home)
                norm_away = normalizer.normalize(away)
                
                # Default values
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
                
            dfs.append(pd.DataFrame(enhanced_rows))
        except Exception as e:
            print(f"Failed to download season {season}: {e}")

    if dfs:
        final_df = pd.concat(dfs, ignore_index=True)
        return final_df.dropna(subset=['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo'])
    return pd.DataFrame()
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/historical.py
git commit -m "feat: merge historical xg and elo into historical ingestion"
```

---

### Task 5: Update ML Feature Engineering

**Files:**
- Modify: `backend/src/ml/features.py`

- [ ] **Step 1: Replace old features with xg_diff and elo_diff**

Modify `backend/src/ml/features.py` to use `Home_xG`, `Away_xG`, `Home_Elo`, and `Away_Elo`:

```python
import pandas as pd

def build_features_for_matches(matches: list) -> pd.DataFrame:
    df = pd.DataFrame(matches)
    if df.empty:
        return df

    # We now expect 'Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo' instead of shots/corners
    if all(col in df.columns for col in ['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo']):
        df["xg_diff"] = df["Home_xG"] - df["Away_xG"]
        df["elo_diff"] = df["Home_Elo"] - df["Away_Elo"]
    else:
        # Fallback for inference format
        if "home_xg" in df.columns and "away_xg" in df.columns:
            df["xg_diff"] = df["home_xg"] - df["away_xg"]
        if "home_elo" in df.columns and "away_elo" in df.columns:
            df["elo_diff"] = df["home_elo"] - df["away_elo"]

    # Target Variables
    if "FTR" in df.columns:
        df["target_1x2"] = df["FTR"].map({"H": 1, "D": 0, "A": 2})
    if "FTHG" in df.columns and "FTAG" in df.columns:
        df["target_over25"] = ((df["FTHG"] + df["FTAG"]) > 2.5).astype(int)

    return df
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ml/features.py
git commit -m "feat: use historical xg and elo features for training"
```

---

### Task 6: Update ML Train Script

**Files:**
- Modify: `backend/src/ml/train.py`

- [ ] **Step 1: Include `elo_diff` in training features**

Modify `backend/src/ml/train.py`:
In `train_and_save_models`, change `features = ["xg_diff"]` to:

```python
    features = ["xg_diff", "elo_diff"]
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ml/train.py
git commit -m "feat: include elo_diff in ml training features"
```
