import pandas as pd

def build_features_for_matches(matches: list) -> pd.DataFrame:
    df = pd.DataFrame(matches)
    if df.empty:
        return df

    # We now expect 'Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo' instead of shots/corners
    if all(col in df.columns for col in ['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo']):
        df["xg_diff"] = df["Home_xG"] - df["Away_xG"]
        df["elo_diff"] = df["Home_Elo"] - df["Away_Elo"]
    else:
        # Fallback for inference format
        if "home_xg" in df.columns and "away_xg" in df.columns:
            df["xg_diff"] = df["home_xg"] - df["away_xg"]
        if "home_elo" in df.columns and "away_elo" in df.columns:
            df["elo_diff"] = df["home_elo"] - df["away_elo"]

    # Target Variables
    if "FTR" in df.columns:
        df["target_1x2"] = df["FTR"].map({"H": 1, "D": 0, "A": 2})
    if "FTHG" in df.columns and "FTAG" in df.columns:
        df["target_over25"] = ((df["FTHG"] + df["FTAG"]) > 2.5).astype(int)

    return df