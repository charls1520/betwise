import pandas as pd
import numpy as np

def build_features_for_matches(matches: list) -> pd.DataFrame:
    df = pd.DataFrame(matches)
    if df.empty:
        return df

    # Asegurar que Date sea datetime y ordenado (UTC)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True)
        df = df.sort_values("Date").reset_index(drop=True)

    # Impute NaNs for Elo with forward fill PER TEAM
    if "HomeTeam" in df.columns and "AwayTeam" in df.columns:
        # Create mapping of last known Elo per team
        # We assume the dataframe is already sorted by Date
        last_elo = {}
        home_elo_col = 'Home_Elo' if 'Home_Elo' in df.columns else 'home_elo' if 'home_elo' in df.columns else None
        away_elo_col = 'Away_Elo' if 'Away_Elo' in df.columns else 'away_elo' if 'away_elo' in df.columns else None
        
        if home_elo_col and away_elo_col:
            # Cold start for Elo is 1350 for newly promoted/unknown teams
            global_median_elo = 1350.0
            
            home_elos_imputed = []
            away_elos_imputed = []
            
            for idx, row in df.iterrows():
                h_team = row['HomeTeam']
                a_team = row['AwayTeam']
                
                h_elo = row[home_elo_col]
                a_elo = row[away_elo_col]
                
                if pd.notna(h_elo) and h_elo != 0:
                    last_elo[h_team] = h_elo
                elif h_team in last_elo:
                    h_elo = last_elo[h_team]
                else:
                    h_elo = global_median_elo
                    
                if pd.notna(a_elo) and a_elo != 0:
                    last_elo[a_team] = a_elo
                elif a_team in last_elo:
                    a_elo = last_elo[a_team]
                else:
                    a_elo = global_median_elo
                    
                home_elos_imputed.append(h_elo)
                away_elos_imputed.append(a_elo)
                
            df['Home_Elo'] = home_elos_imputed
            df['Away_Elo'] = away_elos_imputed
            df['elo_diff'] = df['Home_Elo'] - df['Away_Elo']

    # Transformacion de nuevas features si existe la fecha
    if "Date" in df.columns and "HomeTeam" in df.columns and "AwayTeam" in df.columns:
        # Crear un dataframe largo de equipos para calcular metricas historicas
        home_cols = ['Date', 'HomeTeam']
        if 'HST' in df.columns: home_cols.append('HST')
        if 'FTHG' in df.columns: home_cols.append('FTHG')
        if 'FTAG' in df.columns: home_cols.append('FTAG')
        if 'Home_xG' in df.columns: home_cols.append('Home_xG')
        if 'Away_xG' in df.columns: home_cols.append('Away_xG')
        
        home_df = df[home_cols].copy()
        home_df = home_df.rename(columns={'HomeTeam': 'Team', 'HST': 'ShotsOnTarget', 'FTHG': 'GoalsScored', 'FTAG': 'GoalsConceded', 'Home_xG': 'xG_Scored', 'Away_xG': 'xG_Conceded'})
        home_df['is_home'] = True
        
        away_cols = ['Date', 'AwayTeam']
        if 'AST' in df.columns: away_cols.append('AST')
        if 'FTAG' in df.columns: away_cols.append('FTAG')
        if 'FTHG' in df.columns: away_cols.append('FTHG')
        if 'Away_xG' in df.columns: away_cols.append('Away_xG')
        if 'Home_xG' in df.columns: away_cols.append('Home_xG')
        
        away_df = df[away_cols].copy()
        away_df = away_df.rename(columns={'AwayTeam': 'Team', 'AST': 'ShotsOnTarget', 'FTAG': 'GoalsScored', 'FTHG': 'GoalsConceded', 'Away_xG': 'xG_Scored', 'Home_xG': 'xG_Conceded'})
        away_df['is_home'] = False
        
        team_matches = pd.concat([home_df, away_df]).sort_values('Date').reset_index(drop=True)
        
        # Calcular fatiga (rest days) y capping a 10
        team_matches['prev_match_date'] = team_matches.groupby('Team')['Date'].shift(1)
        team_matches['rest_days'] = (team_matches['Date'] - team_matches['prev_match_date']).dt.days
        # Llenar NaNs (primer partido) con 10 días de descanso
        team_matches['rest_days'] = team_matches['rest_days'].fillna(10)
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
            
            if 'xG_Scored' in team_matches.columns and 'xG_Conceded' in team_matches.columns:
                team_matches['Offensive_Efficiency'] = team_matches['GoalsScored'] - team_matches['xG_Scored']
                team_matches['Defensive_Efficiency'] = team_matches['GoalsConceded'] - team_matches['xG_Conceded']
                team_matches['avg_offensive_efficiency'] = team_matches.groupby('Team')['Offensive_Efficiency'].transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).mean())
                team_matches['avg_defensive_efficiency'] = team_matches.groupby('Team')['Defensive_Efficiency'].transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).mean())
            else:
                team_matches['avg_offensive_efficiency'] = 0
                team_matches['avg_defensive_efficiency'] = 0
            
            team_matches['avg_goals_scored_home'] = team_matches.groupby('Team')['avg_goals_scored_home'].ffill()
            team_matches['avg_goals_conceded_home'] = team_matches.groupby('Team')['avg_goals_conceded_home'].ffill()
            team_matches['avg_goals_scored_away'] = team_matches.groupby('Team')['avg_goals_scored_away'].ffill()
            team_matches['avg_goals_conceded_away'] = team_matches.groupby('Team')['avg_goals_conceded_away'].ffill()
            
            for col in ['avg_goals_scored_general', 'avg_goals_conceded_general', 'avg_goals_scored_home', 'avg_goals_conceded_home', 'avg_goals_scored_away', 'avg_goals_conceded_away', 'avg_offensive_efficiency', 'avg_defensive_efficiency']:
                team_matches[col] = team_matches[col].fillna(0)
        else:
            for col in ['avg_goals_scored_general', 'avg_goals_conceded_general', 'avg_goals_scored_home', 'avg_goals_conceded_home', 'avg_goals_scored_away', 'avg_goals_conceded_away', 'avg_offensive_efficiency', 'avg_defensive_efficiency']:
                team_matches[col] = 0
        
        # Contexto temporada: Asumimos >30 partidos en el dataframe actual (simplificado)
        team_matches['matches_played'] = team_matches.groupby('Team').cumcount()
        team_matches['is_end_of_season_team'] = (team_matches['matches_played'] > 30).astype(int)
        
        # Mapear de vuelta al dataframe original
        # Separar en local y visitante
        stats_cols = ['Date', 'Team', 'rest_days', 'avg_shots_on_target_5', 'is_end_of_season_team',
                      'avg_goals_scored_general', 'avg_goals_conceded_general', 
                      'avg_goals_scored_home', 'avg_goals_conceded_home',
                      'avg_goals_scored_away', 'avg_goals_conceded_away',
                      'avg_offensive_efficiency', 'avg_defensive_efficiency']
        
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
            'avg_goals_conceded_away': 'home_avg_goals_conceded_away',
            'avg_offensive_efficiency': 'home_offensive_efficiency',
            'avg_defensive_efficiency': 'home_defensive_efficiency'
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
            'avg_goals_conceded_away': 'away_avg_goals_conceded_away',
            'avg_offensive_efficiency': 'away_offensive_efficiency',
            'avg_defensive_efficiency': 'away_defensive_efficiency'
        }
        df = df.rename(columns=rename_away).drop(columns=['Team'])
        
        # Diferenciales
        df['rest_days_diff'] = df['home_rest_days'] - df['away_rest_days']
        df['shots_on_target_diff'] = df['home_avg_shots_on_target'] - df['away_avg_shots_on_target']
        df['is_end_of_season'] = (df['home_end_of_season'] | df['away_end_of_season']).astype(int)
        
        # Nuevos diferenciales de goles
        df['goals_scored_general_diff'] = df['home_avg_goals_scored_general'] - df['away_avg_goals_scored_general']
        df['goals_conceded_general_diff'] = df['home_avg_goals_conceded_general'] - df['away_avg_goals_conceded_general']
        
        df['offensive_efficiency_diff'] = df['home_offensive_efficiency'] - df['away_offensive_efficiency']
        df['defensive_efficiency_diff'] = df['home_defensive_efficiency'] - df['away_defensive_efficiency']
        
    else:
        # Fallbacks si no hay suficientes columnas
        for col in ['home_rest_days', 'away_rest_days', 'rest_days_diff', 'shots_on_target_diff', 'is_end_of_season', 'offensive_efficiency_diff', 'defensive_efficiency_diff']:
            if col not in df.columns:
                df[col] = 0

    # Target Variables
    if "FTR" in df.columns:
        df["target_1x2"] = df["FTR"].map({"H": 1, "D": 0, "A": 2})

    # Market Intelligence (Implied Probabilities Diff)
    # Historic uses B365H/A, Inference uses home_odds/away_odds
    home_odds_col = 'B365H' if 'B365H' in df.columns else 'home_odds' if 'home_odds' in df.columns else None
    away_odds_col = 'B365A' if 'B365A' in df.columns else 'away_odds' if 'away_odds' in df.columns else None
    
    if home_odds_col and away_odds_col:
        # Convert odds to probability (1/odds)
        df['home_implied_prob'] = 1 / pd.to_numeric(df[home_odds_col], errors='coerce')
        df['away_implied_prob'] = 1 / pd.to_numeric(df[away_odds_col], errors='coerce')
        df['market_implied_diff'] = df['home_implied_prob'] - df['away_implied_prob']
        # Fill NaNs with 0 (assuming even odds if missing)
        df['market_implied_diff'] = df['market_implied_diff'].fillna(0)
    else:
        df['market_implied_diff'] = 0

    # Drop intermediate and unneeded base columns
    cols_to_drop = [
        'home_rest_days', 'away_rest_days',
        'home_avg_shots_on_target', 'away_avg_shots_on_target',
        'home_end_of_season', 'away_end_of_season',
        'home_avg_goals_scored_general', 'away_avg_goals_scored_general',
        'home_avg_goals_conceded_general', 'away_avg_goals_conceded_general',
        'home_avg_goals_scored_home', 'away_avg_goals_scored_home',
        'home_avg_goals_conceded_home', 'away_avg_goals_conceded_home',
        'home_avg_goals_scored_away', 'away_avg_goals_scored_away',
        'home_avg_goals_conceded_away', 'away_avg_goals_conceded_away',
        'home_offensive_efficiency', 'away_offensive_efficiency',
        'home_defensive_efficiency', 'away_defensive_efficiency',
        'home_implied_prob', 'away_implied_prob'
    ]
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')

    return df
