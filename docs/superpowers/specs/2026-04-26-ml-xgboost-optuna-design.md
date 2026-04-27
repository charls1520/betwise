# Especificación de Diseño: XGBoost, Optuna y Eficacia (Fase B)

**Fecha:** 26 de Abril de 2026
**Contexto Tecnológico:** Python, Pandas, Scikit-Learn, XGBoost, Optuna, Sidetable
**Módulos Afectados:** `src/ml/features.py`, `src/ml/train.py`, `backend/requirements.txt`

---

## 1. Overview / Objetivo
Mejorar sustancialmente el modelo predictivo de goles (y, por extensión, el proyecto entero) reemplazando configuraciones por defecto por un ecosistema de tuning profesional. Pasaremos de usar hiperparámetros estáticos a búsquedas automatizadas con **Optuna** validadas con **TimeSeriesSplit**, e incluiremos variables de **Eficacia (Goles vs xG)** para detectar "suerte" o sobredesempeño estadístico.

## 2. Nuevas Variables (Features de Eficacia)
Se ampliará `build_features_for_matches` en `features.py` para calcular la Diferencia entre Goles Reales (FTHG/FTAG) y Goles Esperados (xG).
*   **Eficiencia Ofensiva:** Promedio móvil de (Goles a Favor - xG a Favor) en los últimos 5 partidos.
*   **Eficiencia Defensiva:** Promedio móvil de (Goles en Contra - xG en Contra) en los últimos 5 partidos.
*   **Variables Finales:** `home_offensive_efficiency`, `away_offensive_efficiency`, `home_defensive_efficiency`, `away_defensive_efficiency`.
*   *Restricción:* Se utilizará rigurosamente `shift(1)` antes del `rolling` para evitar Data Leakage.

## 3. Pipeline de Preprocesamiento (`ColumnTransformer`)
El preprocesamiento en `train.py` pasará de un simple `SimpleImputer` a un `ColumnTransformer`. Esto organiza mejor el flujo de datos:
*   **Variables Numéricas:** Imputación con `median` (mediana) y posterior escalado (opcional/estándar).
*   *Preparación:* Facilita enormemente añadir variables categóricas (como árbitros o estadios) en iteraciones futuras.

## 4. Tuning de Hiperparámetros (`Optuna` + `TimeSeriesSplit`)
El entrenamiento de los modelos `XGBRegressor` (para Goles Locales y Visitantes) y `RandomForestClassifier` (Ganador) dejará de ser estático.
*   **Optuna:** Se crearán "estudios" (`study.optimize`) para buscar los mejores parámetros (`max_depth`, `learning_rate`, `n_estimators`, `subsample` para XGBoost).
*   **Validación Cruzada:** La métrica de evaluación dentro de Optuna será generada usando `TimeSeriesSplit(n_splits=5)`. Esto entrena con el pasado y valida con el futuro de forma escalonada, evitando trampa temporal (Leakage temporal).
*   **Métrica:** Optuna intentará minimizar el Error Cuadrático Medio (RMSE) para los goles.

## 5. Criterio de Aceptación (Quality Gate)
El despliegue de los modelos (guardado en `.joblib`) seguirá condicionado a su calidad empírica:
*   Modelo de Goles (RMSE): Debe ser estrictamente menor a **1.30**.
*   Con el tuning de Optuna y las nuevas variables de eficacia, se proyecta superar esta barrera consistentemente.

## 6. Dependencias Adicionales
Se añadirán a `requirements.txt`:
*   `optuna`
*   `sidetable` (para facilitar el EDA futuro si es necesario)
*   `xgboost` (en caso de que no esté)