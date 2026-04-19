import csv
import io
import requests
import datetime
from typing import List
from src.ingestion.validators import EloScore, validate_volume
from src.ingestion.normalizer import TeamNormalizer

def fetch_clubelo_stats() -> List[dict]:
    today = datetime.date.today().strftime('%Y-%m-%d')
    url = f"http://api.clubelo.com/{today}"
    response = requests.get(url)
    if response.status_code != 200:
        return []
    
    csv_data = response.text
    reader = csv.DictReader(io.StringIO(csv_data))
    
    valid_scores = []
    for row in reader:
        try:
            # Pydantic validation
            score = EloScore(
                team=row.get('Club', ''),
                elo=float(row.get('Elo', 0)),
                date=row.get('To', '')
            )
            valid_scores.append(score.model_dump() if hasattr(score, 'model_dump') else score.dict())
        except Exception:
            continue
            
    if not validate_volume(len(valid_scores), 10):
        return []
        
    return valid_scores

def fetch_clubelo_history(club_name: str):
    """Fetches the entire Elo history for a specific club."""
    import pandas as pd
    import requests
    import io
    
    url = f"http://api.clubelo.com/{club_name}"
    response = requests.get(url)
    if response.status_code != 200:
        return pd.DataFrame()
        
    df = pd.read_csv(io.StringIO(response.text))
    if 'Elo' in df.columns and 'From' in df.columns and 'To' in df.columns:
        df['From'] = pd.to_datetime(df['From'])
        df['To'] = pd.to_datetime(df['To'])
        return df
    return pd.DataFrame()