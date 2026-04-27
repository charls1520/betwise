# Plan de Implementación: XGBoost, Optuna y Eficacia (Fase B)

> **Nota de ejecución:** Todo el código y los tests se ejecutarán DENTRO de los contenedores de Docker (ej. `docker exec -it betwise_backend bash -c "..."`). NO SE USARÁN SUBAGENTES.

**Objetivo:** Integrar XGBoost Tuning (Optuna), TimeSeriesSplit, ColumnTransformer y variables de eficacia en el pipeline de ML.

### Task 1: Instalar dependencias en el contenedor
- [ ] Modificar `backend/requirements.txt` añadiendo `xgboost`, `optuna` y `sidetable`.
- [ ] Instalar dependencias en el contenedor `betwise_backend` (`docker exec -it betwise_backend pip install -r requirements.txt`).

### Task 2: Implementar Variables de Eficacia en `features.py`
- [ ] Modificar `backend/src/ml/features.py` para calcular `offensive_efficiency` y `defensive_efficiency`.
    - Goles Favor - xG Favor
    - Goles Contra - xG Contra
    - Agrupar por equipo, `shift(1)` y `rolling(5).mean()`.
    - Fusionar con dataframe principal como `home_offensive_efficiency`, etc.
- [ ] Ejecutar tests en contenedor: `docker exec -it betwise_backend pytest tests/ml/test_features.py -v`.

### Task 3: Configurar Optuna y TimeSeriesSplit en `train.py`
- [ ] Modificar `backend/src/ml/train.py`.
    - Integrar `ColumnTransformer`.
    - Añadir lógica de búsqueda de Optuna con `TimeSeriesSplit` para optimizar `max_depth`, `learning_rate`, `n_estimators`, etc.
    - Asegurar que el criterio de aceptación (Quality Gate) exige RMSE < 1.30 para Goles y Accuracy >= 0.50 para Ganador.
- [ ] Ejecutar tests en contenedor: `docker exec -it betwise_backend pytest tests/ml/test_train.py -v`.

### Task 4: Ejecutar Pipeline de Entrenamiento
- [ ] Ejecutar en contenedor: `docker exec -it betwise_backend bash -c "export PYTHONPATH='.' && python src/ml/train.py"`.
- [ ] Verificar logs y el archivo `model_metrics.json` para comprobar que los modelos aprueban y se guardan.