import pandas as pd
import numpy as np
from features import build_features_for_matches

matches = [
    {"Date": "2023-01-01", "HomeTeam": "A", "AwayTeam": "B", "FTHG": 2, "FTAG": 1, "HST": 5, "AST": 3},
    {"Date": "2023-01-02", "HomeTeam": "C", "AwayTeam": "A", "FTHG": 0, "FTAG": 3, "HST": 2, "AST": 6},
    {"Date": "2023-01-03", "HomeTeam": "A", "AwayTeam": "D", "FTHG": 1, "FTAG": 1, "HST": 4, "AST": 4},
]

df = pd.DataFrame(matches)
out_df = build_features_for_matches(matches)
print(out_df.columns)
print(out_df[['HomeTeam', 'home_avg_goals_scored_general']])
