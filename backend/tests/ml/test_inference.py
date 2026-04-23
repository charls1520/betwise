import pandas as pd
from unittest.mock import patch
from src.ml.train import train_and_save_models
from src.ml.inference import predict_matches

@patch("src.ml.train.accuracy_score", return_value=1.0)
def test_predict_matches(mock_acc, tmp_path):
    # Train dummy models
    df_train = pd.DataFrame(
        {
            "xg_diff": [1.0, -0.5, 0.2, 2.5, -1.5, 0.0, 1.0, -0.5, 0.2, 2.5, -1.5, 0.0],
            "elo_diff": [100, -50, 20, 250, -150, 0, 100, -50, 20, 250, -150, 0],
            "target_1x2": [2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1],
            "target_over25": [1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0],
        }
    )
    model_dir = str(tmp_path)
    train_and_save_models(df_train, model_dir)

    # Inference data
    df_infer = pd.DataFrame(
        [
            {
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "home_xg": 2.0,
                "away_xg": 0.5,
                "home_elo": 1800,
                "away_elo": 1700,
            }
        ]
    )

    predictions = predict_matches(df_infer, model_dir)

    assert len(predictions) == 1
    assert "prob_home_win" in predictions[0]
    assert "prob_over25" in predictions[0]
