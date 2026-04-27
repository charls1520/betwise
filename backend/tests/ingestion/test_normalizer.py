import pytest
import os
import json
from src.ingestion.normalizer import TeamNormalizer
from src.rag.config import init_llama_index

def test_team_normalizer_exact_and_fuzzy(tmp_path, monkeypatch):
    monkeypatch.setenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
    init_llama_index()
    # Setup isolated cache
    cache_path = str(tmp_path / "team_aliases.json")
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._load_cache", lambda self: {})
    
    def mock_save(self):
        with open(cache_path, "w") as f:
            json.dump(self.aliases, f)
            
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._save_cache", mock_save)
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._ask_llm", lambda self, name: "Arsenal" if "arsen" in name.lower() else None)

    teams = ["Manchester United", "Arsenal", "Chelsea"]
    normalizer = TeamNormalizer(teams)

    # "Arsenel" (typo) is 86 match with Arsenal. It will trigger LLM, which will correctly say Arsenal.
    assert normalizer.normalize("Arsenel") == "Arsenal"
    
def test_team_normalizer_auto_healing(tmp_path, monkeypatch):
    monkeypatch.setenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
    init_llama_index()
    cache_path = str(tmp_path / "team_aliases.json")
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._load_cache", lambda self: {})
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._save_cache", lambda self: None)
    monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._ask_llm", lambda self, name: "Manchester United" if "man" in name.lower() else None)

    teams = ["Manchester United", "Arsenal", "Chelsea"]
    normalizer = TeamNormalizer(teams)

    # "Man Utd" scores around 86, so it will trigger the real LLM
    result = normalizer.normalize("Man Utd")
    assert result == "Manchester United"
    
    # Check that it got saved to memory
    assert "man utd" in normalizer.aliases
