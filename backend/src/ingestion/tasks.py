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
