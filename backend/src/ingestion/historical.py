import os
import pandas as pd
import requests
import io
import time
import random
import urllib3
from tenacity import retry, stop_after_attempt, wait_exponential
from src.utils.logger import get_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from src.ingestion.normalizer import TeamNormalizer
from src.ingestion.scrapers.understat_historical import fetch_understat_historical_season
from src.ingestion.scrapers.clubelo import fetch_clubelo_history

logger = get_logger()

def get_elo_for_date(df_elo: pd.DataFrame, target_date: pd.Timestamp) -> float:
    if df_elo.empty: return None
    mask = (df_elo['From'] <= target_date) & (df_elo['To'] >= target_date)
    res = df_elo[mask]
    if not res.empty:
        return res.iloc[0]['Elo']
    return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_with_retry(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    response = requests.get(url, headers=headers, timeout=15, verify=False)
    response.raise_for_status()
    return response.text

from src.ingestion.config import LEAGUES_CONFIG

def download_football_data_co_uk(seasons: list = ["2526", "2425", "2324", "2223", "2122"]) -> pd.DataFrame:
    base_url = "https://www.football-data.co.uk/mmz4281/{}/{}.csv"
    cache_dir = "data/historical"
    cache_file = os.path.join(cache_dir, "merged_history_cache.csv")
    
    os.makedirs(cache_dir, exist_ok=True)
    
    # 1. Load Cache
    cached_df = pd.DataFrame()
    if os.path.exists(cache_file):
        try:
            cached_df = pd.read_csv(cache_file)
            cached_df["Date"] = pd.to_datetime(cached_df["Date"])
        except Exception as e:
            logger.error(f"Failed to read cache: {e}")
            cached_df = pd.DataFrame()

    dfs_to_append = []
    
    season_to_year = {
        "2526": "2025",
        "2425": "2024",
        "2324": "2023",
        "2223": "2022",
        "2122": "2021",
        "2021": "2020",
        "1920": "2019"
    }

    for league in LEAGUES_CONFIG:
        fd_id = league["football_data_id"]
        und_id = league["understat_id"]
        logger.info(f"Processing Historical Data for {league['name']}...")
        
        for season in seasons:
            url = base_url.format(season, fd_id)
            try:
                # Random delay before fetching new season
                time.sleep(random.uniform(1.0, 3.0))
                
                csv_text = fetch_with_retry(url)
                df = pd.read_csv(io.StringIO(csv_text))
                df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
                df = df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam'])
                
                # Apply column whitelist
                whitelist_cols = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HST', 'AST', 'B365H', 'B365D', 'B365A']
                existing_whitelist = [col for col in whitelist_cols if col in df.columns]
                df = df[existing_whitelist].copy()
                
                # Find what we are missing
                if not cached_df.empty:
                    # Merge indicator to find left_only
                    merged = df.merge(cached_df[['Date', 'HomeTeam', 'AwayTeam']], on=['Date', 'HomeTeam', 'AwayTeam'], how='left', indicator=True)
                    missing_df = df[merged['_merge'] == 'left_only'].copy()
                else:
                    missing_df = df.copy()
                    
                if missing_df.empty:
                    logger.info(f"Season {season} is already fully cached. Skipping.")
                    continue
                    
                logger.info(f"Processing {len(missing_df)} new matches for season {season}...")
                
                # Fetch Understat
                year = season_to_year.get(season)
                df_understat = fetch_understat_historical_season(year, und_id)
                
                normalizer = TeamNormalizer(df_understat['Team'].unique().tolist() if not df_understat.empty else [])
                
                # Prepare Elo cache
                teams = pd.concat([missing_df['HomeTeam'], missing_df['AwayTeam']]).unique().tolist()
                elo_cache = {}
                import re
                for t in teams:
                    norm_t = normalizer.normalize(t)
                    if norm_t:
                        raw_clean = re.sub(r'[^a-zA-Z0-9]', '', t)
                        if 'Forest' in t: raw_clean = 'Forest'
                        elif 'Utd' in t: raw_clean = raw_clean.replace('Utd', 'United')
                        
                        df_elo = fetch_clubelo_history(raw_clean)
                        if df_elo.empty:
                            df_elo = fetch_clubelo_history(norm_t.replace(" ", ""))
                            
                        elo_cache[t] = df_elo
                        # Avoid hammering Clubelo
                        time.sleep(random.uniform(0.5, 1.5))
                
                # Iterate and enrich missing matches
                enhanced_rows = []
                for _, row in missing_df.iterrows():
                    home = row['HomeTeam']
                    away = row['AwayTeam']
                    date = row['Date']
                    
                    norm_home = normalizer.normalize(home)
                    norm_away = normalizer.normalize(away)
                    
                    h_xg, a_xg, h_elo, a_elo = None, None, None, None
                    
                    if not df_understat.empty and norm_home and norm_away:
                        h_cands = df_understat[(df_understat['Team'] == norm_home) & (df_understat['h_a'] == 'h')].copy()
                        a_cands = df_understat[(df_understat['Team'] == norm_away) & (df_understat['h_a'] == 'a')].copy()
                        
                        if not h_cands.empty:
                            h_cands['date_diff'] = (h_cands['Date'] - date).abs().dt.days
                            h_match = h_cands[h_cands['date_diff'] <= 3].sort_values('date_diff')
                            if not h_match.empty: h_xg = h_match.iloc[0]['xG']
                            
                        if not a_cands.empty:
                            a_cands['date_diff'] = (a_cands['Date'] - date).abs().dt.days
                            a_match = a_cands[a_cands['date_diff'] <= 3].sort_values('date_diff')
                            if not a_match.empty: a_xg = a_match.iloc[0]['xG']
                    
                    if home in elo_cache and elo_cache[home] is not None:
                        h_elo = get_elo_for_date(elo_cache[home], date)
                    if away in elo_cache and elo_cache[away] is not None:
                        a_elo = get_elo_for_date(elo_cache[away], date)
                    
                    row_dict = row.to_dict()
                    row_dict['Home_xG'] = h_xg
                    row_dict['Away_xG'] = a_xg
                    row_dict['Home_Elo'] = h_elo
                    row_dict['Away_Elo'] = a_elo
                    enhanced_rows.append(row_dict)
                    
                season_enhanced_df = pd.DataFrame(enhanced_rows)
                # Strict Anti-Void Filter (Drop Any row with None/NaN in features)
                valid_season_df = season_enhanced_df.dropna(subset=['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo'])
                
                logger.info(f"Successfully merged {len(valid_season_df)} out of {len(missing_df)} matches (Dropped {len(missing_df) - len(valid_season_df)} invalid matches).")
                if not valid_season_df.empty:
                    dfs_to_append.append(valid_season_df)
                    
            except Exception as e:
                logger.exception(f"Failed to download or process season {season} for {league['name']}: {e}")
                # We log the error but allow the loop to continue to the next season/league
                continue

    # Append to cache
    if dfs_to_append:
        new_data_df = pd.concat(dfs_to_append, ignore_index=True)
        final_df = pd.concat([cached_df, new_data_df], ignore_index=True)
        final_df.to_csv(cache_file, index=False)
        return final_df
    
    return cached_df