# Auto-Healing Team Normalizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace hardcoded team aliases with an auto-healing normalizer that uses an LLM (Ollama) to resolve unmatched team names and caches the results in a JSON file.

**Architecture:** `TeamNormalizer` reads `data/team_aliases.json` on init. For normalization, it checks the cache, then does fuzzy matching. If fuzzy score is between 50 and 95, it prompts the LLM to identify the canonical team, saves the result to the cache, and returns it.

**Tech Stack:** Python, LlamaIndex, JSON.

---

### Task 1: Create Memory Cache and LLM Logic

**Files:**
- Modify: `backend/src/ingestion/normalizer.py`

- [ ] **Step 1: Rewrite TeamNormalizer**

Update `backend/src/ingestion/normalizer.py`:

```python
import os
import json
from thefuzz import process
from typing import List, Optional
from llama_index.core import Settings

class TeamNormalizer:
    def __init__(self, canonical_teams: List[str], threshold: int = 95):
        self.canonical_teams = canonical_teams
        self.threshold = threshold
        self.cache_file = "data/team_aliases.json"
        self.aliases = self._load_cache()

    def _load_cache(self) -> dict:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.aliases, f, indent=4)

    def _ask_llm(self, raw_name: str) -> Optional[str]:
        if not getattr(Settings, "llm", None):
            return None
            
        prompt = (
            f"The scraper found the team '{raw_name}'. "
            f"Which of these official Premier League teams does it refer to: {self.canonical_teams}? "
            f"You must reply EXCLUSIVAMENTE with the exact official team name from the list, with no punctuation or extra text. "
            f"If it is none of them, reply 'NONE'."
        )
        
        try:
            response = Settings.llm.complete(prompt)
            answer = str(response).strip()
            
            # Verify the LLM didn't hallucinate a name not in the list
            if answer in self.canonical_teams:
                print(f"Auto-Healing learned that '{raw_name}' means '{answer}'")
                return answer
            return None
        except Exception as e:
            print(f"LLM Auto-Healing error for '{raw_name}': {e}")
            return None

    def normalize(self, raw_name: str) -> Optional[str]:
        raw_lower = raw_name.lower().strip()

        # 1. Memory Cache
        if raw_lower in self.aliases:
            return self.aliases[raw_lower]

        # 2. Fuzzy Match
        match_result = process.extractOne(raw_name, self.canonical_teams)
        if not match_result:
            return None

        match, score = match_result[:2]

        if score >= self.threshold:
            return match

        # 3. LLM Auto-Healing (Only if score > 50 to avoid total garbage)
        if score > 50:
            print(f"WARNING: Unmapped team '{raw_name}' (Score: {score}). Asking LLM...")
            llm_match = self._ask_llm(raw_name)
            if llm_match:
                self.aliases[raw_lower] = llm_match
                self._save_cache()
                return llm_match

        print(f"WARNING: Unmapped team name '{raw_name}' (Score: {score}). Discarding.")
        return None
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/normalizer.py
git commit -m "feat(ingestion): implement auto-healing llm normalizer and remove hardcoded aliases"
```

---

### Task 2: Update Normalizer Tests

**Files:**
- Modify: `backend/tests/ingestion/test_normalizer.py`

- [ ] **Step 1: Mock the cache and LLM in tests**

Update `backend/tests/ingestion/test_normalizer.py` to test the new flow:

```python
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

    teams = ["Manchester United", "Arsenal", "Chelsea"]
    normalizer = TeamNormalizer(teams)

    # 1. Exact/Fuzzy Match (>= 95)
    assert normalizer.normalize("Arsenal FC") == "Arsenal"
    
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
```

- [ ] **Step 2: Commit**

```bash
git add backend/tests/ingestion/test_normalizer.py
git commit -m "test: update normalizer tests for auto-healing and caching"
```
