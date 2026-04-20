import pytest
import os
import json
from src.ingestion.normalizer import TeamNormalizer

def test_team_normalizer_exact_and_fuzzy(tmp_path, monkeypatch):
    # Setup isolated cache
    cache_path = str(tmp_path / "team_aliases.json")
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._load_cache", lambda self: {})
    
    def mock_save(self):
        with open(cache_path, "w") as f:
            json.dump(self.aliases, f)
            
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._save_cache", mock_save)
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._ask_llm", lambda self, name: None)

    teams = ["Manchester United", "Arsenal", "Chelsea"]
    normalizer = TeamNormalizer(teams)

    # "Arsenel" (typo) is 92 match with Arsenal. Since we mocked LLM to None, it should return None
    assert normalizer.normalize("Arsenel") is None
    
def test_team_normalizer_auto_healing(tmp_path, monkeypatch):
    cache_path = str(tmp_path / "team_aliases.json")
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._load_cache", lambda self: {})
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._save_cache", lambda self: None)

    # Mock the LLM call to return "Manchester United" for "Man Utd"
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._ask_llm", lambda self, name: "Manchester United" if "man" in name.lower() else None)

    teams = ["Manchester United", "Arsenal", "Chelsea"]
    normalizer = TeamNormalizer(teams)

    # "Man Utd" scores around 86, so it will trigger the LLM mock
    result = normalizer.normalize("Man Utd")
    assert result == "Manchester United"
    
    # Check that it got saved to memory
    assert "man utd" in normalizer.aliases
