from src.ingestion.storage import save_raw_data
from src.ingestion.scrapers.news_scraper import fetch_bbc_sports_news
from src.ingestion.scrapers.odds_api import fetch_premier_league_odds


def run_daily_scraping(odds_api_key: str = "DEMO_KEY"):
    print("Fetching News...")
    news = fetch_bbc_sports_news()
    news_file = save_raw_data("news", {"articles": news})
    print(f"Saved news to {news_file}")

    print("Fetching Odds...")
    odds = fetch_premier_league_odds(api_key=odds_api_key)
    odds_file = save_raw_data("odds", {"matches": odds})
    print(f"Saved odds to {odds_file}")


if __name__ == "__main__":
    run_daily_scraping()
