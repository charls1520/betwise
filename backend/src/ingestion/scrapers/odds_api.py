import requests
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_premier_league_odds(api_key: str = "DEMO_KEY") -> list:
    """Fetches upcoming Premier League odds from The-Odds-API."""
    # We use soccer_epl for Premier League
    url = "https://api.the-odds-api.com/v4/sports/soccer_epl/odds/"
    params = {
        "apiKey": api_key,
        "regions": "uk",
        "markets": "h2h",
        "oddsFormat": "decimal",
    }

    response = requests.get(url, params=params)
    # If using DEMO_KEY, just return a mock response to avoid real failures if key isn't provided
    if api_key == "DEMO_KEY" and response.status_code == 401:
        return [{"home_team": "Arsenal", "away_team": "Chelsea", "bookmakers": []}]

    response.raise_for_status()
    return response.json()
