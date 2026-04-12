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
