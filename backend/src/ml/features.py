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
    # In a real scenario, this would use rolling averages. We use raw xg diff for simplicity here.
    df["xg_diff"] = df.get("home_xg", 0) - df.get("away_xg", 0)

    # Target Variables
    if "home_goals" in df.columns and "away_goals" in df.columns:
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
