import pytest
from src.ingestion.scrapers.news_scraper import fetch_bbc_sports_news


def test_fetch_bbc_sports_news():
    # Test grabbing the RSS feed (we'll just check if it returns a list of dicts)
    articles = fetch_bbc_sports_news(limit=2)
    assert len(articles) <= 2
    if len(articles) > 0:
        assert "title" in articles[0]
        assert "link" in articles[0]
