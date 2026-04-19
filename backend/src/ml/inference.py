import os
import joblib
import pandas as pd
from src.ml.features import build_features_for_matches


def predict_matches(raw_matches: list, model_dir: str = "models") -> list:
    """Loads trained models and predicts probabilities for new matches."""
    df = build_features_for_matches(raw_matches)
    if df.empty:
        return []

    features = ["xg_diff", "elo_diff"]
    for col in features:
        if col not in df.columns:
            df[col] = 0
    X = df[features]

    winner_model_path = os.path.join(model_dir, "winner_model.joblib")
    goals_model_path = os.path.join(model_dir, "goals_model.joblib")

    winner_clf = (
        joblib.load(winner_model_path) if os.path.exists(winner_model_path) else None
    )
    goals_clf = (
        joblib.load(goals_model_path) if os.path.exists(goals_model_path) else None
    )

    results = []
    for i in range(len(df)):
        row = df.iloc[i : i + 1]
        x_row = X.iloc[i : i + 1]
        match_pred = {"match_index": i}

        if winner_clf:
            probs_1x2 = winner_clf.predict_proba(x_row)[0]
            # Assuming classes are [0, 1, 2] -> [Away, Draw, Home]
            classes = list(winner_clf.classes_)
            match_pred["prob_away_win"] = (
                probs_1x2[classes.index(0)] if 0 in classes else 0.0
            )
            match_pred["prob_draw"] = (
                probs_1x2[classes.index(1)] if 1 in classes else 0.0
            )
            match_pred["prob_home_win"] = (
                probs_1x2[classes.index(2)] if 2 in classes else 0.0
            )

        if goals_clf:
            probs_goals = goals_clf.predict_proba(x_row)[0]
            # Assuming classes are [0, 1] -> [Under, Over]
            classes = list(goals_clf.classes_)
            match_pred["prob_under25"] = (
                probs_goals[classes.index(0)] if 0 in classes else 0.0
            )
            match_pred["prob_over25"] = (
                probs_goals[classes.index(1)] if 1 in classes else 0.0
            )

        results.append(match_pred)

    return results
