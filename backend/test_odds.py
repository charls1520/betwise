import os
import datetime
import zoneinfo
import requests
from dotenv import load_dotenv
from src.ingestion.config import LEAGUES_CONFIG

load_dotenv(".env")
api_key = os.environ.get("ODDS_API_KEY")

tz = zoneinfo.ZoneInfo("America/Bogota")
now_utc5 = datetime.datetime.now(tz)
limit_utc5 = now_utc5 + datetime.timedelta(hours=48)

print(f"Now UTC-5: {now_utc5}")
print(f"Limit UTC-5: {limit_utc5}")

for league in LEAGUES_CONFIG:
    sport_key = league["odds_api_id"]
    print(f"\n--- Checking {sport_key} ---")
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
    params = {
        "apiKey": api_key,
        "regions": "eu,uk",
        "markets": "h2h",
        "oddsFormat": "decimal",
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        raw_matches = response.json()
        print(f"API returned {len(raw_matches)} raw matches")
        
        for match in raw_matches:
            commence_time_str = match.get("commence_time")
            try:
                commence_time_utc = datetime.datetime.fromisoformat(commence_time_str.replace('Z', '+00:00'))
                commence_time_utc5 = commence_time_utc.astimezone(tz)
                
                status = "REJECTED (Too far)"
                if commence_time_utc5 < now_utc5:
                    status = "REJECTED (Past)"
                elif now_utc5 <= commence_time_utc5 <= limit_utc5:
                    status = "ACCEPTED"
                elif commence_time_utc5 > limit_utc5:
                    status = "REJECTED (Future >48h)"
                    
                print(f"Match: {match['home_team']} vs {match['away_team']} | Time UTC: {commence_time_utc} | Time UTC-5: {commence_time_utc5} | Status: {status}")
            except Exception as e:
                print(f"Error parsing time: {e}")
    except Exception as e:
        print(f"Failed to fetch: {e}")