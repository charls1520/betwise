import os
import joblib
import math
import pandas as pd
from src.ml.features import build_features_for_matches

def poisson_prob(lmbda, k):
    return (math.pow(lmbda, k) * math.exp(-lmbda)) / math.factorial(k)

def predict_matches(raw_matches: list, model_dir: str = "models", history_file: str = "data/historical/merged_history_cache.csv") -> list:
    """Loads trained models and predicts probabilities for new matches."""
    if not raw_matches:
        return []

    df_future = pd.DataFrame(raw_matches)
    
    # Map odds API keys to historical data keys for feature building
    if 'home_team' in df_future.columns:
        df_future = df_future.rename(columns={'home_team': 'HomeTeam', 'away_team': 'AwayTeam', 'commence_time': 'Date'})
        if 'home_xg' in df_future.columns:
            df_future = df_future.rename(columns={'home_xg': 'Home_xG', 'away_xg': 'Away_xG', 'home_elo': 'Home_Elo', 'away_elo': 'Away_Elo'})
            
    df_future['is_future'] = True
    df_future['original_index'] = range(len(df_future))

    if os.path.exists(history_file):
        try:
            df_history = pd.read_csv(history_file)
            df_history = df_history.assign(is_future=False, original_index=-1)
            combined_df = pd.concat([df_history, df_future], ignore_index=True)
            df_featured = build_features_for_matches(combined_df.to_dict("records"))
            df = df_featured[df_featured['is_future'] == True].copy()
            df = df.sort_values('original_index').reset_index(drop=True)
            df = df.drop(columns=['is_future', 'original_index'])
        except Exception as e:
            # Fallback if there is an error loading history
            df = build_features_for_matches(raw_matches)
    else:
        df = build_features_for_matches(raw_matches)

    if df.empty:
        return []

    features = [
        "elo_diff", "rest_days_diff", "shots_on_target_diff", 
        "is_end_of_season", "goals_scored_general_diff", "goals_conceded_general_diff",
        "offensive_efficiency_diff", "defensive_efficiency_diff", "market_implied_diff"
    ]
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
                float(probs_1x2[classes.index(2)]) if 2 in classes else 0.0
            )
            match_pred["prob_draw"] = (
                float(probs_1x2[classes.index(0)]) if 0 in classes else 0.0
            )
            match_pred["prob_home_win"] = (
                float(probs_1x2[classes.index(1)]) if 1 in classes else 0.0
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