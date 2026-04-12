import pytest
from src.ingestion.scrapers.odds_api import fetch_premier_league_odds


def test_fetch_premier_league_odds(monkeypatch):
    # We mock requests.get to not hit the real API in tests
    class MockResponse:
        def json(self):
            return [{"home_team": "Arsenal", "away_team": "Chelsea", "bookmakers": []}]

        def raise_for_status(self):
            pass

    monkeypatch.setattr("requests.get", lambda url, params: MockResponse())

    odds = fetch_premier_league_odds(api_key="dummy")
    assert len(odds) == 1
    assert odds[0]["home_team"] == "Arsenal"
