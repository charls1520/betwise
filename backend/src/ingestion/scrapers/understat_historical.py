import requests
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger()

def fetch_understat_historical_season(year: str, league_id: str = "EPL") -> pd.DataFrame:
    url = f"https://understat.com/main/getLeagueData/{league_id}/{year}"
    logger.info(f"Fetching Understat API data for {league_id} {year}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        matches_data = []
        for team_id, team_info in data.get("teams", {}).items():
            title = team_info.get("title")
            history = team_info.get("history", [])
            for match_data in history:
                matches_data.append({
                    "Team": title,
                    "h_a": match_data.get("h_a"),
                    "Date": match_data.get("date", "").split(" ")[0],
                    "xG": float(match_data.get("xG", 0)),
                    "xGA": float(match_data.get("xGA", 0))
                })
        
        if not matches_data:
            logger.warning(f"No match data found in API response for {league_id} {year}")
            return pd.DataFrame()
            
        df = pd.DataFrame(matches_data)
        df["Date"] = pd.to_datetime(df["Date"])
        logger.info(f"Successfully fetched {len(df)} Understat records for {league_id} {year}")
        return df
        
    except Exception as e:
        logger.exception(f"Understat API Error for {league_id} {year}: {e}")
        return pd.DataFrame()
