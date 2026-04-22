import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from src.ml.features import build_features_for_matches


def train_and_save_models(df: pd.DataFrame, model_dir: str = "models"):
    """Trains independent models for each market and saves them."""
    os.makedirs(model_dir, exist_ok=True)

    features = ["xg_diff", "elo_diff"]
    
    # Robust imputation pipeline instead of fillna(0)
    imputer = SimpleImputer(strategy='median')

    X = df[features]

    models = {}

    if "target_1x2" in df.columns:
        valid_idx = df["target_1x2"].notna()
        X_valid = X[valid_idx]
        y_valid = df.loc[valid_idx, "target_1x2"]

        if len(X_valid) > 0:
            winner_clf = Pipeline([
                ('imputer', imputer),
                ('rf', RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42))
            ])
            winner_clf.fit(X_valid, y_valid)
            joblib.dump(winner_clf, os.path.join(model_dir, "winner_model.joblib"))
            models["winner_model"] = winner_clf

    if "target_over25" in df.columns:
        valid_idx = df["target_over25"].notna()
        X_valid = X[valid_idx]
        y_valid = df.loc[valid_idx, "target_over25"]

        if len(X_valid) > 0:
            goals_clf = Pipeline([
                ('imputer', imputer),
                ('lr', LogisticRegression(random_state=42))
            ])
            goals_clf.fit(X_valid, y_valid)
            joblib.dump(goals_clf, os.path.join(model_dir, "goals_model.joblib"))
            models["goals_model"] = goals_clf

    return models


if __name__ == "__main__":
    from src.ingestion.historical import download_football_data_co_uk

    print("Downloading historical data...")
    raw_df = download_football_data_co_uk()

    if not raw_df.empty:
        print(f"Downloaded {len(raw_df)} historical matches.")
        print("Engineering features...")
        df_features = build_features_for_matches(raw_df.to_dict("records"))

        print("Training models...")
        train_and_save_models(df_features)
        print("Models trained and saved successfully.")
    else:
        print("Failed to download historical data.")
