import os
import pandas as pd
from src.ml.train import train_and_save_models


def test_train_and_save_models(tmp_path):
    # Dummy data
    df = pd.DataFrame(
        {
            "xg_diff": [1.0, -0.5, 0.2, 2.5, -1.5, 0.0],
            "elo_diff": [100, -50, 20, 250, -150, 0],
            "target_1x2": [2, 0, 1, 2, 0, 1],
            "target_over25": [1, 0, 0, 1, 1, 0],
        }
    )

    model_dir = str(tmp_path)
    models = train_and_save_models(df, model_dir)

    assert "winner_model" in models
    assert "goals_model" in models
    assert os.path.exists(os.path.join(model_dir, "winner_model.joblib"))
    assert os.path.exists(os.path.join(model_dir, "goals_model.joblib"))
