import pandas as pd


def build_features_for_matches(raw_matches: list) -> pd.DataFrame:
    """
    Transforms raw match dictionaries into a DataFrame with engineered features
    and target variables suitable for training.
    """
    df = pd.DataFrame(raw_matches)
    if df.empty:
        return df

    # Feature Engineering
    # 1. Expected Goals Difference (if available from Understat)
    if "home_xg" in df.columns and "away_xg" in df.columns:
        df["xg_diff"] = df["home_xg"] - df["away_xg"]
    else:
        # Fallback for historical data without xG (simplification for V1)
        df["xg_diff"] = 0.0

    # Target Variables (Historical Training)
    # football-data.co.uk uses FTR (H, D, A) and FTHG, FTAG
    if "FTR" in df.columns:
        # 0: Away, 1: Draw, 2: Home
        ftr_map = {"A": 0, "D": 1, "H": 2}
        df["target_1x2"] = df["FTR"].map(ftr_map)

    if "FTHG" in df.columns and "FTAG" in df.columns:
        df["target_over25"] = ((df["FTHG"] + df["FTAG"]) > 2.5).astype(int)

    # Target Variables (Live/Mock training fallback)
    elif "home_goals" in df.columns and "away_goals" in df.columns:
        # Match Winner Target (0: Away, 1: Draw, 2: Home)
        def get_1x2(row):
            if row["home_goals"] > row["away_goals"]:
                return 2
            if row["home_goals"] == row["away_goals"]:
                return 1
            return 0

        df["target_1x2"] = df.apply(get_1x2, axis=1)

        # Over/Under Target (1: Over 2.5, 0: Under 2.5)
        df["target_over25"] = ((df["home_goals"] + df["away_goals"]) > 2.5).astype(int)

    return df
