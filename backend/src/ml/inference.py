import os
import joblib
import math
import pandas as pd
from src.ml.features import build_features_for_matches

def poisson_prob(lmbda, k):
    return (math.pow(lmbda, k) * math.exp(-lmbda)) / math.factorial(k)

def predict_matches(raw_matches: list, model_dir: str = "models") -> list:
    """Loads trained models and predicts probabilities for new matches."""
    df = build_features_for_matches(raw_matches)
    if df.empty:
        return []

    features = ["xg_diff", "elo_diff", "rest_days_diff", "shots_on_target_diff", "is_end_of_season", "goals_scored_general_diff", "goals_conceded_general_diff"]
    for col in features:
        if col not in df.columns:
            df[col] = 0
    X = df[features]

    winner_model_path = os.path.join(model_dir, "winner_model.joblib")
    home_goals_model_path = os.path.join(model_dir, "home_goals_model.joblib")
    away_goals_model_path = os.path.join(model_dir, "away_goals_model.joblib")

    winner_clf = (
        joblib.load(winner_model_path) if os.path.exists(winner_model_path) else None
    )
    home_goals_clf = (
        joblib.load(home_goals_model_path) if os.path.exists(home_goals_model_path) else None
    )
    away_goals_clf = (
        joblib.load(away_goals_model_path) if os.path.exists(away_goals_model_path) else None
    )

    results = []
    for i in range(len(df)):
        row = df.iloc[i : i + 1]
        x_row = X.iloc[i : i + 1]
        match_pred = {"match_index": i}

        if winner_clf:
            probs_1x2 = winner_clf.predict_proba(x_row)[0]
            # Based on features.py: "H": 1, "D": 0, "A": 2
            classes = list(winner_clf.classes_)
            match_pred["prob_away_win"] = (
                probs_1x2[classes.index(2)] if 2 in classes else 0.0
            )
            match_pred["prob_draw"] = (
                probs_1x2[classes.index(0)] if 0 in classes else 0.0
            )
            match_pred["prob_home_win"] = (
                probs_1x2[classes.index(1)] if 1 in classes else 0.0
            )

        if home_goals_clf and away_goals_clf:
            exp_home = max(0, home_goals_clf.predict(x_row)[0])
            exp_away = max(0, away_goals_clf.predict(x_row)[0])
            
            match_pred["expected_home_goals"] = float(exp_home)
            match_pred["expected_away_goals"] = float(exp_away)
            
            total_lambda = exp_home + exp_away
            if total_lambda > 0:
                prob_under25 = sum(poisson_prob(total_lambda, k) for k in range(3))
                prob_over25 = 1.0 - prob_under25
            else:
                prob_under25 = 1.0
                prob_over25 = 0.0
                
            match_pred["prob_under25"] = prob_under25
            match_pred["prob_over25"] = prob_over25

        results.append(match_pred)

    return results