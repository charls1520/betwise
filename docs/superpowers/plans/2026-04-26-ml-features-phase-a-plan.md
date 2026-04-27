# ML Features Phase A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mejora el poder predictivo de los modelos de ML introduciendo variables de fatiga, estadísticas de tiro (tiros a puerta) y contexto de final de temporada (Fase A) utilizando solo los datos de football-data.co.uk.

**Architecture:** La transformación de datos ocurrirá "al vuelo" en `src/ml/features.py`. Para evitar fuga de datos (data leakage), se agrupará por equipo y se usarán ventanas móviles con `shift(1)`. Las nuevas variables se añadirán a la lista de `features` en `train.py` e `inference.py`.

**Tech Stack:** Python, Pandas, Scikit-Learn

---

### Task 1: Implementar lógica de extracción de nuevas variables en `features.py`

**Files:**
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ml\features.py`
- Test: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_features.py`

- [x] **Step 1: Write the failing test**

```python
import pandas as pd
from src.ml.features import build_features_for_matches

def test_new_ml_features():
    # Simulamos un dataset histórico de un equipo
    data = [
        {"Date": "2023-01-01", "HomeTeam": "TeamA", "AwayTeam": "TeamB", "FTHG": 1, "FTAG": 0, "HST": 5, "AST": 2, "Home_xG": 1.2, "Away_xG": 0.8, "Home_Elo": 1500, "Away_Elo": 1400},
        {"Date": "2023-01-05", "HomeTeam": "TeamC", "AwayTeam": "TeamA", "FTHG": 2, "FTAG": 1, "HST": 4, "AST": 3, "Home_xG": 1.5, "Away_xG": 1.0, "Home_Elo": 1450, "Away_Elo": 1505},
        # TeamA descansa 15 dias (se debe capear a 10)
        {"Date": "2023-01-20", "HomeTeam": "TeamA", "AwayTeam": "TeamD", "FTHG": 0, "FTAG": 0, "HST": 6, "AST": 4, "Home_xG": 1.4, "Away_xG": 1.1, "Home_Elo": 1500, "Away_Elo": 1350}
    ]
    
    # Creamos un DF con 30+ partidos para testear is_end_of_season
    for i in range(35):
        data.append({"Date": f"2023-02-{i%28+1:02d}", "HomeTeam": "TeamA", "AwayTeam": "TeamB", "FTHG": 1, "FTAG": 1, "HST": 2, "AST": 2, "Home_xG": 1.0, "Away_xG": 1.0, "Home_Elo": 1500, "Away_Elo": 1400})
        
    df = build_features_for_matches(data)
    
    assert "home_rest_days" in df.columns
    assert "away_rest_days" in df.columns
    assert "rest_days_diff" in df.columns
    assert "shots_on_target_diff" in df.columns
    assert "is_end_of_season" in df.columns
    
    # Verificamos que no haya leakage y el capping funcione
    # El partido del 2023-01-20 de TeamA fue 15 dias despues del 2023-01-05. El cap es 10.
    # En el index 2, TeamA es local. Su descanso deberia ser 10.
    assert df.loc[2, "home_rest_days"] == 10.0
    
    # El ultimo partido debe tener is_end_of_season en 1
    assert df.iloc[-1]["is_end_of_season"] == 1
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest "C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_features.py" -v`
Expected: FAIL due to missing columns or `KeyError`

- [x] **Step 3: Write minimal implementation**

```python
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
        home_df = df[['Date', 'HomeTeam', 'HST']].rename(columns={'HomeTeam': 'Team', 'HST': 'ShotsOnTarget'})
        home_df['is_home'] = True
        away_df = df[['Date', 'AwayTeam', 'AST']].rename(columns={'AwayTeam': 'Team', 'AST': 'ShotsOnTarget'})
        away_df['is_home'] = False
        
        team_matches = pd.concat([home_df, away_df]).sort_values('Date').reset_index(drop=True)
        
        # Calcular fatiga (rest days) y capping a 10
        team_matches['prev_match_date'] = team_matches.groupby('Team')['Date'].shift(1)
        team_matches['rest_days'] = (team_matches['Date'] - team_matches['prev_match_date']).dt.days
        team_matches['rest_days'] = np.clip(team_matches['rest_days'], 0, 10)
        
        # Promedio movil de tiros a puerta (ultimos 5 partidos) con shift para evitar leakage
        team_matches['avg_shots_on_target_5'] = team_matches.groupby('Team')['ShotsOnTarget'].transform(lambda x: x.shift(1).rolling(window=5, min_periods=1).mean())
        
        # Contexto temporada: Asumimos >30 partidos en el dataframe actual (simplificado)
        team_matches['matches_played'] = team_matches.groupby('Team').cumcount()
        team_matches['is_end_of_season_team'] = (team_matches['matches_played'] > 30).astype(int)
        
        # Mapear de vuelta al dataframe original
        # Separar en local y visitante
        home_stats = team_matches[team_matches['is_home'] == True][['Date', 'Team', 'rest_days', 'avg_shots_on_target_5', 'is_end_of_season_team']]
        away_stats = team_matches[team_matches['is_home'] == False][['Date', 'Team', 'rest_days', 'avg_shots_on_target_5', 'is_end_of_season_team']]
        
        df = df.merge(home_stats, left_on=['Date', 'HomeTeam'], right_on=['Date', 'Team'], how='left')
        df = df.rename(columns={'rest_days': 'home_rest_days', 'avg_shots_on_target_5': 'home_avg_shots_on_target', 'is_end_of_season_team': 'home_end_of_season'}).drop(columns=['Team'])
        
        df = df.merge(away_stats, left_on=['Date', 'AwayTeam'], right_on=['Date', 'Team'], how='left')
        df = df.rename(columns={'rest_days': 'away_rest_days', 'avg_shots_on_target_5': 'away_avg_shots_on_target', 'is_end_of_season_team': 'away_end_of_season'}).drop(columns=['Team'])
        
        # Diferenciales
        df['rest_days_diff'] = df['home_rest_days'] - df['away_rest_days']
        df['shots_on_target_diff'] = df['home_avg_shots_on_target'] - df['away_avg_shots_on_target']
        df['is_end_of_season'] = (df['home_end_of_season'] | df['away_end_of_season']).astype(int)
        
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
```

- [x] **Step 4: Run test to verify it passes**

Run: `pytest "C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_features.py" -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add "C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_features.py" "C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ml\features.py"
git commit -m "feat(ml): add phase A features (fatigue, shots, end of season)"
```

### Task 2: Actualizar la lista de features en `train.py`

**Files:**
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ml\train.py`

- [x] **Step 1: Verify current tests pass (Baseline)**

Run: `pytest "C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_train.py" -v`

- [x] **Step 2: Write minimal implementation**

Modify `features` variable inside `train_and_save_models` function:

```python
    features = ["xg_diff", "elo_diff", "rest_days_diff", "shots_on_target_diff", "is_end_of_season"]
```

- [x] **Step 3: Run test to verify it passes**

Run: `pytest "C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_train.py" -v`
Expected: PASS

- [x] **Step 4: Commit**

```bash
git add "C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ml\train.py"
git commit -m "feat(ml): include new phase A features in training pipeline"
```

### Task 3: Actualizar la lista de features y fallbacks en `inference.py`

**Files:**
- Modify: `C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ml\inference.py`

- [x] **Step 1: Write minimal implementation**

Modify `predict_matches` function to include new features:

```python
    features = ["xg_diff", "elo_diff", "rest_days_diff", "shots_on_target_diff", "is_end_of_season"]
    for col in features:
        if col not in df.columns:
            df[col] = 0
    X = df[features]
```

- [x] **Step 2: Run test to verify it passes**

Run: `pytest "C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\tests\ml\test_inference.py" -v`
Expected: PASS

- [x] **Step 3: Commit**

```bash
git add "C:\Users\Carlos Perez\Documents\deporte_project\BetWise\backend\src\ml\inference.py"
git commit -m "feat(ml): include new phase A features in inference pipeline"
```
