# Active Data Recovery & Audit Design

## 1. Detección y Recuperación Activa (On-the-fly Recovery)
**Problema:** Cuando el motor de inferencia (`main.py`) no encuentra estadísticas clave (xG o Elo) para un equipo, el sistema actualmente asigna un valor por defecto (0.0 o 1500) de manera silenciosa, lo que genera predicciones de ML erróneas.
**Solución:** 
- Implementar un módulo interceptor (`src/ingestion/recovery.py`).
- Cuando `main.py` detecte que falta xG o Elo para un equipo normalizado, pausará la inferencia para ese partido.
- Se invocará una función de recuperación en tiempo real (ej. `fetch_xg_live(team_name)` o `fetch_elo_live(team_name)`).
- **CRÍTICO:** Para la recolección en vivo (ej. Understat), se utilizará exclusivamente **Scrapling** (scraping ligero y rápido), evitando inicializar navegadores pesados con Playwright.
- Si la recuperación es exitosa, se actualiza la caché en memoria y se procede con el cálculo real.

## 2. Estrategia de Fallo: Tolerante con Alertas
**Problema:** Si el scraper en vivo falla (API caída, nombre totalmente irreconocible), el sistema debe seguir funcionando sin mentir con ceros.
**Solución:**
- **Imputación Inteligente:** En lugar de `0.0`, el sistema calculará dinámicamente el promedio de la liga para esa métrica (ej. xG promedio de la Premier League) y lo asignará al equipo huérfano.
- **Indicador de Confianza:** El endpoint `/api/dashboard` añadirá un nuevo campo booleano `is_reliable: false` (o `data_quality: "LOW"`) al objeto del partido afectado.
- **UI Frontend:** El frontend leerá este flag. Si el partido tiene datos de baja calidad o inferidos por fallo, mostrará un ícono de advertencia (⚠️) indicando visualmente que la predicción es una estimación con datos incompletos.
- **Logging:** Se emitirá un log nivel `WARNING/ERROR` detallando exactamente qué métrica falló para qué equipo en qué partido.

## 3. Auditoría a Largo Plazo y Curación de Nombres
**Problema:** La mayoría de fallos provienen de discrepancias en los nombres (ej. "Betis" vs "Real Betis"). Depender de recuperaciones en vivo o promedios es ineficiente a largo plazo.
**Solución:**
- **Registro de Anomalías:** Cada vez que el sistema no encuentre un "match" directo y tenga que usar recuperación en vivo o promedios, registrará el nombre problemático en un archivo local: `data/audit/unmatched_teams.json`.
- **Endpoint de Auditoría:** Se extenderá la respuesta del endpoint `/api/health/audit` para incluir la lista de nombres huérfanos/problemáticos recientes.
- **Flujo de Trabajo del Administrador:** El administrador podrá consultar el endpoint de auditoría, identificar los nombres que fallan recurrentemente, y agregarlos manualmente al diccionario de sinónimos en `src/ingestion/normalizer.py`, curando la base de datos de forma permanente.