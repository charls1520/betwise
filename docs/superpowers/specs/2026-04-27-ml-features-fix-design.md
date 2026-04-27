# Corrección de Data Leakage y Contaminación Cruzada en Features ML

## Contexto
Durante la auditoría del modelo de Machine Learning, se identificaron dos problemas críticos que estaban destruyendo las predicciones en producción (evidenciado en pronósticos totalmente desviados como el partido Cagliari vs Atalanta):
1. **Data Leakage:** El modelo estaba usando la variable `xg_diff` (basada en `Home_xG` y `Away_xG` del mismo partido) para entrenar. En producción, como el partido no ha ocurrido, esto se llenaba con basura, rompiendo la inferencia.
2. **Contaminación Cruzada:** En la fase de inferencia, la imputación de valores faltantes (`ffill()`) se hacía de forma global sobre el DataFrame en lugar de agrupar por equipo. Esto causaba que los equipos "heredaran" el Elo y estadísticas del último partido procesado en el CSV, sin importar quiénes jugaban.

## Diseño de la Solución

### 1. Eliminación del Data Leakage (Remoción de xg_diff)
- **Acción:** Se eliminará el cálculo y uso de la variable `xg_diff` en el pipeline de ML.
- **Justificación:** Previene que el modelo "haga trampa" usando datos del partido actual. En su lugar, el modelo dependerá de `offensive_efficiency_diff` y `defensive_efficiency_diff`, las cuales son métricas derivadas calculadas correctamente usando un promedio móvil (`shift(1)`) de los últimos 5 partidos, asegurando que solo se usa información pasada.
- **Archivos Afectados:**
  - `src/ml/features.py`: Eliminar lógica de `xg_diff`.
  - `src/ml/train.py`: Remover `xg_diff` de la lista de features.
  - `src/ml/inference.py`: Remover `xg_diff` de la lista de features.

### 2. Corrección del Rellenado de Datos (Imputación por Equipo)
- **Acción:** Modificar la lógica de imputación de `Home_Elo` y `Away_Elo` en `src/ml/features.py`.
- **Lógica:** En lugar de un `df.ffill()` global, el sistema debe obtener el último Elo real registrado para cada equipo antes de la fecha del partido a predecir. Si un equipo es completamente nuevo en el dataset, se le asignará la mediana global de Elo.
- **Archivos Afectados:**
  - `src/ml/features.py`: Reescribir la lógica de imputación de Elo al inicio de la función `build_features_for_matches` para usar agrupaciones por equipo (`groupby('Team')` o un mapeo directo del último valor conocido en el dataframe expandido de equipos).

## Impacto y Entrenamiento
Al eliminar `xg_diff`, las variables relacionadas al Elo, tiros a puerta y eficiencias (ofensiva/defensiva) tomarán más peso en el modelo. Tras aplicar estos cambios, será necesario reentrenar los modelos para que XGBoost ajuste sus pesos a las nuevas reglas.

## Testing
- Se deberán ejecutar los tests unitarios existentes en `tests/ml/` para asegurar que el cambio de features no rompe los pipelines.
- Se debe validar manualmente o mediante tests que, al pasar un partido futuro a `build_features_for_matches`, el Elo asignado corresponda al último Elo histórico de ese equipo específico y no al del equipo de la fila anterior.