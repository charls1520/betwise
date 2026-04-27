import os
import joblib
import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
import numpy as np
from src.ml.features import build_features_for_matches


def train_and_save_models(df: pd.DataFrame, model_dir: str = "models"):
    """Trains independent models for each market and saves them."""
    os.makedirs(model_dir, exist_ok=True)

    features = ["xg_diff", "elo_diff", "rest_days_diff", "shots_on_target_diff", "is_end_of_season", "goals_scored_general_diff", "goals_conceded_general_diff"]
    
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

    if "FTHG" in df.columns:
        valid_idx = df["FTHG"].notna()
        X_valid = X[valid_idx]
        y_valid = df.loc[valid_idx, "FTHG"]

        if len(X_valid) > 0:
            X_train, X_test, y_train, y_test = train_test_split(X_valid, y_valid, test_size=0.2, random_state=42)
            
            home_goals_clf = Pipeline([
                ('imputer', imputer),
                ('xgb', XGBRegressor(random_state=42, objective='reg:squarederror'))
            ])
            home_goals_clf.fit(X_train, y_train)
            
            y_pred = home_goals_clf.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            prev_rmse = current_metrics.get("home_goals_model_rmse", 999.0)
            
            if rmse < 1.3 and (rmse <= prev_rmse + 0.1):
                joblib.dump(home_goals_clf, os.path.join(model_dir, "home_goals_model.joblib"))
                models["home_goals_model"] = home_goals_clf
                current_metrics["home_goals_model_rmse"] = rmse
                current_metrics["home_goals_model_mae"] = mae
                print(f"Home goals model deployed. RMSE: {rmse:.4f}, MAE: {mae:.4f}")
            else:
                print(f"Home goals model REJECTED. New RMSE: {rmse:.4f}, Prev: {prev_rmse:.4f}")

    if "FTAG" in df.columns:
        valid_idx = df["FTAG"].notna()
        X_valid = X[valid_idx]
        y_valid = df.loc[valid_idx, "FTAG"]

        if len(X_valid) > 0:
            X_train, X_test, y_train, y_test = train_test_split(X_valid, y_valid, test_size=0.2, random_state=42)
            
            away_goals_clf = Pipeline([
                ('imputer', imputer),
                ('xgb', XGBRegressor(random_state=42, objective='reg:squarederror'))
            ])
            away_goals_clf.fit(X_train, y_train)
            
            y_pred = away_goals_clf.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            prev_rmse = current_metrics.get("away_goals_model_rmse", 999.0)
            
            if rmse < 1.3 and (rmse <= prev_rmse + 0.1):
                joblib.dump(away_goals_clf, os.path.join(model_dir, "away_goals_model.joblib"))
                models["away_goals_model"] = away_goals_clf
                current_metrics["away_goals_model_rmse"] = rmse
                current_metrics["away_goals_model_mae"] = mae
                print(f"Away goals model deployed. RMSE: {rmse:.4f}, MAE: {mae:.4f}")
            else:
                print(f"Away goals model REJECTED. New RMSE: {rmse:.4f}, Prev: {prev_rmse:.4f}")

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
    # Solo buscamos actualizaciones de las temporadas en curso para evitar procesar errores viejos
    raw_df = download_football_data_co_uk(seasons=["2526", "2425"])

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
