# Especificación de Diseño: Evolución del Modelo 1X2 con XGBoost y Optuna

**Fecha:** 26 de Abril de 2026
**Contexto Tecnológico:** Python, Pandas, Scikit-Learn, XGBoost, Optuna
**Módulos Afectados:** `src/ml/train.py`, `src/ml/inference.py`

---

## 1. Overview / Objetivo
Elevar la calidad técnica del modelo de predicción de Ganador (1X2) reemplazando el algoritmo base (`RandomForestClassifier` estático) por un ecosistema de tuning profesional idéntico al implementado para los modelos de goles. Esto implica usar `XGBClassifier` optimizado automáticamente por `Optuna` y validado temporalmente con `TimeSeriesSplit`.

## 2. Cambio de Motor (De Random Forest a XGBoost)
El modelo `winner_model` pasará de ser un `RandomForestClassifier` a un `XGBClassifier`.
*   **Configuración del Objetivo:** Dado que es un problema de clasificación multiclase (Local, Empate, Visitante), XGBoost se configurará con `objective='multi:softprob'` para que devuelva las probabilidades exactas de cada clase de forma calibrada.

## 3. Tuning de Hiperparámetros (`Optuna`)
Se implementará una función `optimize_xgboost_classifier` en `train.py`.
*   **Espacio de Búsqueda:** Optuna buscará la mejor combinación de `max_depth` (2 a 7), `learning_rate` (0.01 a 0.2), `n_estimators` (50 a 200), `subsample` y `colsample_bytree`.
*   **Validación Cruzada (CV):** Al igual que en la Fase B, la validación interna de Optuna usará `TimeSeriesSplit(n_splits=3)` para respetar la cronología y evitar el Data Leakage temporal.
*   **Métrica de Optimización:** Optuna intentará maximizar el `accuracy_score` (Precisión) o minimizar el `log_loss` (Logarithmic Loss). Optaremos por minimizar el `log_loss` interno, ya que penaliza predicciones muy seguras pero incorrectas, lo cual es ideal para apuestas.

## 4. Criterio de Aceptación (Quality Gate)
El despliegue del modelo (`winner_model.joblib`) seguirá condicionado a superar un umbral de calidad empírico en el conjunto de prueba (`test_size=0.2`).
*   **Métrica Principal:** La precisión (`Accuracy`) debe ser mayor o igual a **0.50** (50%).
*   **Mejora Continua:** Además, el nuevo Accuracy no puede ser significativamente peor que el del modelo anterior desplegado (margen de tolerancia de -0.02).

## 5. Mantenimiento del Pipeline de Datos e Inferencia
*   **Preprocesamiento:** Se reutilizará el `ColumnTransformer` ya existente en `train.py` para manejar la imputación de nulos (`SimpleImputer(strategy='median')`).
*   **Inferencia:** En `inference.py`, el cambio de RandomForest a XGBoost es transparente gracias a la API compatible de Scikit-Learn (`predict_proba`), por lo que no se requieren cambios estructurales mayores en la inferencia, solo asegurar que XGBoost se cargue correctamente.