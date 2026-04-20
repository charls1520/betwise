import pytest
import datetime
import zoneinfo
from src.ingestion.scrapers.odds_api import fetch_premier_league_odds


def test_fetch_premier_league_odds(monkeypatch):
    # We mock requests.get to not hit the real API in tests
    class MockResponse:
        def json(self):
            # Return one match inside 48h and one outside
            tz = zoneinfo.ZoneInfo("America/Bogota")
            now = datetime.datetime.now(tz)
            match_in_24h = (now + datetime.timedelta(hours=24)).astimezone(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
            match_in_72h = (now + datetime.timedelta(hours=72)).astimezone(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
            
            return [
                {
                    "home_team": "Arsenal",
                    "away_team": "Chelsea",
                    "commence_time": match_in_24h,
                    "bookmakers": []
                },
                {
                    "home_team": "Liverpool",
                    "away_team": "Everton",
                    "commence_time": match_in_72h,
                    "bookmakers": []
                }
            ]

        def raise_for_status(self):
            pass

    monkeypatch.setattr("requests.get", lambda url, params: MockResponse())

    odds = fetch_premier_league_odds(api_key="dummy")
    # Should only return the Arsenal match (inside 48h window)
    assert len(odds) == 1
    assert odds[0]["home_team"] == "Arsenal"
