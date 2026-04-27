# Diseño de Limpieza Quirúrgica de Datos (Data Cleaning)

## Contexto
El proyecto BetWise actualmente descarga, procesa y almacena grandes volúmenes de datos históricos (CSVs de `football-data.co.uk`) y características temporales generadas en tiempo de ejecución. Gran parte de esta información consiste en columnas irrelevantes para XGBoost (como árbitros, tarjetas, cuotas de casas obsoletas) o columnas intermedias usadas solo para calcular diferenciales. Además, algunos reemplazos de datos faltantes con `0` generan ruido estadístico.

## Objetivos
1. **Reducir consumo de disco y memoria:** Eliminar columnas basura desde el momento de la ingesta.
2. **Optimizar Inferencia:** Evitar el transporte de columnas temporales o en desuso hasta el paso de predicción del modelo.
3. **Mejorar Calidad de Datos:** Permitir que XGBoost maneje `NaNs` de forma nativa en lugar de inyectar ceros artificiales que rompen la lógica del árbol de decisión.

## Diseño de la Solución

### 1. Filtrado Estricto (Whitelist) en Ingesta Histórica
- **Archivo:** `src/ingestion/historical.py`
- **Cambio:** Al descargar y procesar cada CSV de temporada, aplicar un filtro de columnas. Solo se retendrán las columnas estrictamente necesarias antes de guardar el DataFrame en `merged_history_cache.csv`.
- **Columnas permitidas:** `Date`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`, `FTR`, `HST`, `AST`, `B365H`, `B365D`, `B365A` (y las columnas enriquecidas `Home_xG`, `Away_xG`, `Home_Elo`, `Away_Elo`).
- **Impacto:** El archivo de caché histórico reducirá su peso dramáticamente.

### 2. Purgado de Características Temporales y Obsoletas
- **Archivo:** `src/ml/features.py`
- **Cambio:**
  - Eliminar el cálculo de la variable `target_over25`, ya que el nuevo enfoque de modelos independientes de goles de Poisson lo ha vuelto obsoleto.
  - Al final de la función `build_features_for_matches`, implementar un bloque de limpieza explícito (`df.drop(columns=[...])`) para borrar todas las métricas base (ej. `home_rest_days`, `away_rest_days`, `home_avg_goals_scored_general`, etc.) una vez que se han calculado los diferenciales finales (`rest_days_diff`, `goals_scored_general_diff`, etc.).

### 3. Prevención de "Ceros" Artificiales
- **Archivo:** `src/ml/features.py`
- **Cambio:** 
  - En la sección final donde se calculan los fallbacks para columnas faltantes, en lugar de llenar con `0`, se dejará como `np.nan`.
  - XGBoost tiene soporte nativo para `Missing Values`. Al dejar un `NaN` verdadero en lugar de un `0` (especialmente en estadísticas donde un 0 absoluto es irreal, como eficiencias o elos base), el modelo aprenderá a enviar esas muestras por la rama correcta del árbol sin alterar la estadística de los que sí tienen datos de valor 0 real.

## Testing
- Actualizar `tests/ml/test_features.py` para asegurar que las columnas eliminadas (ej. `target_over25` y columnas base `home_*`) ya no existen en el DataFrame final.
- Ejecutar el pipeline de ingesta histórico (`historical.py`) para confirmar que el caché solo contiene el "Whitelist" de columnas definido.