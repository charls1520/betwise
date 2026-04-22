# Spec: Refinamiento de Scrapers, Calidad de Datos y Modelos ML

## Contexto y Objetivo
El objetivo es auditar y mejorar el pipeline actual de extracción, validación y entrenamiento de modelos (Machine Learning) sin romper la arquitectura existente definida en el `MASTER-PLAN.md` (FastAPI, React, Cron Jobs). Se busca garantizar que haya suficiente historial para todas las ligas (no solo "EPL"), que la calidad de los datos sea alta (validaciones estrictas) y que el entrenamiento de ML utilice imputaciones correctas y variables más predictivas.

## 1. Extracción y Scrapers (Playwright + Scrapling)
Actualmente, `understat.py` usa Playwright y `scrapling_base.py` usa Scrapling.
- **Parametrización de Ligas:** En `understat.py`, eliminaremos el hardcode a `"EPL"`. El scraper iterará dinámicamente sobre la lista de ligas definida en la configuración (`config.py`).
- **Resiliencia (Anti-Bot y Rate Limits):** Se mantendrán las pausas humanizadas y los reintentos (Tenacity) ya implementados en previas specs.
- **Profundidad Histórica:** Se asegurará que la ingesta histórica abarque múltiples temporadas hacia atrás por cada liga, guardando el historial necesario para calcular promedios robustos.

## 2. Calidad de Datos y Validación
El módulo `validators.py` actual solo verifica rangos básicos. Se agregarán aserciones de calidad más robustas:
- **Suficiencia de Historial:** Un registro de partido solo se considerará "válido" para entrenar si ambos equipos tienen un mínimo de `N` partidos previos en la temporada (ej. N=3) para asegurar que las métricas de *Rolling Averages* (promedios móviles) o forma no estén sesgadas.
- **Consistencia de Datos:** Validar que los valores de `xG` y `Elo` no contengan saltos estadísticamente imposibles de un partido a otro.
- **Aislamiento de Fallos:** Si la validación de una liga falla, el error se registrará, pero no detendrá el pipeline de las demás ligas.

## 3. Entrenamiento y Modelos (ML)
Los módulos `train.py` y `features.py` necesitan ser más sofisticados que simplemente usar `xg_diff` y `elo_diff` rellenando NaNs con ceros.
- **Manejo de Faltantes (NaNs):** Rellenar variables como el Elo con `0` daña el modelo. Se usará imputación hacia adelante (*forward-fill*) para arrastrar el último valor conocido del equipo, o en su defecto, el promedio de la liga.
- **Nuevas Features (Variables):** 
  - *Rolling Averages*: Promedio de goles a favor/en contra o xG/xGA de los últimos 5 partidos.
  - *Forma/Racha*: Porcentaje de victorias en los últimos 3-5 partidos.
- **Modelo Global:** Se entrenará un único `RandomForestClassifier` y `LogisticRegression` utilizando los datos combinados de todas las ligas, incorporando un identificador de liga o de peso relativo para generalizar mejor los patrones, sin afectar los endpoints de inferencia actuales (`inference.py`).

## 4. Impacto en la Arquitectura
- **Backend:** Sin cambios estructurales. Solo mejoras dentro de `src/ml/` y `src/ingestion/`.
- **Frontend:** Ninguno. La API de inferencia seguirá devolviendo las mismas probabilidades pero más precisas.
- **Base de Datos:** Se mantendrán las tablas actuales, agregando solo lógica de cálculo en memoria o columnas temporales en DataFrames de pandas durante el entrenamiento.