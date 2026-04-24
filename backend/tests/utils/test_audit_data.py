import pytest
from src.utils.audit_data import audit_data_lake

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