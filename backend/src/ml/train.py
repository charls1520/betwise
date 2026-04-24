import os
import joblib
import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from src.ml.features import build_features_for_matches


def train_and_save_models(df: pd.DataFrame, model_dir: str = "models"):
    """Trains independent models for each market and saves them."""
    os.makedirs(model_dir, exist_ok=True)

    features = ["xg_diff", "elo_diff"]
    
    # Robust imputation pipeline instead of fillna(0)
    imputer = SimpleImputer(strategy='median')

    X = df[features]

    models = {}
    metrics_file = os.path.join(model_dir, "model_metrics.json")
    
    current_metrics = {}
    if os.path.exists(metrics_file):
        with open(metrics_file, "r") as f:
            current_metrics = json.load(f)

    if "target_1x2" in df.columns:
        valid_idx = df["target_1x2"].notna()
        X_valid = X[valid_idx]
        y_valid = df.loc[valid_idx, "target_1x2"]

        if len(X_valid) > 0:
            X_train, X_test, y_train, y_test = train_test_split(X_valid, y_valid, test_size=0.2, random_state=42)
            
            winner_clf = Pipeline([
                ('imputer', imputer),
                ('rf', RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42))
            ])
            winner_clf.fit(X_train, y_train)
            
            y_pred = winner_clf.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            
            prev_acc = current_metrics.get("winner_model_acc", 0)
            
            if acc >= 0.50 and (acc >= prev_acc - 0.02):
                joblib.dump(winner_clf, os.path.join(model_dir, "winner_model.joblib"))
                models["winner_model"] = winner_clf
                current_metrics["winner_model_acc"] = acc
                print(f"Winner model deployed. Acc: {acc:.4f}")
            else:
                print(f"Winner model REJECTED. New Acc: {acc:.4f}, Prev: {prev_acc:.4f}")

    if "target_over25" in df.columns:
        valid_idx = df["target_over25"].notna()
        X_valid = X[valid_idx]
        y_valid = df.loc[valid_idx, "target_over25"]

        if len(X_valid) > 0:
            X_train, X_test, y_train, y_test = train_test_split(X_valid, y_valid, test_size=0.2, random_state=42)
            
            goals_clf = Pipeline([
                ('imputer', imputer),
                ('lr', LogisticRegression(random_state=42))
            ])
            goals_clf.fit(X_train, y_train)
            
            y_pred = goals_clf.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            
            prev_acc = current_metrics.get("goals_model_acc", 0)
            
            if acc >= 0.50 and (acc >= prev_acc - 0.02):
                joblib.dump(goals_clf, os.path.join(model_dir, "goals_model.joblib"))
                models["goals_model"] = goals_clf
                current_metrics["goals_model_acc"] = acc
                print(f"Goals model deployed. Acc: {acc:.4f}")
            else:
                print(f"Goals model REJECTED. New Acc: {acc:.4f}, Prev: {prev_acc:.4f}")

    with open(metrics_file, "w") as f:
        json.dump(current_metrics, f)

    return models


def run_weekly_training():
    from src.rag.config import init_llama_index
    init_llama_index()

    from src.ingestion.historical import download_football_data_co_uk
    from src.utils.logger import get_logger

    logger = get_logger()

    logger.info("Starting weekly ML continuous training...")
    logger.info("Downloading historical/live data...")
    raw_df = download_football_data_co_uk()

    if not raw_df.empty:
        logger.info(f"Downloaded {len(raw_df)} historical/live matches.")
        logger.info("Engineering features...")
        df_features = build_features_for_matches(raw_df.to_dict("records"))

        logger.info("Training models...")
        train_and_save_models(df_features)
        logger.info("Continuous models trained and saved successfully.")
    else:
        logger.error("Failed to download historical data. Aborting training.")

if __name__ == "__main__":
    run_weekly_training()
