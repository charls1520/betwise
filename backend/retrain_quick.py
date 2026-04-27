import pandas as pd
from src.ml.train import train_and_save_models
from src.ml.features import build_features_for_matches

df = pd.read_csv("data/historical/merged_history_cache.csv")
df_features = build_features_for_matches(df.to_dict("records"))
train_and_save_models(df_features, "models")
print("Models retrained successfully.")
