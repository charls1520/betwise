import pytest
import pandas as pd
from src.ingestion.historical import download_football_data_co_uk


def test_download_football_data_co_uk(monkeypatch):
    class MockResponse:
        status_code = 200

        @property
        def text(self):
            return "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR\nE0,12/08/2023,Arsenal,Nott'm Forest,2,1,H\n"

        def raise_for_status(self):
            pass

    monkeypatch.setattr("requests.get", lambda url, timeout=None: MockResponse())
    
    # Mock the new dependent functions
    monkeypatch.setattr("src.ingestion.historical.fetch_understat_historical_season", 
                        lambda year: pd.DataFrame([{"Team": "Arsenal", "Date": pd.to_datetime("2023-08-12"), "xG": 2.0, "xGA": 1.0},
                                                   {"Team": "Nottingham Forest", "Date": pd.to_datetime("2023-08-12"), "xG": 1.0, "xGA": 2.0}]))
    monkeypatch.setattr("src.ingestion.historical.fetch_clubelo_history", 
                        lambda club: pd.DataFrame([{"From": pd.to_datetime("2023-08-01"), "To": pd.to_datetime("2023-08-31"), "Elo": 1800}]))

    df = download_football_data_co_uk(seasons=["2324"])
    assert not df.empty
    assert "HomeTeam" in df.columns
    assert df.iloc[0]["HomeTeam"] == "Arsenal"
