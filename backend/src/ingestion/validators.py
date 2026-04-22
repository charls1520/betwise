from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import pandas as pd

class NewsArticle(BaseModel):
    title: str = Field(..., min_length=5)
    summary: str = Field(..., min_length=10)
    url: str

class MatchOdds(BaseModel):
    home_team: str
    away_team: str
    home_odds: float = Field(..., gt=1.0, lt=100.0)
    away_odds: float = Field(..., gt=1.0, lt=100.0)
    draw_odds: float = Field(..., gt=1.0, lt=100.0)

class EloScore(BaseModel):
    team: str
    elo: float = Field(..., gt=500.0, lt=2500.0)
    date: str

def validate_volume(current_count: int, expected_minimum: int = 1) -> bool:
    """Heuristic check: Ensure we didn't scrape 0 or abnormally few items."""
    if current_count < expected_minimum:
        print(f"Validation Error: Extracted {current_count} items, expected at least {expected_minimum}.")
        return False
    return True

def validate_history_sufficiency(df: pd.DataFrame, min_matches: int = 3) -> pd.DataFrame:
    """Filters matches where both teams don't have enough prior history in the dataset."""
    if df.empty:
        return df
        
    team_counts = {}
    valid_indices = []
    
    for idx, row in df.iterrows():
        home = row.get("HomeTeam", row.get("home_team"))
        away = row.get("AwayTeam", row.get("away_team"))
        
        home_count = team_counts.get(home, 0)
        away_count = team_counts.get(away, 0)
        
        if home_count >= min_matches and away_count >= min_matches:
            valid_indices.append(idx)
            
        team_counts[home] = home_count + 1
        team_counts[away] = away_count + 1
        
    return df.loc[valid_indices].copy()