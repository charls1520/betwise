# Especificación de Diseño: Inferencia con Contexto Histórico (Fusión al Vuelo)

**Fecha:** 26 de Abril de 2026
**Contexto Tecnológico:** Python, Pandas, Scikit-Learn, XGBoost
**Módulos Afectados:** `src/ml/inference.py`

---

## 1. Overview / Objetivo
Resolver el problema de falta de contexto histórico (Data Leakage inverso) durante la inferencia en vivo. Actualmente, cuando se predicen partidos futuros, las nuevas variables complejas (Fatiga, Tiros a Puerta, Eficacia Ofensiva/Defensiva basadas en promedios móviles) se evalúan como cero (`0`) debido a que el modelo solo recibe los datos del partido futuro sin su historial previo.
El objetivo es inyectar el historial reciente de los equipos "al vuelo" antes de generar las características (features) y realizar la predicción.

## 2. Arquitectura y Flujo de Datos (Fusión al Vuelo)
Se adoptará el enfoque de "Fusión al Vuelo" (Opción A). El flujo dentro de la función `predict_matches` en `src/ml/inference.py` se modificará de la siguiente manera:

1. **Carga del Historial:** Al inicio de la inferencia, se leerá el archivo de caché histórico completo (`data/historical/merged_history_cache.csv`), el cual ya es generado y actualizado semanalmente por el pipeline de entrenamiento.
2. **Preparación de Partidos Futuros:** Los `raw_matches` entrantes (usualmente provenientes de `The-Odds-API` y ya normalizados) se convertirán en un DataFrame. Para asegurar que la fusión sea limpia, se garantizará que las columnas clave coincidan (ej. `HomeTeam`, `AwayTeam`, `Date`).
3. **Concatenación:** El DataFrame de partidos futuros se concatenará **al final** del DataFrame histórico.
4. **Cálculo de Features:** Se llamará a la función `build_features_for_matches` pasando el DataFrame combinado. Gracias al ordenamiento cronológico por fecha (`Date`), las funciones `.shift(1)` y `.rolling(5)` en `features.py` tomarán los últimos 5 partidos reales del historial para calcular correctamente la fatiga y las eficacias del partido futuro.
5. **Filtrado:** Una vez que el DataFrame gigante tenga todas las features calculadas, se filtrará para conservar **únicamente** las filas correspondientes a los partidos futuros (los originales solicitados para inferencia).
6. **Predicción:** Se utilizarán los modelos entrenados (`winner_clf`, `home_goals_clf`, `away_goals_clf`) sobre este subconjunto filtrado para generar las probabilidades y expectativas de goles finales.

## 3. Manejo de Nombres de Equipos (Team Normalization)
Es vital que los nombres de los equipos en `raw_matches` coincidan exactamente con los nombres en el archivo histórico. Se asume que el flujo actual de ingesta (`tasks.py` / `odds_api.py`) ya aplica el `TeamNormalizer`. De ser necesario, se agregará una capa de normalización de seguridad antes de la fusión para asegurar que el agrupamiento (`groupby('Team')`) en `features.py` no se rompa por diferencias de sintaxis (ej. "Arsenal FC" vs "Arsenal").

## 4. Consideraciones de Rendimiento
La lectura del CSV histórico y las operaciones vectorizadas de Pandas sobre un dataset de unos pocos megabytes (10-20 MB) tomarán un tiempo estimado de procesamiento inferior a 1-2 segundos. Este impacto en la latencia de la inferencia es despreciable en comparación con la mejora crítica en la precisión y coherencia de las predicciones de los modelos de XGBoost y Random Forest.