# Design Spec: Expansión Multi-Liga (Top 5 Europeas)

## Contexto
Actualmente BetWise está diseñado, orquestado y entrenado exclusivamente para la **English Premier League (EPL)**. El scraper The-Odds-API usa el identificador `soccer_epl`, Understat apunta a `/league/EPL` y Clubelo extrae `/eng`. Sin embargo, el core de la aplicación (modelo de Machine Learning basado en `xg_diff` y `elo_diff`) es inherentemente agnóstico a la liga, dado que mide fuerzas relativas entre equipos.
Se requiere escalar la plataforma para que cubra las **5 Grandes Ligas de Europa**: Premier League (Inglaterra), La Liga (España), Serie A (Italia), Bundesliga (Alemania) y Ligue 1 (Francia).

## Objetivos
1. **Escalabilidad del Scraping:** Reestructurar los scripts de ingestión para que iteren a través de una lista configurable de ligas y extraigan cuotas, xG y Elo simultáneamente.
2. **Entrenamiento Agregado:** Combinar el dataset histórico de todas estas ligas en el mismo motor de Machine Learning. El algoritmo aprenderá patrones generales de fuerza relativa y "value betting", volviéndose más robusto.
3. **Control de Presupuesto:** Asegurar que la expansión no exceda los límites gratuitos de la API de *The-Odds*, administrando con precisión las llamadas iterativas.

## Arquitectura de Expansión

### 1. Mapeo de Identificadores (Constants)
Se definirá un archivo de configuración o diccionario central (ej. `src/ingestion/config.py`) que establezca la relación entre los identificadores de los tres proveedores:
| País | The-Odds-API | Understat | Clubelo | football-data (History) |
|---|---|---|---|---|
| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENG | `soccer_epl` | `EPL` | `/eng` | `E0` |
| 🇪🇸 ESP | `soccer_spain_la_liga` | `La_liga` | `/esp` | `SP1` |
| 🇮🇹 ITA | `soccer_italy_serie_a` | `Serie_A` | `/ita` | `I1` |
| 🇩🇪 GER | `soccer_germany_bundesliga` | `Bundesliga` | `/ger` | `D1` |
| 🇫🇷 FRA | `soccer_france_ligue_one` | `Ligue_1` | `/fra` | `F1` |

### 2. Orquestador de Tareas (ETL Pipeline)
- En `tasks.py`, el `run_daily_scraping()` iterará sobre el diccionario anterior.
- Extraerá los datos de Understat y Clubelo por cada liga y los consolidará en un gran diccionario/JSON global antes de guardarlos.
- Opcionalmente se usará asyncio/`async_playwright` para lanzar las consultas de las 5 páginas de Understat en paralelo y reducir el tiempo del cron job.

### 3. Histórico y Normalización a Gran Escala
- **Caché Histórico:** `download_football_data_co_uk()` descargará iterativamente `E0.csv`, `SP1.csv`, etc. Todo caerá en el mismo `merged_history_cache.csv`.
- **Auto-Healing Normalizer:** Se extenderá la lista `canonical_teams` pasándole los nombres combinados de las 5 ligas al arrancar la inferencia. Dado que el LLM OpenRouter se hace cargo de las discrepancias (ej. "Atleti" -> "Atletico Madrid", "Juve" -> "Juventus"), el proceso crecerá sin necesitar trabajo manual de programación de excepciones en múltiples idiomas.

### 4. Frontend (Dashboard)
- El Dashboard devolverá la lista combinada de partidos.
- A corto plazo, el Frontend añadirá visualmente una etiqueta o ícono que indique de qué liga proviene la sugerencia, agrupando u ordenando los "Value Edges" sin importar el país.

## Componentes a Modificar
- `src/ingestion/scrapers/odds_api.py`, `understat.py`, `clubelo.py`, `historical.py`: Reescribir las funciones para que acepten un parámetro `league_config` en lugar de tener las URLs "hardcodeadas".
- `src/ingestion/tasks.py`: Orquestar el loop de las 5 ligas.
- `src/main.py`: Adaptar la lectura de datos crudos (`raw_odds` y `xg_stats`) para manejar la estructura ampliada.

## Manejo de Errores y Seguridad
- Si The-Odds-API devuelve un `429 Too Many Requests` durante el loop de las 5 ligas (por exceder límites), la ingesta se detendrá silenciosamente guardando el progreso que haya logrado, pero se evitará enviar cuotas corruptas.
- El modelo ML será entrenado con cerca de 2,500 partidos históricos de calidad gracias a esta expansión. Si algunas ligas tienen datos ausentes de xG o Elo, el `dropna()` establecido previamente continuará garantizando que solo la información perfecta entre al algoritmo.