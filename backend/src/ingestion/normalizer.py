from thefuzz import process
from typing import List, Optional


class TeamNormalizer:
    def __init__(self, canonical_teams: List[str], threshold: int = 80):
        self.canonical_teams = canonical_teams
        self.threshold = threshold

        # Hardcoded overrides for common aliases that fuzzy matching might miss
        self.manual_overrides = {
            "man utd": "Manchester United",
            "man city": "Manchester City",
            "spurs": "Tottenham Hotspur",
        }

    def normalize(self, raw_name: str) -> Optional[str]:
        raw_lower = raw_name.lower().strip()

        if raw_lower in self.manual_overrides:
            return self.manual_overrides[raw_lower]

        match_result = process.extractOne(raw_name, self.canonical_teams)
        if not match_result:
            return None

        match, score = match_result[
            :2
        ]  # extractOne returns (match, score) or (match, score, index)

        if score >= self.threshold:
            return match
        return None
