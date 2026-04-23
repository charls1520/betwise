import pytest
import os
from src.ingestion.tasks import run_daily_scraping

def test_run_daily_scraping_requires_api_key(monkeypatch):
    # Ensure ODDS_API_KEY is not set
    monkeypatch.delenv("ODDS_API_KEY", raising=False)
    
    with pytest.raises(ValueError, match="ODDS_API_KEY is not set in environment variables"):
        run_daily_scraping()