import os
from dotenv import load_dotenv
from src.ingestion.storage import save_raw_data
from src.ingestion.scrapers.news_scraper import fetch_bbc_sports_news
from src.ingestion.scrapers.odds_api import fetch_premier_league_odds
from src.ingestion.scrapers.understat import fetch_current_xg_stats
from src.ingestion.scrapers.clubelo import fetch_clubelo_stats
from src.ingestion.config import LEAGUES_CONFIG
from src.utils.logger import get_logger
from src.ingestion.validators import NewsArticle, validate_volume
from src.ingestion.state import get_last_run, update_last_run
from datetime import datetime

load_dotenv()
logger = get_logger()

def run_daily_scraping(odds_api_key: str = None):
    if odds_api_key is None:
        odds_api_key = os.environ.get("ODDS_API_KEY")
        if not odds_api_key or odds_api_key == "DEMO_KEY":
            raise ValueError("ODDS_API_KEY is not set in environment variables")
        
    logger.info("Fetching News...")
    news = fetch_bbc_sports_news()
    
    valid_news = []
    for article in news:
        try:
            valid_article = NewsArticle(**article)
            valid_news.append(valid_article.dict())
        except Exception as e:
            logger.warning(f"Dropping invalid news article: {e}")
            
    if validate_volume(len(valid_news), expected_minimum=1):
        news_file = save_raw_data("news", {"articles": valid_news})
        logger.info(f"Saved news to {news_file}")
    else:
        logger.error("News validation failed - volume too low. Not saving.")

    logger.info("Fetching Global Clubelo...")
    elo_stats = fetch_clubelo_stats()
    
    valid_elo = {}
    for stat in elo_stats:
        team = stat.get("team")
        elo = stat.get("elo")
        if isinstance(elo, (int, float)) and 500.0 < elo < 2500.0:
            valid_elo[team] = float(elo)
        else:
            logger.warning(f"Dropping invalid elo for {team}: {elo}")

    if validate_volume(len(valid_elo), expected_minimum=10):
        elo_file = save_raw_data("elo", {"stats": valid_elo})
        logger.info(f"Saved Clubelo to {elo_file}")
    else:
        logger.error("Clubelo validation failed - volume too low. Not saving.")

    all_odds = []
    all_xg = {}

    last_odds_run = get_last_run("odds_api")
    last_xg_run = get_last_run("understat")

    for league in LEAGUES_CONFIG:
        logger.info(f"Fetching data for {league['name']}...")
        
        try:
            odds = fetch_premier_league_odds(api_key=odds_api_key, sport_key=league["odds_api_id"])
            if last_odds_run:
                odds = [o for o in odds if o.get("commence_time", "") > last_odds_run]

            if validate_volume(len(odds), expected_minimum=1):
                all_odds.extend(odds)
            else:
                logger.info(f"No new odds or volume too low for {league['name']}.")
        except Exception as e:
            logger.error(f"Failed odds for {league['name']}: {e}")
            
        try:
            xg_stats = fetch_current_xg_stats(league_id=league["understat_id"])
            if validate_volume(len(xg_stats), expected_minimum=1):
                all_xg.update(xg_stats)
            else:
                logger.error(f"xG volume validation failed for {league['name']}.")
        except Exception as e:
            logger.error(f"Failed xG for {league['name']}: {e}")

    if len(all_odds) > 0:
        update_last_run("odds_api")
        odds_file = save_raw_data("odds", {"matches": all_odds})
        logger.info(f"Saved multi-league odds to {odds_file}")
        
    if len(all_xg) > 0:
        update_last_run("understat")
        xg_file = save_raw_data("xg", all_xg)
        logger.info(f"Saved multi-league xG to {xg_file}")

if __name__ == "__main__":
    run_daily_scraping()
