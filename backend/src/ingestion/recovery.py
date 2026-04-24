import requests
import csv
import io
import json
import re
from scrapling import Fetcher
from src.utils.logger import get_logger

logger = get_logger()

def fetch_xg_live(team_name: str) -> dict:
    """Attempts to fetch current xG for a team using Scrapling (without Playwright)."""
    # Using scrapling to search for the team or scrape from main pages if needed.
    # In a fully robust system, we would map the team name to a specific Understat ID.
    # Since we can't reliably map unknown team names to Understat URLs without a mapping table,
    # we log the attempt and return an empty dict to trigger the league average fallback,
    # or implement a search if possible. For now, we return empty so fallback handles it smoothly.
    
    logger.info(f"Live xG recovery attempted for {team_name}, but requires URL mapping. Falling back to averages.")
    return {}

def fetch_elo_live(team_name: str) -> float:
    """Attempts to fetch current Elo for a team using Clubelo API."""
    try:
        # Clubelo API allows fetching by name. We format the name: remove spaces, etc.
        formatted_name = team_name.replace(" ", "")
        url = f"http://api.clubelo.com/{formatted_name}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200 and "Elo" in response.text:
            reader = csv.DictReader(io.StringIO(response.text))
            for row in reader:
                # Assuming the last row or the row returned contains the Elo
                return float(row.get('Elo', 1500.0))
        return None
    except Exception as e:
        logger.error(f"Failed to fetch live Elo for {team_name}: {e}")
        return None