import csv
import io
import requests
import datetime
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from src.ingestion.validators import EloScore, validate_volume
from src.ingestion.normalizer import TeamNormalizer
from src.utils.logger import get_logger

logger = get_logger()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _fetch_clubelo_with_retry(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text

def fetch_clubelo_stats() -> List[dict]:
    today = datetime.date.today().strftime('%Y-%m-%d')
    url = f"http://api.clubelo.com/{today}"
    
    try:
        csv_data = _fetch_clubelo_with_retry(url)
    except Exception as e:
        logger.error(f"Clubelo fetch error: {e}")
        return []
        
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
    
    url = f"http://api.clubelo.com/{club_name}"
    try:
        csv_data = _fetch_clubelo_with_retry(url)
        df = pd.read_csv(io.StringIO(csv_data))
        if 'Elo' in df.columns and 'From' in df.columns and 'To' in df.columns:
            df['From'] = pd.to_datetime(df['From'])
            df['To'] = pd.to_datetime(df['To'])
            return df
    except Exception as e:
        logger.error(f"Clubelo history error for {club_name}: {e}")
        
    return pd.DataFrame()

def fetch_clubelo_bulk_history(date_str: str):
    """
    Downloads the entire global Elo list for a specific date.
    Date must be YYYY-MM-DD.
    """
    import pandas as pd
    url = f"http://api.clubelo.com/{date_str}"
    try:
        csv_data = _fetch_clubelo_with_retry(url)
        df = pd.read_csv(io.StringIO(csv_data))
        if 'Elo' in df.columns and 'Club' in df.columns:
            return df
    except Exception as e:
        logger.error(f"Clubelo bulk history error for {date_str}: {e}")
        
    return pd.DataFrame()