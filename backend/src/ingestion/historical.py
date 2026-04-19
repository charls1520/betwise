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
    dfs = []
    
    # Map football-data seasons to understat years (e.g. "2324" -> "2023")
    season_to_year = {
        "2324": "2023",
        "2223": "2022",
        "2122": "2021"
    }

    for season in seasons:
        url = base_url.format(season)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            df = pd.read_csv(io.StringIO(response.text))
            
            df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
            
            # Fetch Understat
            year = season_to_year.get(season)
            df_understat = fetch_understat_historical_season(year)
            
            normalizer = TeamNormalizer(df_understat['Team'].unique().tolist() if not df_understat.empty else [])
            
            # Prepare Elo cache
            teams = pd.concat([df['HomeTeam'], df['AwayTeam']]).unique().tolist()
            elo_cache = {}
            for t in teams:
                norm_t = normalizer.normalize(t)
                if norm_t:
                    clubelo_name = norm_t.replace(" ", "")
                    elo_cache[t] = fetch_clubelo_history(clubelo_name)
            
            # Iterate and enrich
            enhanced_rows = []
            for _, row in df.iterrows():
                home = row['HomeTeam']
                away = row['AwayTeam']
                date = row['Date']
                
                norm_home = normalizer.normalize(home)
                norm_away = normalizer.normalize(away)
                
                # Default values
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
                
            dfs.append(pd.DataFrame(enhanced_rows))
        except Exception as e:
            print(f"Failed to download season {season}: {e}")

    if dfs:
        final_df = pd.concat(dfs, ignore_index=True)
        print("Final DF Before Dropna:")
        print(final_df[['HomeTeam', 'AwayTeam', 'Date', 'Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo']])
        return final_df.dropna(subset=['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo'])
    return pd.DataFrame()