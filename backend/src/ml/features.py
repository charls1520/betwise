import pandas as pd
import numpy as np

def build_features_for_matches(matches: list) -> pd.DataFrame:
    df = pd.DataFrame(matches)
    if df.empty:
        return df

    # Asegurar que Date sea datetime y ordenado
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.sort_values("Date").reset_index(drop=True)

    # Impute NaNs with forward fill per team, then global median
    for col in ['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo', 'home_xg', 'away_xg', 'home_elo', 'away_elo']:
        if col in df.columns:
            df[col] = df[col].ffill().fillna(df[col].median()).fillna(0)

    # We now expect 'Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo' instead of shots/corners
    if all(col in df.columns for col in ['Home_xG', 'Away_xG', 'Home_Elo', 'Away_Elo']):
        df["xg_diff"] = df["Home_xG"] - df["Away_xG"]
        df["elo_diff"] = df["Home_Elo"] - df["Away_Elo"]
    else:
        # Fallback for inference format
        if "home_xg" in df.columns and "away_xg" in df.columns:
            df["xg_diff"] = df["home_xg"] - df["away_xg"]
        if "home_elo" in df.columns and "away_elo" in df.columns:
            df["elo_diff"] = df["home_elo"] - df["away_elo"]

    # Transformacion de nuevas features si existe la fecha
    if "Date" in df.columns and "HomeTeam" in df.columns and "AwayTeam" in df.columns:
        # Crear un dataframe largo de equipos para calcular metricas historicas
        home_cols = ['Date', 'HomeTeam']
        if 'HST' in df.columns: home_cols.append('HST')
        if 'FTHG' in df.columns: home_cols.append('FTHG')
        if 'FTAG' in df.columns: home_cols.append('FTAG')
        
        home_df = df[home_cols].copy()
        home_df = home_df.rename(columns={'HomeTeam': 'Team', 'HST': 'ShotsOnTarget', 'FTHG': 'GoalsScored', 'FTAG': 'GoalsConceded'})
        home_df['is_home'] = True
        
        away_cols = ['Date', 'AwayTeam']
        if 'AST' in df.columns: away_cols.append('AST')
        if 'FTAG' in df.columns: away_cols.append('FTAG')
        if 'FTHG' in df.columns: away_cols.append('FTHG')
        
        away_df = df[away_cols].copy()
        away_df = away_df.rename(columns={'AwayTeam': 'Team', 'AST': 'ShotsOnTarget', 'FTAG': 'GoalsScored', 'FTHG': 'GoalsConceded'})
        away_df['is_home'] = False
        
        team_matches = pd.concat([home_df, away_df]).sort_values('Date').reset_index(drop=True)
        
        # Calcular fatiga (rest days) y capping a 10
        team_matches['prev_match_date'] = team_matches.groupby('Team')['Date'].shift(1)
        team_matches['rest_days'] = (team_matches['Date'] - team_matches['prev_match_date']).dt.days
        team_matches['rest_days'] = np.clip(team_matches['rest_days'], 0, 10)
        
        # Promedio movil de tiros a puerta (ultimos 5 partidos) con shift para evitar leakage
        if 'ShotsOnTarget' in team_matches.columns:
            team_matches['avg_shots_on_target_5'] = team_matches.groupby('Team')['ShotsOnTarget'].transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).mean())
        else:
            team_matches['avg_shots_on_target_5'] = 0

        if 'GoalsScored' in team_matches.columns and 'GoalsConceded' in team_matches.columns:
            team_matches['avg_goals_scored_general'] = team_matches.groupby('Team')['GoalsScored'].transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).mean())
            team_matches['avg_goals_conceded_general'] = team_matches.groupby('Team')['GoalsConceded'].transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).mean())
            
            team_matches['avg_goals_scored_home'] = team_matches[team_matches['is_home'] == True].groupby('Team')['GoalsScored'].transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).mean())
            team_matches['avg_goals_conceded_home'] = team_matches[team_matches['is_home'] == True].groupby('Team')['GoalsConceded'].transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).mean())
            
            team_matches['avg_goals_scored_away'] = team_matches[team_matches['is_home'] == False].groupby('Team')['GoalsScored'].transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).mean())
            team_matches['avg_goals_conceded_away'] = team_matches[team_matches['is_home'] == False].groupby('Team')['GoalsConceded'].transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).mean())
            
            team_matches['avg_goals_scored_home'] = team_matches.groupby('Team')['avg_goals_scored_home'].ffill()
            team_matches['avg_goals_conceded_home'] = team_matches.groupby('Team')['avg_goals_conceded_home'].ffill()
            team_matches['avg_goals_scored_away'] = team_matches.groupby('Team')['avg_goals_scored_away'].ffill()
            team_matches['avg_goals_conceded_away'] = team_matches.groupby('Team')['avg_goals_conceded_away'].ffill()
            
            for col in ['avg_goals_scored_general', 'avg_goals_conceded_general', 'avg_goals_scored_home', 'avg_goals_conceded_home', 'avg_goals_scored_away', 'avg_goals_conceded_away']:
                team_matches[col] = team_matches[col].fillna(0)
        else:
            for col in ['avg_goals_scored_general', 'avg_goals_conceded_general', 'avg_goals_scored_home', 'avg_goals_conceded_home', 'avg_goals_scored_away', 'avg_goals_conceded_away']:
                team_matches[col] = 0
        
        # Contexto temporada: Asumimos >30 partidos en el dataframe actual (simplificado)
        team_matches['matches_played'] = team_matches.groupby('Team').cumcount()
        team_matches['is_end_of_season_team'] = (team_matches['matches_played'] > 30).astype(int)
        
        # Mapear de vuelta al dataframe original
        # Separar en local y visitante
        stats_cols = ['Date', 'Team', 'rest_days', 'avg_shots_on_target_5', 'is_end_of_season_team',
                      'avg_goals_scored_general', 'avg_goals_conceded_general', 
                      'avg_goals_scored_home', 'avg_goals_conceded_home',
                      'avg_goals_scored_away', 'avg_goals_conceded_away']
        
        home_stats = team_matches[team_matches['is_home'] == True][stats_cols]
        away_stats = team_matches[team_matches['is_home'] == False][stats_cols]
        
        df = df.merge(home_stats, left_on=['Date', 'HomeTeam'], right_on=['Date', 'Team'], how='left')
        rename_home = {
            'rest_days': 'home_rest_days', 
            'avg_shots_on_target_5': 'home_avg_shots_on_target', 
            'is_end_of_season_team': 'home_end_of_season',
            'avg_goals_scored_general': 'home_avg_goals_scored_general',
            'avg_goals_conceded_general': 'home_avg_goals_conceded_general',
            'avg_goals_scored_home': 'home_avg_goals_scored_home',
            'avg_goals_conceded_home': 'home_avg_goals_conceded_home',
            'avg_goals_scored_away': 'home_avg_goals_scored_away',
            'avg_goals_conceded_away': 'home_avg_goals_conceded_away'
        }
        df = df.rename(columns=rename_home).drop(columns=['Team'])
        
        df = df.merge(away_stats, left_on=['Date', 'AwayTeam'], right_on=['Date', 'Team'], how='left')
        rename_away = {
            'rest_days': 'away_rest_days', 
            'avg_shots_on_target_5': 'away_avg_shots_on_target', 
            'is_end_of_season_team': 'away_end_of_season',
            'avg_goals_scored_general': 'away_avg_goals_scored_general',
            'avg_goals_conceded_general': 'away_avg_goals_conceded_general',
            'avg_goals_scored_home': 'away_avg_goals_scored_home',
            'avg_goals_conceded_home': 'away_avg_goals_conceded_home',
            'avg_goals_scored_away': 'away_avg_goals_scored_away',
            'avg_goals_conceded_away': 'away_avg_goals_conceded_away'
        }
        df = df.rename(columns=rename_away).drop(columns=['Team'])
        
        # Diferenciales
        df['rest_days_diff'] = df['home_rest_days'] - df['away_rest_days']
        df['shots_on_target_diff'] = df['home_avg_shots_on_target'] - df['away_avg_shots_on_target']
        df['is_end_of_season'] = (df['home_end_of_season'] | df['away_end_of_season']).astype(int)
        
        # Nuevos diferenciales de goles
        df['goals_scored_general_diff'] = df['home_avg_goals_scored_general'] - df['away_avg_goals_scored_general']
        df['goals_conceded_general_diff'] = df['home_avg_goals_conceded_general'] - df['away_avg_goals_conceded_general']
        
    else:
        # Fallbacks si no hay suficientes columnas
        for col in ['home_rest_days', 'away_rest_days', 'rest_days_diff', 'shots_on_target_diff', 'is_end_of_season']:
            if col not in df.columns:
                df[col] = 0

    # Target Variables
    if "FTR" in df.columns:
        df["target_1x2"] = df["FTR"].map({"H": 1, "D": 0, "A": 2})
    if "FTHG" in df.columns and "FTAG" in df.columns:
        df["target_over25"] = ((df["FTHG"] + df["FTAG"]) > 2.5).astype(int)

    return df
