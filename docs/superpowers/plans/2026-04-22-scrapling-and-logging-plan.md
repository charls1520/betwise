# Scrapling and Centralized Logging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Playwright with Scrapling for faster, more reliable scraping, and implement a robust logging system using `loguru` to track ingestion progress and errors.

**Architecture:** A central logger module configuring `loguru` for console and rotating file output. `understat_historical.py` rewritten to use `scrapling`'s `Fetcher`. Ingestion scripts updated to use the centralized logger instead of `print()`.

**Tech Stack:** Python, Scrapling, Loguru.

---

### Task 1: Update Dependencies and Dockerfile

**Files:**
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\requirements.txt`
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\Dockerfile.dev`

- [ ] **Step 1: Update requirements.txt**

Add `loguru` and update `scrapling` to include fetchers. Remove `playwright`.

```text
# Replace 'playwright' with 'loguru'
loguru
# Modify scrapling line
scrapling[fetchers]
```
Make sure `playwright` is removed.

- [ ] **Step 2: Update Dockerfile.dev**

Remove Playwright installation steps and add Scrapling browser install.

```dockerfile
# Replace lines 14-16 with:
RUN pip install --no-cache-dir -r requirements.txt && \
    scrapling install
```

- [ ] **Step 3: Commit**

```bash
git add backend/requirements.txt backend/Dockerfile.dev
git commit -m "chore: update dependencies for scrapling and loguru"
```

---

### Task 2: Implement Centralized Logger

**Files:**
- Create: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\utils\logger.py`

- [ ] **Step 1: Create logger module**

```python
import sys
import os
from loguru import logger

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Remove default logger to prevent duplicates
logger.remove()

# Add console sink
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Add rotating file sink
logger.add(
    "logs/ingestion.log",
    rotation="10 MB",
    retention="5 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

def get_logger():
    return logger
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/utils/logger.py
git commit -m "feat: implement centralized logger using loguru"
```

---

### Task 3: Rewrite Understat Scraper with Scrapling

**Files:**
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ingestion\scrapers\understat_historical.py`

- [ ] **Step 1: Replace Playwright with Scrapling**

Replace the entire content of `understat_historical.py` with the following:

```python
import json
import re
import random
import pandas as pd
from scrapling import Fetcher
from src.utils.logger import get_logger

logger = get_logger()

def fetch_understat_historical_season(year: str, league_id: str = "EPL") -> pd.DataFrame:
    url = f"https://understat.com/league/{league_id}/{year}"
    logger.info(f"Fetching Understat data for {league_id} {year}")
    
    try:
        # Use basic Fetcher, which is fast and lightweight
        fetcher = Fetcher(
            auto_match=False, # Disable auto_match to avoid downloading unnecessary resources
        )
        page = fetcher.get(url)
        
        # Scrapling returns the page object, we can get its HTML text
        content = page.text
        
        match = re.search(r"var teamsData\s*=\s*JSON\.parse\('([^']+)'\);", content)
        if match:
            decoded = bytes(match.group(1), "utf-8").decode("unicode_escape")
            data = json.loads(decoded)
        else:
            raise Exception("Could not find teamsData JSON in page content (Cloudflare Block or Empty Data)")
        
        matches_data = []
        for team_id, team_info in data.items():
            title = team_info.get("title")
            history = team_info.get("history", [])
            if not history:
                continue
            for match_data in history:
                h_team = match_data.get("h", {}).get("title", "")
                a_team = match_data.get("a", {}).get("title", "")
                matches_data.append({
                    "Team": title,
                    "HomeTeam_Und": h_team,
                    "AwayTeam_Und": a_team,
                    "Date": match_data.get("date").split(" ")[0],
                    "xG": float(match_data.get("xG", 0)),
                    "xGA": float(match_data.get("xGA", 0))
                })
        
        if not matches_data:
            raise Exception("Parsed data contains no matches")
            
        df = pd.DataFrame(matches_data)
        df["Date"] = pd.to_datetime(df["Date"])
        logger.info(f"Successfully fetched {len(df)} Understat records for {league_id} {year}")
        return df
        
    except Exception as e:
        logger.exception(f"Scrapling Error for {league_id} {year}: {e}")
        return pd.DataFrame()
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/scrapers/understat_historical.py
git commit -m "feat: migrate Understat scraper to scrapling"
```

---

### Task 4: Integrate Logger into Ingestion Scripts

**Files:**
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ingestion\historical.py`
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ingestion\normalizer.py`
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ingestion\scrapers\clubelo.py`

- [ ] **Step 1: Update historical.py**

Add `from src.utils.logger import get_logger` and `logger = get_logger()`.
Replace all `print(...)` statements with `logger.info(...)`, `logger.warning(...)`, or `logger.error(...)`. Ensure `logger.exception(...)` is used in `except Exception as e:` blocks instead of `print(...)`.

- [ ] **Step 2: Update normalizer.py**

Add `from src.utils.logger import get_logger` and `logger = get_logger()`.
Replace `print(...)` statements with `logger.warning(...)`, `logger.info(...)`, or `logger.error(...)`.

- [ ] **Step 3: Update clubelo.py**

Add `from src.utils.logger import get_logger` and `logger = get_logger()`.
Replace `print(...)` with `logger.error(...)`.

- [ ] **Step 4: Commit**

```bash
git add backend/src/ingestion/historical.py backend/src/ingestion/normalizer.py backend/src/ingestion/scrapers/clubelo.py
git commit -m "refactor: replace print statements with centralized logger in ingestion"
```
