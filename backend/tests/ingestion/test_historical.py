import pytest
from src.ingestion.historical import download_football_data_co_uk


def test_download_football_data_co_uk(monkeypatch):
    class MockResponse:
        @property
        def text(self):
            return "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR\nE0,12/08/2023,Arsenal,Nott'm Forest,2,1,H\n"

        def raise_for_status(self):
            pass

    monkeypatch.setattr("requests.get", lambda url, timeout: MockResponse())

    df = download_football_data_co_uk(seasons=["2324"])
    assert not df.empty
    assert "HomeTeam" in df.columns
    assert df.iloc[0]["HomeTeam"] == "Arsenal"
