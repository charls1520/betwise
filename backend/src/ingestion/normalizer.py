import os
import json
from thefuzz import process
from typing import List, Optional
from llama_index.core import Settings
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from src.utils.logger import get_logger

logger = get_logger()


class TeamNormalizer:
    def __init__(self, canonical_teams: List[str], threshold: int = 85):
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
        
        try:
            response = Settings.llm.complete(prompt)
        except ValueError as e:
            logger.error(f"LLM Configuration Error (Auto-healing skipped): {e}")
            return None
            
        answer = str(response).strip()
        
        # Verify the LLM didn't hallucinate a name not in the list
        if answer in self.canonical_teams:
            logger.info(f"Auto-Healing learned that '{raw_name}' means '{answer}'")
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

        match, score = match_result[
            :2
        ]  # extractOne returns (match, score) or (match, score, index)

        if score >= self.threshold:
            return match

        # 3. LLM Auto-Healing (Only if score > 50 to avoid total garbage)
        if score > 50:
            logger.warning(f"Unmapped team '{raw_name}' (Score: {score}). Asking LLM...")
            try:
                llm_match = self._ask_llm(raw_name)
                if llm_match:
                    self.aliases[raw_lower] = llm_match
                    self._save_cache()
                    return llm_match
            except RetryError as e:
                logger.error(f"LLM Auto-Healing failed after retries for '{raw_name}': {e}")
            except Exception as e:
                logger.exception(f"Unexpected LLM error for '{raw_name}': {e}")

        logger.warning(
            f"Unmapped team name '{raw_name}' (Score: {score}). Discarding."
        )
        return None
