import pandas as pd
from src.ml.features import build_features_for_matches


def test_build_features_for_matches():
    # Mock some raw match data
    data = [
        {
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "home_xg": 2.1,
            "away_xg": 0.8,
            "home_goals": 2,
            "away_goals": 0,
            "FTR": "H",
            "FTHG": 2,
            "FTAG": 0
        },
        {
            "home_team": "Chelsea",
            "away_team": "Arsenal",
            "home_xg": 1.2,
            "away_xg": 1.5,
            "home_goals": 1,
            "away_goals": 1,
            "FTR": "D",
            "FTHG": 1,
            "FTAG": 1
        },
    ]

    df = build_features_for_matches(data)
    assert not df.empty
    assert "xg_diff" in df.columns
    assert "target_1x2" in df.columns
    assert "target_over25" in df.columns


def test_build_features_from_historical():
    data = [
        {
            "HomeTeam": "Arsenal",
            "AwayTeam": "Chelsea",
            "Home_xG": 2.1,
            "Away_xG": 0.8,
            "Home_Elo": 1800,
            "Away_Elo": 1700,
            "FTHG": 2,
            "FTAG": 0,
            "FTR": "H",
        },
        {
            "HomeTeam": "Chelsea",
            "AwayTeam": "Arsenal",
            "Home_xG": 1.2,
            "Away_xG": 1.5,
            "Home_Elo": 1700,
            "Away_Elo": 1800,
            "FTHG": 1,
            "FTAG": 1,
            "FTR": "D",
        },
    ]
    df = build_features_for_matches(data)
    # The updated function should map FTR to target_1x2
    assert "target_1x2" in df.columns
    assert df["target_1x2"].iloc[0] == 1  # Home
    assert df["target_1x2"].iloc[1] == 0  # Draw
