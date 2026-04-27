import os
import pandas as pd
from unittest.mock import patch
from src.ml.train import train_and_save_models
from src.ml.inference import predict_matches

@patch("src.ml.train.optimize_xgboost_classifier", return_value={'max_depth': 3, 'learning_rate': 0.1, 'n_estimators': 50, 'subsample': 0.8, 'colsample_bytree': 0.8, 'random_state': 42, 'objective': 'multi:softprob'})
@patch("src.ml.train.optimize_xgboost", return_value={'max_depth': 3, 'learning_rate': 0.1, 'n_estimators': 50, 'subsample': 0.8, 'colsample_bytree': 0.8, 'random_state': 42, 'objective': 'reg:squarederror'})
@patch("src.ml.train.mean_squared_error", return_value=1.0)
@patch("src.ml.train.mean_absolute_error", return_value=1.0)
@patch("src.ml.train.accuracy_score", return_value=1.0)
def test_predict_matches(mock_acc, mock_mae, mock_mse, mock_opt, mock_opt_clf, tmp_path):
    # Train dummy models
    df_train = pd.DataFrame(
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
    train_and_save_models(df_train, model_dir)

    # Inference data
    df_infer = pd.DataFrame(
        [
            {
                "HomeTeam": "Arsenal",
                "AwayTeam": "Chelsea",
                "Home_xG": 2.0,
                "Away_xG": 0.5,
                "Home_Elo": 1800,
                "Away_Elo": 1700,
                "Date": "2026-05-01"
            }
        ]
    )

    # Mock history file
    history_df = pd.DataFrame({
        "HomeTeam": ["Arsenal", "Chelsea", "Arsenal"],
        "AwayTeam": ["TeamA", "TeamB", "TeamC"],
        "Date": ["2026-04-10", "2026-04-12", "2026-04-20"],
        "Home_xG": [1.5, 1.0, 2.0],
        "Away_xG": [0.5, 0.8, 1.0],
        "Home_Elo": [1780, 1690, 1790],
        "Away_Elo": [1500, 1550, 1600],
        "FTHG": [2, 1, 3],
        "FTAG": [0, 1, 1],
        "HST": [5, 3, 6],
        "AST": [2, 4, 3]
    })
    history_file_path = os.path.join(tmp_path, "mock_history.csv")
    history_df.to_csv(history_file_path, index=False)

    predictions = predict_matches(df_infer.to_dict("records"), model_dir, history_file=history_file_path)

    assert len(predictions) == 1
    assert "prob_home_win" in predictions[0]
    assert "prob_over25" in predictions[0]
    assert "expected_home_goals" in predictions[0]
    assert "expected_away_goals" in predictions[0]