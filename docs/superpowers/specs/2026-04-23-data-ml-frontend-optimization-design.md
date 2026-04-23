# Spec: Data Ingestion, ML Validation, and Real-Time Frontend Optimization

## Context
El proyecto requiere tres mejoras operativas críticas para garantizar la calidad y la experiencia en tiempo real:
1. Evitar la descarga repetitiva de los mismos partidos durante cada ciclo de ingesta para ahorrar ancho de banda y tiempo.
2. Validar que los modelos de Machine Learning (ML) se entrenen correctamente antes de ser desplegados a producción, evitando la regresión de rendimiento.
3. Asegurar que el frontend (Dashboard) esté actualizado constantemente con los últimos datos disponibles tras las ingestas y entrenamientos.

## 1. Prevención de Descargas Duplicadas (Ingesta Delta)
### Diseño
- **Filtro en Origen (Scraper)**: Los scrapers (`odds_api`, `understat_historical`, etc.) utilizarán parámetros de fecha/tiempo (como `last_update` o un rango desde el último `commence_time` conocido) siempre que la API externa lo soporte.
- **Caché de Estado de Ingesta**: Se creará un mecanismo en base de datos o un archivo de estado (ej. `ingestion_state.json` en `backend/data/`) que registre la última fecha/hora exitosa (timestamp UTC) de descarga para cada liga/origen.
- En la siguiente ejecución, el cron job leerá este timestamp y pasará dicho filtro a los scrapers para descargar **únicamente** los deltas (los datos creados o modificados desde ese punto).

## 2. Validación Automática del Modelo ML
### Diseño
- **Métricas de Evaluación**: `train.py` se modificará para separar los datos (Train / Test split, o validación cruzada). Se calcularán métricas clave de clasificación, por ejemplo, Accuracy y ROC-AUC para el modelo 1X2 y el modelo Over/Under.
- **Umbral y Comparación**: El sistema guardará el historial de métricas del modelo actualmente en producción (en un archivo JSON o en BD). Al entrenar el nuevo modelo, se compararán sus métricas con las del modelo actual.
- **Circuit Breaker**: Si el rendimiento (ej. Accuracy) del nuevo modelo es significativamente peor (supera un margen de regresión permitido, ej. > 2% de caída) o no supera un umbral base (ej. 50%), el entrenamiento será marcado como fallido o "degraded", no se reemplazará el `.joblib` en producción, y se registrará la falla en los logs y en el endpoint de estado de salud (Audit Panel).

## 3. Actualización Continua del Frontend
### Diseño
- **Short Polling**: El dashboard principal (`DashboardPanel.tsx`) y componentes críticos utilizarán una estrategia de Short Polling.
- **Implementación React**: Se usará un `setInterval` (o idealmente `React Query` con refetch interval) para solicitar el endpoint `/api/dashboard` y `/api/health/audit` cada 60 segundos de forma silenciosa (en background).
- **UX**: Esto asegurará que, sin necesidad de recargar la página manualmente, el usuario siempre vea los últimos partidos ingestados, las sugerencias actualizadas por el ML y las nuevas métricas del sistema. La recarga no interrumpirá interacciones de otros paneles.

## Impacto
Estas tres mejoras reducirán la carga de red y costos (menor uso de la Odds API o scrapers), garantizarán estabilidad en las predicciones y mejorarán significativamente la experiencia del usuario (datos frescos siempre visibles).
