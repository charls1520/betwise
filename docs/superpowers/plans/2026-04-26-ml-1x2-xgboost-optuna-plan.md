# Plan de Implementación: Evolución del Modelo 1X2 con XGBoost y Optuna

> **Nota de ejecución:** Todo el código y los tests se ejecutarán DENTRO del contenedor de Docker. NO SE USARÁN SUBAGENTES.

**Objetivo:** Integrar XGBoost Tuning (Optuna), TimeSeriesSplit y log_loss para el modelo de Ganador (1X2).

### Task 1: Modificar `train.py` para usar `XGBClassifier` y Optuna
- [x] Crear función `optimize_xgboost_classifier` usando `optuna`.
- [x] Configurar búsqueda de parámetros (`max_depth`, `learning_rate`, `n_estimators`, etc.) y optimizar `log_loss` usando `TimeSeriesSplit`.
- [x] Reemplazar `RandomForestClassifier` por `XGBClassifier` en el bloque de "Winner Model".
- [x] Añadir `log_loss` a las métricas guardadas en `model_metrics.json`.

### Task 2: Modificar Tests
- [x] Actualizar `tests/ml/test_train.py` para parchear `XGBClassifier` en lugar de `RandomForestClassifier` y `optimize_xgboost_classifier`.
- [x] Ejecutar tests en contenedor: `docker exec -it betwise_backend pytest tests/ml/test_train.py -v`.

### Task 3: Ejecutar Entrenamiento Completo y Validar Inferencia
- [x] Ejecutar el pipeline de entrenamiento: `docker exec -it betwise_backend bash -c "export PYTHONPATH='.' && python src/ml/train.py"`.
- [x] Verificar que los tests de inferencia siguen funcionando.
- [x] Actualizar `MASTER-PLAN.md` indicando la compleción.