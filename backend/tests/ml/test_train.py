import os
import pandas as pd
from unittest.mock import patch
from src.ml.train import train_and_save_models

@patch("src.ml.train.optimize_xgboost_classifier", return_value={'max_depth': 3, 'learning_rate': 0.1, 'n_estimators': 50, 'subsample': 0.8, 'colsample_bytree': 0.8, 'random_state': 42, 'objective': 'multi:softprob'})
@patch("src.ml.train.optimize_xgboost", return_value={'max_depth': 3, 'learning_rate': 0.1, 'n_estimators': 50, 'subsample': 0.8, 'colsample_bytree': 0.8, 'random_state': 42, 'objective': 'reg:squarederror'})
@patch("src.ml.train.mean_squared_error", return_value=1.0)
@patch("src.ml.train.mean_absolute_error", return_value=1.0)
@patch("src.ml.train.accuracy_score", return_value=1.0)
def test_train_and_save_models(mock_acc, mock_mae, mock_mse, mock_opt, mock_opt_clf, tmp_path):
    # Dummy data
    df = pd.DataFrame(
        {
            "elo_diff": [100, -50, 20, 250, -150, 0, 100, -50, 20, 250, -150, 0],
            "rest_days_diff": [0, 1, -1, 0, 2, -2, 0, 1, -1, 0, 2, -2],
            "shots_on_target_diff": [2.0, -1.0, 0.5, 3.0, -2.0, 0.0, 2.0, -1.0, 0.5, 3.0, -2.0, 0.0],
            "is_end_of_season": [0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0],
            "goals_scored_general_diff": [0.5, -0.5, 0.2, 1.0, -1.0, 0.0, 0.5, -0.5, 0.2, 1.0, -1.0, 0.0],
            "goals_conceded_general_diff": [0.2, 0.1, -0.2, -0.5, 1.0, 0.0, 0.2, 0.1, -0.2, -0.5, 1.0, 0.0],
            "offensive_efficiency_diff": [0.1, -0.1, 0.0, 0.2, -0.2, 0.1, 0.1, -0.1, 0.0, 0.2, -0.2, 0.1],
            "defensive_efficiency_diff": [0.0, 0.2, -0.1, -0.2, 0.1, 0.0, 0.0, 0.2, -0.1, -0.2, 0.1, 0.0],
            "target_1x2": [2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1],
            "FTHG": [2, 0, 1, 3, 0, 1, 2, 0, 1, 3, 0, 1],
            "FTAG": [1, 0, 0, 1, 2, 1, 1, 0, 0, 1, 2, 1],
        }
    )

    model_dir = str(tmp_path)
    models = train_and_save_models(df, model_dir)

    assert "winner_model" in models
    assert "home_goals_model" in models
    assert "away_goals_model" in models
    assert os.path.exists(os.path.join(model_dir, "winner_model.joblib"))
    assert os.path.exists(os.path.join(model_dir, "home_goals_model.joblib"))
    assert os.path.exists(os.path.join(model_dir, "away_goals_model.joblib"))

@patch("src.ml.train.optimize_xgboost_classifier", return_value={'max_depth': 3, 'learning_rate': 0.1, 'n_estimators': 50, 'subsample': 0.8, 'colsample_bytree': 0.8, 'random_state': 42, 'objective': 'multi:softprob'})
@patch("src.ml.train.optimize_xgboost", return_value={'max_depth': 3, 'learning_rate': 0.1, 'n_estimators': 50, 'subsample': 0.8, 'colsample_bytree': 0.8, 'random_state': 42, 'objective': 'reg:squarederror'})
@patch("src.ml.train.mean_squared_error", return_value=1.0)
@patch("src.ml.train.mean_absolute_error", return_value=1.0)
@patch("src.ml.train.accuracy_score", return_value=1.0)
def test_train_and_save_models_with_imputation(mock_acc, mock_mae, mock_mse, mock_opt, mock_opt_clf, tmp_path):
    df = pd.DataFrame({
        "elo_diff": [100, -50, 20, None, 100, -50, 20, None, 100, -50],
        "rest_days_diff": [1, -1, None, 0, 2, -2, None, 0, 1, -1],
        "shots_on_target_diff": [1.5, -0.5, None, 2.0, 1.0, -1.0, None, 1.5, 0.5, -0.5],
        "is_end_of_season": [0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
        "goals_scored_general_diff": [0.5, -0.5, None, 1.0, -1.0, 0.0, None, -0.5, 0.2, 1.0],
        "goals_conceded_general_diff": [0.2, 0.1, None, -0.5, 1.0, 0.0, None, 0.1, -0.2, -0.5],
        "offensive_efficiency_diff": [0.1, -0.1, None, 0.2, -0.2, 0.1, None, 0.1, -0.1, 0.0],
        "defensive_efficiency_diff": [0.0, 0.2, None, -0.2, 0.1, 0.0, None, 0.2, -0.1, -0.2],
        "target_1x2": [1, 2, 0, 1, 1, 2, 0, 1, 1, 2],
        "FTHG": [2, 0, 1, 3, 0, 1, 2, 0, 1, 3],
        "FTAG": [1, 0, 0, 1, 2, 1, 1, 0, 0, 1],
    })
    
    # Train should handle NaNs by dropping or imputing internally
    models = train_and_save_models(df, model_dir=str(tmp_path))
    assert "winner_model" in models
    assert "home_goals_model" in models
    assert "away_goals_model" in models

# from src.ml.train import run_weekly_training
#
# @patch("src.ml.train.train_and_save_models")
# @patch("src.ml.train.build_features_for_matches")
# @patch("src.ingestion.historical.download_football_data_co_uk")
# @patch("src.rag.config.init_llama_index")
# def test_run_weekly_training(mock_init_llama, mock_download, mock_build, mock_train):
#     mock_download.return_value = pd.DataFrame([{"dummy": "data"}])
#     mock_build.return_value = pd.DataFrame([{"feat": 1}])
#     
#     run_weekly_training()
#     
#     mock_init_llama.assert_called_once()
#     mock_download.assert_called_once()
#     mock_build.assert_called_once()
#     mock_train.assert_called_once()