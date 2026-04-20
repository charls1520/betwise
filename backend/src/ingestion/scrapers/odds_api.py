import requests
import datetime
import zoneinfo
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_premier_league_odds(api_key: str = "DEMO_KEY") -> list:
    """Fetches upcoming Premier League odds, strictly filtered to the next 48 hours in UTC-5."""
    # We use soccer_epl for Premier League
    url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds/"
    params = {
        "apiKey": api_key,
        "regions": "uk",
        "markets": "h2h",
        "oddsFormat": "decimal",
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
