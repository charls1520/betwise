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