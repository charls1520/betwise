import pytest
from src.ingestion.scrapers.understat import fetch_current_xg_stats


def test_fetch_current_xg_stats(monkeypatch):
    class MockResponse:
        @property
        def text(self):
            return '<html><body><script>var teamsData = {"1": {"title": "Arsenal", "history": [{"xG": 2.1, "xGA": 0.5}]}};</script></body></html>'

        def raise_for_status(self):
            pass

    monkeypatch.setattr("requests.get", lambda url: MockResponse())

    stats = fetch_current_xg_stats()
    assert "Arsenal" in stats
    assert stats["Arsenal"]["xg_for_avg"] == 2.1
