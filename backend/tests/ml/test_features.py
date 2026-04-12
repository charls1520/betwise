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
        },
        {
            "home_team": "Chelsea",
            "away_team": "Arsenal",
            "home_xg": 1.2,
            "away_xg": 1.5,
            "home_goals": 1,
            "away_goals": 1,
        },
    ]

    df = build_features_for_matches(data)
    assert not df.empty
    assert "xg_diff" in df.columns
    assert "target_1x2" in df.columns
    assert "target_over25" in df.columns
