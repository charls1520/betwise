# LLM Rate Limits Mitigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent OpenRouter/Ollama rate limit errors from silently discarding valid rows during auto-healing by adding robust exponential backoff retries.

**Architecture:** Use `tenacity` to wrap the `_ask_llm` method in `TeamNormalizer`. Remove the generic `try/except` inside the method so `tenacity` can intercept the HTTP/RateLimit exceptions, wait exponentially, and retry. Handle the final `RetryError` in the caller (`normalize`) to safely return `None` if all retries fail.

**Tech Stack:** Python, Tenacity, LlamaIndex.

---

### Task 1: Refactor `TeamNormalizer` with Retries

**Files:**
- Modify: `backend/src/ingestion/normalizer.py`

- [ ] **Step 1: Add tenacity and refactor `_ask_llm`**

Modify `backend/src/ingestion/normalizer.py` to import `tenacity` and apply the retry logic to `_ask_llm`:

```python
import os
import json
from thefuzz import process
from typing import List, Optional
from llama_index.core import Settings
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError

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

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=5, max=30))
    def _ask_llm(self, raw_name: str) -> Optional[str]:
        if not getattr(Settings, "llm", None):
            return None
            
        prompt = (
            f"The scraper found the team '{raw_name}'. "
            f"Which of these official Premier League teams does it refer to: {self.canonical_teams}? "
            f"You must reply EXCLUSIVAMENTE with the exact official team name from the list, with no punctuation or extra text. "
            f"If it is none of them, reply 'NONE'."
        )
        
        # We removed the generic try-except here so tenacity can catch network/rate-limit exceptions.
        response = Settings.llm.complete(prompt)
        answer = str(response).strip()
        
        if answer in self.canonical_teams:
            print(f"Auto-Healing learned that '{raw_name}' means '{answer}'")
            return answer
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

        # 3. LLM Auto-Healing
        if score > 50:
            print(f"WARNING: Unmapped team '{raw_name}' (Score: {score}). Asking LLM...")
            try:
                llm_match = self._ask_llm(raw_name)
                if llm_match:
                    self.aliases[raw_lower] = llm_match
                    self._save_cache()
                    return llm_match
            except RetryError as e:
                print(f"LLM Auto-Healing failed after retries for '{raw_name}': {e}")
            except Exception as e:
                print(f"Unexpected LLM error for '{raw_name}': {e}")

        print(f"WARNING: Unmapped team name '{raw_name}' (Score: {score}). Discarding.")
        return None
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/ingestion/normalizer.py
git commit -m "feat(ingestion): add tenacity exponential backoff to LLM auto-healing"
```

---

### Task 2: Update Tests for Normalizer Retries

**Files:**
- Modify: `backend/tests/ingestion/test_normalizer.py`

- [ ] **Step 1: Handle `RetryError` in test mock**

If tests mock `_ask_llm` directly, they bypass `tenacity` entirely, which is fine since we mock the method itself.
Check `backend/tests/ingestion/test_normalizer.py`. In `test_team_normalizer_auto_healing`, we have:
`monkeypatch.setattr("src.ingestion.normalizer.TeamNormalizer._ask_llm", lambda self, name: "Manchester United" if "man" in name.lower() else None)`

This actually replaces the wrapped `_ask_llm` with a simple lambda, which completely bypasses the retry wrapper. This means our tests will not break due to `tenacity` unless we specifically want to test the retry logic. Since we just want to ensure the logic works without hanging, no changes are strictly necessary to the tests.

However, to be safe, let's just run pytest to confirm.

```bash
docker exec betwise_backend pytest tests/ingestion/test_normalizer.py -v
```

- [ ] **Step 2: Commit (if changes needed)**

If any test needs changes, commit them. Otherwise, skip this commit.
````