import pandas as pd
from src.ingestion.validators import validate_history_sufficiency

def test_validate_history_sufficiency():
    df = pd.DataFrame([
        {"HomeTeam": "A", "AwayTeam": "B", "Date": "2023-01-01"},
        {"HomeTeam": "A", "AwayTeam": "C", "Date": "2023-01-08"},
        {"HomeTeam": "D", "AwayTeam": "A", "Date": "2023-01-15"},
    ])
    
    # Require 2 prior matches for both teams. A has 3, B, C, D have 1.
    valid_df = validate_history_sufficiency(df, min_matches=2)
    # Since B, C, D don't have 2 prior matches, none of the matches should pass if both require >= 2 history
    assert len(valid_df) == 0
    
    df2 = pd.DataFrame([
        {"HomeTeam": "A", "AwayTeam": "B"},
        {"HomeTeam": "A", "AwayTeam": "B"},
        {"HomeTeam": "A", "AwayTeam": "B"},
    ])
    valid_df2 = validate_history_sufficiency(df2, min_matches=2)
    # The third match has A and B with 2 prior matches, so it passes.
    assert len(valid_df2) == 1