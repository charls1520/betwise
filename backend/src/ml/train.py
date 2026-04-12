import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


def train_and_save_models(df: pd.DataFrame, model_dir: str = "models"):
    """Trains independent models for each market and saves them."""
    os.makedirs(model_dir, exist_ok=True)
    features = ["xg_diff"]
    X = df[features]

    models = {}

    # 1. Match Winner (1X2) Model
    if "target_1x2" in df.columns:
        winner_clf = RandomForestClassifier(n_estimators=10, random_state=42)
        winner_clf.fit(X, df["target_1x2"])
        joblib.dump(winner_clf, os.path.join(model_dir, "winner_model.joblib"))
        models["winner_model"] = winner_clf

    # 2. Total Goals (Over/Under 2.5) Model
    if "target_over25" in df.columns:
        goals_clf = LogisticRegression(random_state=42)
        goals_clf.fit(X, df["target_over25"])
        joblib.dump(goals_clf, os.path.join(model_dir, "goals_model.joblib"))
        models["goals_model"] = goals_clf

    return models
