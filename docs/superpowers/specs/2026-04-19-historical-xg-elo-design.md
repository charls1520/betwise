# Design Spec: Ingesta Histórica de xG y Elo para Entrenamiento de ML

## Contexto
El modelo de Machine Learning actual se entrena usando el historial oficial de resultados y estadísticas (tiros, córners) provenientes de `football-data.co.uk`. Sin embargo, durante la inferencia en vivo (Dashboard), el modelo evalúa usando Goles Esperados (xG) de `Understat` y el `Elo Rating` de `Clubelo`. Esta diferencia (entrenar con tiros, predecir con xG) limita la capacidad predictiva del modelo.
Se requiere actualizar el proceso de entrenamiento histórico para que también consuma y utilice datos pasados de xG y Elo.

## Objetivos
1. **Scraping Histórico:** Descargar el historial de partidos de Clubelo (Elo histórico por fecha) y Understat (xG histórico por partido).
2. **Cruce de Datos (Merge):** Unir los datos oficiales de `football-data.co.uk` con el xG de Understat y el Elo de Clubelo usando la fecha del partido y el normalizador de equipos (`TeamNormalizer`).
3. **Reemplazo de Features:** Entrenar el modelo de Machine Learning usando `xg_diff` y `elo_diff` históricos en lugar de proxies menos precisos como la diferencia de tiros o córners.

## Arquitectura de Entrenamiento Histórico

### 1. Extracción de xG Histórico (Understat)
- Se creará un scraper histórico en `src/ingestion/historical.py` o extendiendo `understat.py` para descargar el resumen de temporadas pasadas de Understat.
- Esto nos proporcionará el `xG_for` y `xG_against` de cada equipo a lo largo de las temporadas (ej. 2019 a 2024). Alternativamente, se usará el xG promedio histórico si el partido por partido es inaccesible, pero se priorizará el xG real del partido.

### 2. Extracción de Elo Histórico (Clubelo)
- Se utilizará la API de Clubelo (`http://api.clubelo.com/<date>`) de manera iterativa o se descargará el dump completo por club (`http://api.clubelo.com/<Club>`) para tener el historial del Elo Rating de cada equipo en cualquier fecha pasada.

### 3. Pipeline de Cruce (Merge)
- Se descargará el CSV base de `football-data.co.uk` con los resultados oficiales (Goles locales y visitantes).
- Por cada fila (partido), se buscará el `Elo` del equipo Local y Visitante para esa `Date` exacta usando Clubelo.
- Se buscará el `xG` generado por el equipo Local y Visitante en esa misma fecha o partido usando los datos históricos de Understat.
- **Normalización:** Se aplicará `TeamNormalizer` (con umbral > 95) para alinear nombres como "Man Utd" con "Manchester United".

### 4. Feature Engineering & ML
- En `src/ml/features.py`, se modificarán las lógicas para depender de:
  - `home_xg` y `away_xg` (Históricos) -> `xg_diff`
  - `home_elo` y `away_elo` (Históricos) -> `elo_diff`
- Se eliminarán o depreciarán las métricas basadas únicamente en `HST` (Home Shots on Target) y `HC` (Home Corners) si el modelo prueba ser superior solo con xG y Elo.

## Componentes a Modificar / Crear
- `src/ingestion/historical.py`: Añadir la descarga de históricos de Understat y Clubelo, y el código de *merge* basado en Pandas.
- `src/ml/features.py`: Ajustar las features usadas durante el entrenamiento.
- `src/ml/train.py`: Ejecutar el nuevo pipeline de descarga completa antes de entrenar el `RandomForestClassifier`.

## Manejo de Errores y Calidad de Datos
- **Missing Data:** Si un partido antiguo no tiene datos de xG (ej. temporada muy lejana) o Elo, la fila será descartada (`dropna()`) para garantizar que el modelo solo se entrene con registros perfectos.
- **Normalización Estricta:** Si no hay un *match* de nombres claro, el partido se ignora para no introducir ruido.