import pytest
import pandas as pd
from src.utils.audit_data import audit_data_lake, audit_historical_cache

def test_audit_data_lake(tmp_path):
    # Setup dummy data lake
    lake_dir = tmp_path / "data" / "raw" / "2026-01-01"
    lake_dir.mkdir(parents=True)
    
    # 1 valid file
    (lake_dir / "odds_1.json").write_text('{"matches": [{"id": 1}]}')
    # 1 empty file
    (lake_dir / "odds_2.json").write_text('{"matches": []}')
    # 1 corrupt file
    (lake_dir / "odds_3.json").write_text('{corrupt')
    
    metrics = audit_data_lake(base_dir=str(tmp_path / "data" / "raw"))
    
    assert metrics["total_files"] == 3
    assert metrics["empty_matches"] == 1
    assert metrics["corrupt_files"] == 1
    assert "total_size_mb" in metrics

def test_audit_historical_cache(tmp_path):
    cache_file = tmp_path / "merged_history_cache.csv"
    
    df = pd.DataFrame({
        "Date": ["2026-01-01", "2026-01-01", "2026-01-02"],
        "HomeTeam": ["A", "A", "B"],
        "AwayTeam": ["B", "B", "C"],
        "Home_xG": [1.0, 1.0, None], # 1 missing, 1 duplicate row
        "Away_xG": [0.0, 0.0, 1.5],  # 2 zeros
        "Home_Elo": [1500, 1500, 0], # 1 zero elo
        "Away_Elo": [1400, 1400, 1600]
    })
    df.to_csv(cache_file, index=False)
    
    metrics = audit_historical_cache(str(cache_file))
    
    assert metrics["total_rows"] == 3
    assert metrics["duplicates"] == 1
    assert metrics["missing_xg"] == 1
    assert metrics["zero_xg"] == 2
    assert metrics["zero_elo"] == 1