# Spec: Ingesta de Datos 100% Reales (Matchmaking Difuso y Tolerancia Cero a Vacíos)

## Contexto y Objetivo
El objetivo es erradicar la pérdida silenciosa de datos (`NaN`s) durante la ingesta histórica, garantizando que el pipeline de ML trabaje con información real (Goles Esperados y Elo) sin necesidad de abusar de la imputación por promedios.

Las fugas actuales se deben a:
1. Diferencias en la fecha de registro entre `football-data` y `Understat` (por husos horarios).
2. Fallos en los nombres y abusos del límite de peticiones (rate limits) a `Clubelo`.
3. Errores silenciosos donde Cloudflare bloquea a Playwright y este devuelve objetos vacíos.

## 1. Cruce Seguro de Goles Esperados (Understat)
Se modificará el cruce (merge) en `historical.py`:
- **Algoritmo de Cruce:** En lugar de hacer match por `[Equipo, Fecha Exacta]`, se cruzará por `[Equipo Local, Equipo Visitante, Temporada/Año]`. Dado que en cada liga los equipos juegan en casa contra el mismo rival una única vez por temporada, el cruce es matemáticamente perfecto independientemente de si la fecha difiere por 24-48 horas.
- El script de `understat_historical.py` no requiere cambiar su lógica de extracción asíncrona, pero el DataFrame resultante entregado a `historical.py` mantendrá información de qué equipo era local y visitante, si es posible, o en el `merge` se validará la correspondencia de ambos contendientes.

## 2. Obtención de Elo en Masa (Clubelo)
Se modificará el scraper `clubelo.py` y su uso en `historical.py`:
- **Bulk Download:** En lugar de iterar por cada uno de los 20 equipos de una liga enviando 20 peticiones a la API de Clubelo (`api.clubelo.com/[Club]`), descargaremos o cachearemos localmente la base de datos de fechas si el API lo permite, o mantendremos un diccionario/caché persistente local.
- **Normalización Inteligente:** Al obtener los datos de Elo en memoria, se pasará la lista de nombres completos al `TeamNormalizer`. Esto aplicará TheFuzz (y si falla, el LLM de Auto-Healing) localmente, evitando que un equipo se quede sin Elo por abreviaturas complejas como `Nott'm Forest`.

## 3. Tolerancia Cero a Vacíos (Hard Failures)
Se aplicará la política de "Si entra basura, detente" (Fail Fast):
- **Aserción de Scraping:** Si `fetch_understat_historical_season` devuelve un DataFrame vacío porque Cloudflare bloqueó la página (ej. no encuentra `teamsData`), en lugar de retornar silenciosamente, levantará una excepción `Exception("Cloudflare Block / Empty Data")`.
- **Reintentos (Tenacity):** `historical.py` envolverá las peticiones a Playwright con un bloque de reintentos exponenciales (`@retry` de `tenacity` con espera de hasta varios minutos) si capta este error. Si tras 5 intentos sigue fallando, se abortará el pipeline por completo en lugar de grabar datos corruptos/vacíos en el CSV o la Base de Datos.
- **Limpieza del Data Lake:** Las filas del CSV donde aún falten métricas críticas se eliminarán estrictamente antes del entrenamiento. No más `NaN` en los features primarios `xg_diff` y `elo_diff`.

## 4. Impacto Arquitectónico
- **Performance:** La ingesta será ligeramente más lenta por los reintentos pausados (anti-ban), pero la calidad del dato será del 100%.
- **Bases de Datos:** Los CSVs en `data/historical` contendrán exclusivamente filas ricas en características, aumentando el *Value Edge* real del modelo de Machine Learning.