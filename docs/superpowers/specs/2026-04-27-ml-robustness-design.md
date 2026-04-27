# Diseño de Arquitectura para Robustez en Modelos de ML

## Contexto
Tras una auditoría exhaustiva del pipeline de Machine Learning (Ingestión e Inferencia) en `BetWise`, se identificaron cinco riesgos sistémicos ocultos que comprometen la precisión del modelo en producción. Estos errores comunes en predicción deportiva (Data Leakage, Cold Start, Desequilibrio de Clases, Caos de Zonas Horarias e Ignorar al Mercado) requieren una solución integral para elevar el sistema a un estándar profesional.

## Problemas Identificados y Soluciones

### 1. Solución al "Cold Start" (Equipos Ascendidos y Jornada 1)
- **Problema:** Los equipos nuevos sin historial en los últimos 5 partidos reciben estadísticas promedio (mediana global) o ceros, desvirtuando su rendimiento real (generalmente de equipos recién ascendidos).
- **Diseño Técnico:** 
  - Modificar `build_features_for_matches` en `src/ml/features.py`.
  - En lugar de rellenar los `NaN` de estadísticas (goles, tiros, eficiencia) con `0`, usar la media de los peores 6 equipos (tercil inferior) de la liga.
  - Para `Home_Elo` y `Away_Elo`, si un equipo no tiene historial, asignar un valor base de ascendido (ej. `1350`) en lugar de `1500`.

### 2. Corrección de Fatiga Falsa (Rest Days)
- **Problema:** En el primer partido de la temporada, la resta de fechas genera `NaN`. El código asume 0 días de descanso (fatiga máxima).
- **Diseño Técnico:** 
  - En `features.py`, al calcular `rest_days`, llenar los valores nulos (`NaN`) explícitamente con el límite máximo (`10` días), asumiendo que vienen de pretemporada o descanso prolongado.

### 3. Solución al Desequilibrio de Clases (Predicción de Empates)
- **Problema:** XGBoost (`XGBClassifier`) optimiza la precisión general (Accuracy), lo que lo lleva a casi nunca predecir empates (Draws) porque ocurren con menor frecuencia (~25%).
- **Diseño Técnico:**
  - Modificar `train_and_save_models` en `src/ml/train.py`.
  - Calcular los pesos de clase (Class Weights) usando la distribución real de `target_1x2` en el set de entrenamiento (usando `compute_sample_weight` de `sklearn.utils.class_weight`).
  - Pasar este array de pesos (`sample_weight`) al método `fit()` del `XGBClassifier` para penalizar fuertemente los errores al predecir empates.

### 4. Blindaje contra "Timezone Leakage" (Orden Cronológico)
- **Problema:** Mezclar fechas de CSV (`DD/MM/YYYY`) con fechas de The Odds API (`ISO 8601 UTC`) sin estandarizar zonas horarias rompe el orden de la función `.sort_values('Date')`, arruinando el cálculo de estadísticas previas `shift(1)`.
- **Diseño Técnico:**
  - En `features.py`, forzar la conversión de la columna `Date` a formato UTC absoluto (`utc=True`) antes de ordenar el DataFrame.

### 5. Inyección de "Inteligencia de Mercado" (Market Implied Diff)
- **Problema:** El modelo es ciego a la información externa (lesiones de última hora, clima, etc.) que las casas de apuestas ya incorporan en sus cuotas iniciales.
- **Diseño Técnico:**
  - **Histórico (`historical.py` / `features.py`):** Usar las cuotas de Bet365 (`B365H`, `B365D`, `B365A`) del CSV para calcular la probabilidad implícita (`1 / Cuota`).
  - **Inferencia (`inference.py`):** Usar las cuotas proporcionadas por The Odds API (ej. `home_odds` y `away_odds`).
  - **Nueva Feature:** Crear `market_implied_diff = (1 / home_odds) - (1 / away_odds)` y agregarla a la lista de `features` en el entrenamiento y la inferencia. Esto permite al modelo ajustar sus proyecciones matemáticas usando el consenso del mercado.

## Impacto Esperado
El modelo aumentará significativamente su capacidad para predecir empates, manejará correctamente la primera jornada de cada liga y aprovechará la inteligencia colectiva del mercado para corregir desviaciones en sus estadísticas crudas.

## Testing
- Se deberán actualizar los tests en `tests/ml/test_features.py` para verificar que `market_implied_diff` se calcula correctamente y que los `rest_days` de la jornada 1 son `10.0`.
- Se deberá actualizar `tests/ml/test_train.py` para asegurar que el pipeline entrena exitosamente con `sample_weight` y la nueva variable.