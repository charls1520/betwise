# Plan de Implementación: Inferencia con Contexto Histórico

> **Nota de ejecución:** Todo el código y los tests se ejecutarán en local o dentro del contenedor, según corresponda. NO SE USARÁN SUBAGENTES.

**Objetivo:** Modificar `src/ml/inference.py` para fusionar "al vuelo" los datos de inferencia (partidos futuros) con el historial `merged_history_cache.csv`, de modo que las variables temporales (fatiga, rachas de tiros/goles) se calculen usando el historial real en vez de rellenarse con ceros.

### Task 1: Modificar la inferencia para incluir el historial
- [x] Modificar `backend/src/ml/inference.py` en la función `predict_matches`.
- [x] Ejecutar los tests de inferencia para comprobar que no se rompe: `docker exec -it betwise_backend pytest tests/ml/test_inference.py -v`.

### Task 2: Actualizar Test de Inferencia
- [x] Modificar `backend/tests/ml/test_inference.py` para mockear o simular que el archivo histórico existe, y validar que la concatenación funciona.
- [x] Ejecutar los tests nuevamente para verificar cobertura y correctitud.

### Task 3: Actualizar Documentación
- [x] Actualizar `docs/MASTER-PLAN.md` marcando esta subtarea/fase como completada o moviendo el progreso.
- [x] Opcional: Actualizar `SPEC.md` detallando este nuevo comportamiento de inferencia con contexto.