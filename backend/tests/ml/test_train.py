import os
import pandas as pd
from unittest.mock import patch
from src.ml.train import train_and_save_models

@patch("src.ml.train.accuracy_score", return_value=1.0)
def test_train_and_save_models(mock_acc, tmp_path):
    # Dummy data
    df = pd.DataFrame(
        {
            "xg_diff": [1.0, -0.5, 0.2, 2.5, -1.5, 0.0, 1.0, -0.5, 0.2, 2.5, -1.5, 0.0],
            "elo_diff": [100, -50, 20, 250, -150, 0, 100, -50, 20, 250, -150, 0],
            "target_1x2": [2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1],
            "target_over25": [1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0],
        }
    )

    model_dir = str(tmp_path)
    models = train_and_save_models(df, model_dir)

    assert "winner_model" in models
    assert "goals_model" in models
    assert os.path.exists(os.path.join(model_dir, "winner_model.joblib"))
    assert os.path.exists(os.path.join(model_dir, "goals_model.joblib"))

@patch("src.ml.train.accuracy_score", return_value=1.0)
def test_train_and_save_models_with_imputation(mock_acc, tmp_path):
    df = pd.DataFrame({
        "xg_diff": [1.0, -0.5, None, 2.0, 1.0, -0.5, None, 2.0, 1.0, -0.5],
        "elo_diff": [100, -50, 20, None, 100, -50, 20, None, 100, -50],
        "target_1x2": [1, 2, 0, 1, 1, 2, 0, 1, 1, 2],
        "target_over25": [1, 0, 1, 1, 0, 1, 0, 1, 1, 0]
    })
    
    # Train should handle NaNs by dropping or imputing internally
    models = train_and_save_models(df, model_dir=str(tmp_path))
    assert "winner_model" in models
    assert "goals_model" in models
