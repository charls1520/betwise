from thefuzz import process
from typing import List, Optional


class TeamNormalizer:
    def __init__(self, canonical_teams: List[str], threshold: int = 95):
        self.canonical_teams = canonical_teams
        self.threshold = threshold

        # Hardcoded, exhaustive overrides for strict matching
        self.manual_overrides = {
            "man utd": "Manchester United",
            "manchester utd": "Manchester United",
            "man city": "Manchester City",
            "manchester city": "Manchester City",
            "spurs": "Tottenham Hotspur",
            "tottenham": "Tottenham Hotspur",
            "west ham united": "West Ham",
            "nott'm forest": "Nottingham Forest",
            "newcastle united": "Newcastle United",
            "sheffield utd": "Sheffield United",
            "wolverhampton wanderers": "Wolverhampton Wanderers",
            "brighton and hove albion": "Brighton",
            "brighton & hove albion": "Brighton",
            "leeds united": "Leeds",
            "tottenham hotspur": "Tottenham"
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

        # Log unmapped team exception here in a real scenario
        print(
            f"WARNING: Unmapped team name '{raw_name}' (Score: {score}). Needs manual override."
        )
        return None
