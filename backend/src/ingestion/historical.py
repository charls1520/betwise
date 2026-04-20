import os
import pandas as pd
import requests
import io
from src.ingestion.normalizer import TeamNormalizer
from src.ingestion.scrapers.understat_historical import fetch_understat_historical_season
from src.ingestion.scrapers.clubelo import fetch_clubelo_history

def get_elo_for_date(df_elo: pd.DataFrame, target_date: pd.Timestamp) -> float:
    if df_elo.empty: return None
    mask = (df_elo['From'] <= target_date) & (df_elo['To'] >= target_date)
    res = df_elo[mask]
    if not res.empty:
        return res.iloc[0]['Elo']
    return None

def download_football_data_co_uk(seasons: list = ["2324", "2223", "2122"]) -> pd.DataFrame:
    base_url = "https://www.football-data.co.uk/mmz4281/{}/E0.csv"
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
            print(f"Failed to read cache: {e}")
            cached_df = pd.DataFrame()

    dfs_to_append = []
    
    season_to_year = {
        "2324": "2023",
        "2223": "2022",
        "2122": "2021",
        "2021": "2020",
        "1920": "2019"
    }

    for season in seasons:
        url = base_url.format(season)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            df = pd.read_csv(io.StringIO(response.text))
            df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
            df = df.dropna(subset=['Date', 'HomeTeam', 'AwayTeam'])
            
            # Find what we are missing
            if not cached_df.empty:
                # Merge indicator to find left_only
                merged = df.merge(cached_df[['Date', 'HomeTeam', 'AwayTeam']], on=['Date', 'HomeTeam', 'AwayTeam'], how='left', indicator=True)
                missing_df = df[merged['_merge'] == 'left_only'].copy()
            else:
                missing_df = df.copy()
                
            if missing_df.empty:
                print(f"Season {season} is already fully cached. Skipping.")
                continue
                
            print(f"Processing {len(missing_df)} new matches for season {season}...")
            
            # Fetch Understat
            year = season_to_year.get(season)
            df_understat = fetch_understat_historical_season(year)
            
            normalizer = TeamNormalizer(df_understat['Team'].unique().tolist() if not df_understat.empty else [])
            
            # Prepare Elo cache
            teams = pd.concat([missing_df['HomeTeam'], missing_df['AwayTeam']]).unique().tolist()
            elo_cache = {}
            for t in teams:
                norm_t = normalizer.normalize(t)
                if norm_t:
                    clubelo_name = norm_t.replace(" ", "")
                    elo_cache[t] = fetch_clubelo_history(clubelo_name)
            
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
                    h_xg_row = df_understat[(df_understat['Team'] == norm_home) & (df_understat['Date'] == date)]
                    a_xg_row = df_understat[(df_understat['Team'] == norm_away) & (df_understat['Date'] == date)]
                    if not h_xg_row.empty: h_xg = h_xg_row.iloc[0]['xG']
                    if not a_xg_row.empty: a_xg = a_xg_row.iloc[0]['xG']
                
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
            
            print(f"Successfully merged {len(valid_season_df)} out of {len(missing_df)} matches (Dropped {len(missing_df) - len(valid_season_df)} invalid matches).")
            if not valid_season_df.empty:
                dfs_to_append.append(valid_season_df)
                
        except Exception as e:
            print(f"Failed to download or process season {season}: {e}")

    # Append to cache
    if dfs_to_append:
        new_data_df = pd.concat(dfs_to_append, ignore_index=True)
        final_df = pd.concat([cached_df, new_data_df], ignore_index=True)
        final_df.to_csv(cache_file, index=False)
        return final_df
    
    return cached_df