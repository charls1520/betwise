import pytest
import os
from unittest.mock import patch
from src.ingestion.tasks import run_daily_scraping

def test_run_daily_scraping_requires_api_key(monkeypatch):
    # Ensure ODDS_API_KEY is not set
    monkeypatch.delenv("ODDS_API_KEY", raising=False)
    
    with pytest.raises(ValueError, match="ODDS_API_KEY is not set in environment variables"):
        run_daily_scraping()

@patch("src.ingestion.tasks.TelegramNotifier")
@patch("src.ingestion.tasks.predict_matches")
@patch("src.ingestion.tasks.save_raw_data")
@patch("src.ingestion.tasks.fetch_current_xg_stats")
@patch("src.ingestion.tasks.fetch_premier_league_odds")
@patch("src.ingestion.tasks.fetch_clubelo_stats")
@patch("src.ingestion.tasks.fetch_bbc_sports_news")
@patch("src.ingestion.tasks.get_last_run")
@patch("src.ingestion.tasks.update_last_run")
def test_run_daily_scraping_with_telegram(
    mock_update_last_run,
    mock_get_last_run,
    mock_fetch_news,
    mock_fetch_elo,
    mock_fetch_odds,
    mock_fetch_xg,
    mock_save,
    mock_predict,
    mock_notifier
):
    mock_get_last_run.return_value = None
    mock_fetch_news.return_value = [{"title": "Long News Title Here", "url": "http://bbc.com/1", "published_date": "2026-04-20T10:00:00Z", "summary": "Long Summary Details Here"}]
    mock_fetch_elo.return_value = [{"team": "Arsenal", "elo": 1900}, {"team": "Chelsea", "elo": 1800}, {"team": "A", "elo": 1000}, {"team": "B", "elo": 1000}, {"team": "C", "elo": 1000}, {"team": "D", "elo": 1000}, {"team": "E", "elo": 1000}, {"team": "F", "elo": 1000}, {"team": "G", "elo": 1000}, {"team": "H", "elo": 1000}]
    mock_fetch_odds.return_value = [{"home_team": "Arsenal", "away_team": "Chelsea", "commence_time": "2026-04-26T15:00:00Z", "bookmakers": []}]
    mock_fetch_xg.return_value = {"Arsenal": {"xG": 2.0}, "Chelsea": {"xG": 1.5}}
    
    mock_predict.return_value = [
        {"home_team": "Arsenal", "away_team": "Chelsea", "value_edge": True, "prob_home_win": 0.6}
    ]
    
    mock_notifier_instance = mock_notifier.return_value
    
    run_daily_scraping(odds_api_key="test_key")
    
    mock_predict.assert_called_once()
    mock_notifier_instance.send_prediction.assert_called_once_with(
        {"home_team": "Arsenal", "away_team": "Chelsea", "value_edge": True, "prob_home_win": 0.6}
    )