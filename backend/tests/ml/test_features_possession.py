import pandas as pd
from src.ml.features import add_rolling_possession

def test_add_rolling_possession():
    df = pd.DataFrame({
        'team_id': [1, 1, 1],
        'possession_percentage': [50.0, 60.0, 55.0]
    })
    
    result = add_rolling_possession(df, window=2)
    assert 'rolling_possession_2' in result.columns
    # (50+60)/2 = 55.0 for the second match
    assert result.iloc[1]['rolling_possession_2'] == 55.0