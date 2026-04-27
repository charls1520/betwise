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

def test_build_features_rolling_and_imputation():
    matches = [
        {"HomeTeam": "A", "AwayTeam": "B", "Home_xG": 1.0, "Away_xG": 0.5, "Home_Elo": 1500, "Away_Elo": 1400, "FTR": "H"},
        {"HomeTeam": "C", "AwayTeam": "A", "Home_xG": None, "Away_xG": 1.5, "Home_Elo": 1450, "Away_Elo": None, "FTR": "A"}
    ]
    df = build_features_for_matches(matches)
    
    # Check NaN imputation (forward fill or global mean fallback)
    assert not df["xg_diff"].isna().any()
    assert not df["elo_diff"].isna().any()

def test_new_ml_features():
    # Simulamos un dataset histórico de un equipo
    data = [
        {"Date": "2023-01-01", "HomeTeam": "TeamA", "AwayTeam": "TeamB", "FTHG": 1, "FTAG": 0, "HST": 5, "AST": 2, "Home_xG": 1.2, "Away_xG": 0.8, "Home_Elo": 1500, "Away_Elo": 1400},
        {"Date": "2023-01-05", "HomeTeam": "TeamC", "AwayTeam": "TeamA", "FTHG": 2, "FTAG": 1, "HST": 4, "AST": 3, "Home_xG": 1.5, "Away_xG": 1.0, "Home_Elo": 1450, "Away_Elo": 1505},
        # TeamA descansa 15 dias (se debe capear a 10)
        {"Date": "2023-01-20", "HomeTeam": "TeamA", "AwayTeam": "TeamD", "FTHG": 0, "FTAG": 0, "HST": 6, "AST": 4, "Home_xG": 1.4, "Away_xG": 1.1, "Home_Elo": 1500, "Away_Elo": 1350}
    ]
    
    # Creamos un DF con 30+ partidos para testear is_end_of_season
    for i in range(35):
        data.append({"Date": f"2023-02-{i%28+1:02d}", "HomeTeam": "TeamA", "AwayTeam": "TeamB", "FTHG": 1, "FTAG": 1, "HST": 2, "AST": 2, "Home_xG": 1.0, "Away_xG": 1.0, "Home_Elo": 1500, "Away_Elo": 1400})
        
    df = build_features_for_matches(data)
    
    assert "home_rest_days" in df.columns
    assert "away_rest_days" in df.columns
    assert "rest_days_diff" in df.columns
    assert "shots_on_target_diff" in df.columns
    assert "is_end_of_season" in df.columns
    
    # Verificamos que no haya leakage y el capping funcione
    # El partido del 2023-01-20 de TeamA fue 15 dias despues del 2023-01-05. El cap es 10.
    # En el index 2, TeamA es local. Su descanso deberia ser 10.
    assert df.loc[2, "home_rest_days"] == 10.0
    
    # El ultimo partido debe tener is_end_of_season en 1
    assert df.iloc[-1]["is_end_of_season"] == 1

