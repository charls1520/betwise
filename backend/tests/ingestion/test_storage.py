import os
import json
from src.ingestion.storage import save_raw_data


def test_save_raw_data(tmp_path):
    data = {"test": "data", "teams": ["Arsenal", "Chelsea"]}
    filepath = save_raw_data("stats", data, base_dir=str(tmp_path))

    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        loaded = json.load(f)
        assert loaded["test"] == "data"

from src.ingestion.scrapers.clubelo import fetch_clubelo_bulk_history

def test_fetch_clubelo_bulk_history():
    # Use a well-known past date to avoid breaking the test if the API is down on "today"
    df = fetch_clubelo_bulk_history("2023-08-01")
    assert df is not None
    if not df.empty:
        assert 'Elo' in df.columns
        assert 'Club' in df.columns
