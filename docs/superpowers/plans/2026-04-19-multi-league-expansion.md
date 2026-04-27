# Multi-League Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the ingestion pipeline and historical training to support the Top 5 European leagues, allowing the ML model to learn across different competitions.

**Architecture:** Create a `config.py` in the ingestion module mapping the league codes for The-Odds-API, Understat, Clubelo, and football-data.co.uk. Refactor scrapers to take the league config as a parameter and update `tasks.py` and `historical.py` to loop over all leagues.

**Tech Stack:** Python, Pandas, Asyncio, Scrapling.

---

### Task 1: Create League Configuration

**Files:**
- Create: `backend/src/ingestion/config.py`

- [ ] **Step 1: Define the league mappings**

Create `backend/src/ingestion/config.py` to store the mapping for the Top 5 European Leagues:

```python
LEAGUES_CONFIG = [
    {
        "name": "Premier League",
        "odds_api_id": "soccer_epl",
        "understat_id": "EPL",
        "clubelo_id": "eng",
        "football_data_id": "E0"
    },
    {
        "name": "La Liga",
        "odds_api_id": "soccer_spain_la_liga",
        "understat_id": "La_liga",
        "clubelo_id": "esp",
        "football_data_id": "SP1"
    },
    {
        "name": "Serie A",
        "odds_api_id": "soccer_italy_serie_a",
        "understat_id": "Serie_A",
        "clubelo_id": "ita",
        "football_data_id": "I1"
    },
    {
        "name": "Bundesliga",
        "odds_api_id": "soccer_germany_bundesliga",
        "understat_id": "Bundesliga",
        "clubelo_id": "ger",
        "football_data_id": "D1"
    },
    {
        "name": "Ligue 1",
        "odds_api_id": "soccer_france_ligue_one",
        "understat_id": "Ligue_1",
        "clubelo_id": "fra",
        "football_data_id": "F1"
    }
]
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/config.py
git commit -m "feat(ingestion): add top 5 european leagues configuration"
```

---

### Task 2: Refactor The-Odds-API Scraper

**Files:**
- Modify: `backend/src/ingestion/scrapers/odds_api.py`
- Modify: `backend/tests/ingestion/test_odds_api.py`

- [ ] **Step 1: Parameterize league ID in odds API**

Modify `backend/src/ingestion/scrapers/odds_api.py`:

```python
import requests
import datetime
import zoneinfo
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_premier_league_odds(api_key: str, sport_key: str = "soccer_epl") -> list:
    """Fetches upcoming odds, strictly filtered to the next 48 hours in UTC-5."""
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {
        "apiKey": api_key,
        "regions": "eu,uk", # Expanded regions for broader coverage
        "markets": "h2h",
        "oddsFormat": "decimal",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    raw_matches = response.json()
    
    tz = zoneinfo.ZoneInfo("America/Bogota")
    now_utc5 = datetime.datetime.now(tz)
    limit_utc5 = now_utc5 + datetime.timedelta(hours=48)
    
    filtered_matches = []
    for match in raw_matches:
        commence_time_str = match.get("commence_time")
        if not commence_time_str:
            continue
            
        try:
            commence_time_utc = datetime.datetime.fromisoformat(commence_time_str.replace('Z', '+00:00'))
            commence_time_utc5 = commence_time_utc.astimezone(tz)
            
            if now_utc5 <= commence_time_utc5 <= limit_utc5:
                # Add a metadata tag so we know the league later
                match['sport_key'] = sport_key
                filtered_matches.append(match)
        except ValueError:
            filtered_matches.append(match)
            
    return filtered_matches
```

- [ ] **Step 2: Update odds test**

Modify `backend/tests/ingestion/test_odds_api.py`:

Update the call to `fetch_premier_league_odds(api_key="dummy")` to not break, as the default signature still has `sport_key="soccer_epl"`. No major changes needed unless we want to test multiple leagues, but adding the parameter satisfies the requirement.

- [ ] **Step 3: Commit**

```bash
git add backend/src/ingestion/scrapers/odds_api.py
git commit -m "refactor(ingestion): parameterize odds api scraper for multiple leagues"
```

---

### Task 3: Refactor Understat and Clubelo Scrapers

**Files:**
- Modify: `backend/src/ingestion/scrapers/understat.py`
- Modify: `backend/src/ingestion/scrapers/clubelo.py`

- [ ] **Step 1: Parameterize Understat scraper**

Modify `backend/src/ingestion/scrapers/understat.py`:
Change `_fetch_understat_async` to take a `league_id` and rename `fetch_current_xg_stats`:

```python
import json
import re
import asyncio
import nest_asyncio
from playwright.async_api import async_playwright
from tenacity import retry, stop_after_attempt, wait_fixed

nest_asyncio.apply()

async def _fetch_understat_async(league_id: str) -> dict:
    url = f"https://understat.com/league/{league_id}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=15000)
            
            is_defined = await page.evaluate("typeof teamsData !== 'undefined'")
            if is_defined:
                data = await page.evaluate("teamsData")
                return data

            content = await page.content()
            match = re.search(r"var teamsData\s*=\s*JSON\.parse\('([^']+)'\);", content)
            if match:
                decoded = bytes(match.group(1), "utf-8").decode("unicode_escape")
                return json.loads(decoded)
            return {}
        except Exception as e:
            print(f"Playwright Scraper Error for {league_id}: {e}")
            raise e
        finally:
            await browser.close()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def fetch_current_xg_stats(league_id: str = "EPL") -> dict:
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    raw_data = loop.run_until_complete(_fetch_understat_async(league_id))
    
    if not raw_data:
        return {}

    parsed_stats = {}
    for team_id, team_info in raw_data.items():
        title = team_info.get("title")
        history = team_info.get("history", [])
        if not history:
            continue

        recent = history[-5:]
        avg_xg_for = sum(float(m.get("xG", 0)) for m in recent) / len(recent)
        avg_xg_against = sum(float(m.get("xGA", 0)) for m in recent) / len(recent)

        parsed_stats[title] = {
            "xg_for_avg": round(avg_xg_for, 2),
            "xg_against_avg": round(avg_xg_against, 2),
        }
    return parsed_stats
```

- [ ] **Step 2: Parameterize Clubelo scraper**

Modify `backend/src/ingestion/scrapers/clubelo.py` to fetch from specific country subsets instead of a single list if possible, or just download the specific endpoints per league. E.g., change `url = f"http://api.clubelo.com/{today}"` to not strictly depend on a single country, or just fetch the global endpoint which returns all teams worldwide and parse what we need. Since `http://api.clubelo.com/YYYY-MM-DD` returns all global teams, we don't actually need to change the clubelo scraper! It already fetches global data for a date.

However, let's just make sure it's intact. No changes needed to `clubelo.py`.

- [ ] **Step 3: Commit**

```bash
git add backend/src/ingestion/scrapers/understat.py
git commit -m "refactor(ingestion): parameterize understat scraper for multiple leagues"
```

---

### Task 4: Update Daily Ingestion Task

**Files:**
- Modify: `backend/src/ingestion/tasks.py`

- [ ] **Step 1: Iterate over leagues in tasks**

Update `backend/src/ingestion/tasks.py`:

```python
import os
from dotenv import load_dotenv
from src.ingestion.storage import save_raw_data
from src.ingestion.scrapers.news_scraper import fetch_bbc_sports_news
from src.ingestion.scrapers.odds_api import fetch_premier_league_odds
from src.ingestion.scrapers.understat import fetch_current_xg_stats
from src.ingestion.scrapers.clubelo import fetch_clubelo_stats
from src.ingestion.config import LEAGUES_CONFIG

load_dotenv()

def run_daily_scraping(odds_api_key: str = None):
    if odds_api_key is None:
        odds_api_key = os.environ.get("ODDS_API_KEY", "DEMO_KEY")
        
    print("Fetching News...")
    news = fetch_bbc_sports_news()
    news_file = save_raw_data("news", {"articles": news})
    print(f"Saved news to {news_file}")

    print("Fetching Global Clubelo...")
    elo_stats = fetch_clubelo_stats()
    elo_file = save_raw_data("elo", {"stats": elo_stats})
    print(f"Saved Clubelo to {elo_file}")

    all_odds = []
    all_xg = {}

    for league in LEAGUES_CONFIG:
        print(f"Fetching data for {league['name']}...")
        
        try:
            odds = fetch_premier_league_odds(api_key=odds_api_key, sport_key=league["odds_api_id"])
            all_odds.extend(odds)
        except Exception as e:
            print(f"Failed odds for {league['name']}: {e}")
            
        try:
            xg_stats = fetch_current_xg_stats(league_id=league["understat_id"])
            all_xg.update(xg_stats)
        except Exception as e:
            print(f"Failed xG for {league['name']}: {e}")

    odds_file = save_raw_data("odds", {"matches": all_odds})
    print(f"Saved multi-league odds to {odds_file}")

    xg_file = save_raw_data("xg", all_xg)
    print(f"Saved multi-league xG to {xg_file}")

if __name__ == "__main__":
    run_daily_scraping()
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/tasks.py
git commit -m "feat(ingestion): run daily tasks across top 5 leagues"
```

---

### Task 5: Refactor Historical Ingestion Loop

**Files:**
- Modify: `backend/src/ingestion/historical.py`
- Modify: `backend/src/ingestion/scrapers/understat_historical.py`

- [ ] **Step 1: Parameterize Understat Historical**

In `backend/src/ingestion/scrapers/understat_historical.py`, add `league_id`:
```python
async def _fetch_understat_season_async(year: str, league_id: str) -> dict:
    url = f"https://understat.com/league/{league_id}/{year}"
    # ... rest is same
```
And modify `fetch_understat_historical_season`:
```python
def fetch_understat_historical_season(year: str, league_id: str = "EPL") -> pd.DataFrame:
    # ...
    data = loop.run_until_complete(_fetch_understat_season_async(year, league_id))
    # ...
```

- [ ] **Step 2: Iterate leagues in historical**

In `backend/src/ingestion/historical.py`, change `download_football_data_co_uk` to download all leagues:

```python
from src.ingestion.config import LEAGUES_CONFIG

def download_football_data_co_uk(seasons: list = ["2324", "2223", "2122"]) -> pd.DataFrame:
    base_url = "https://www.football-data.co.uk/mmz4281/{}/{}.csv" # second param is league code
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
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    continue
                df = pd.read_csv(io.StringIO(response.text))
                df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
                df = df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam'])
                
                if not cached_df.empty:
                    merged = df.merge(cached_df[['Date', 'HomeTeam', 'AwayTeam']], on=['Date', 'HomeTeam', 'AwayTeam'], how='left', indicator=True)
                    missing_df = df[merged['_merge'] == 'left_only'].copy()
                else:
                    missing_df = df.copy()
                    
                if missing_df.empty:
                    continue
                    
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
                
                if not valid_season_df.empty:
                    dfs_to_append.append(valid_season_df)
                    
            except Exception as e:
                print(f"Failed season {season} for {league['name']}: {e}")

    if dfs_to_append:
        new_data_df = pd.concat(dfs_to_append, ignore_index=True)
        final_df = pd.concat([cached_df, new_data_df], ignore_index=True)
        final_df.to_csv(cache_file, index=False)
        return final_df
    
    return cached_df
```

- [ ] **Step 3: Update Test Mock**

In `backend/tests/ingestion/test_historical.py`, update the mock for `fetch_understat_historical_season` to accept the new parameter:
```python
        monkeypatch.setattr("src.ingestion.historical.fetch_understat_historical_season",
                            lambda year, league: pd.DataFrame([{"Team": "Arsenal", "Date": pd.to_datetime("2023-08-12"), "xG": 2.0, "xGA": 1.0},
                                                       {"Team": "Nottingham Forest", "Date": pd.to_datetime("2023-08-12"), "xG": 1.0, "xGA": 2.0}]))
```

- [ ] **Step 4: Commit**

```bash
git add backend/src/ingestion/scrapers/understat_historical.py backend/src/ingestion/historical.py backend/tests/ingestion/test_historical.py
git commit -m "feat(ingestion): extend historical processing to all top 5 leagues"
```

---

### Task 6: Final Inference Integration

**Files:**
- Modify: `backend/src/main.py`

- [ ] **Step 1: Ensure main.py loads new variables gracefully**

In `backend/src/main.py`, since `fetch_current_xg_stats` and `fetch_premier_league_odds` are now looped in the cron job, `get_latest_ml_suggestions()` and `/api/dashboard` already read the merged raw files which now contain all leagues. The ML model is also trained globally. So no changes needed for ML prediction!

- [ ] **Step 2: Commit**

If no changes are strictly needed, just run tests to verify.

```bash
docker exec betwise_backend pytest
```
````