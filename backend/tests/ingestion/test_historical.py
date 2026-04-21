import pytest
import os
import pandas as pd
from src.ingestion.historical import download_football_data_co_uk


def test_download_football_data_co_uk(monkeypatch, tmp_path):
    # Mock the direct fetch_with_retry function instead of requests.get
    monkeypatch.setattr("src.ingestion.historical.fetch_with_retry", lambda url: "Div,Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR\nE0,12/08/2023,Arsenal,Nott'm Forest,2,1,H\n")
    
    # Mock the new dependent functions
    monkeypatch.setattr("src.ingestion.historical.fetch_understat_historical_season",
                        lambda year, league: pd.DataFrame([{"Team": "Arsenal", "Date": pd.to_datetime("2023-08-12"), "xG": 2.0, "xGA": 1.0},
                                                       {"Team": "Nottingham Forest", "Date": pd.to_datetime("2023-08-12"), "xG": 1.0, "xGA": 2.0}]))
    monkeypatch.setattr("src.ingestion.historical.fetch_clubelo_history", 
                        lambda club: pd.DataFrame([{"From": pd.to_datetime("2023-08-01"), "To": pd.to_datetime("2023-08-31"), "Elo": 1800}]))

    # Override the hardcoded cache dir with pytest's tmp_path using a monkeypatch wrapper
    original_makedirs = os.makedirs
    
    def mock_makedirs(name, exist_ok=False):
        if "data/historical" in str(name).replace("\\", "/"):
            original_makedirs(str(tmp_path), exist_ok=True)
        else:
            original_makedirs(name, exist_ok=exist_ok)
            
    monkeypatch.setattr("os.makedirs", mock_makedirs)
    original_join = os.path.join
    def safe_join(*args):
        if args and str(args[0]) in ("data", "data/historical"):
            return original_join(str(tmp_path), *args[1:])
        return original_join(*args)
    monkeypatch.setattr("os.path.join", safe_join)
    monkeypatch.setenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
    
    from src.rag.config import init_llama_index
    init_llama_index()

    df = download_football_data_co_uk(seasons=["2324"])
    assert not df.empty
    assert "HomeTeam" in df.columns
    assert df.iloc[0]["HomeTeam"] == "Arsenal"
