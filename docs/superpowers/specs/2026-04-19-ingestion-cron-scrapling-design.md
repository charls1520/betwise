# Design Spec: Nuevo Flujo de Ingesta, Scraping y Retraining

## Contexto
El sistema actual realiza un scraping básico (BBC, Odds, Understat) y carece de programación automática para la recolección de datos y el reentrenamiento del modelo. Además, se requiere evitar la inserción de información falsa, vacía o inventada, mejorar el proceso de extracción web incorporando `Scrapling` (https://github.com/D4Vinci/Scrapling) y añadir `clubelo.com` como nueva fuente de datos estadísticos para enriquecer la predicción.

## Objetivos
1. Programar scraping diario y reentrenamiento de ML semanal mediante un Cron en Python (APScheduler) dentro del backend FastAPI.
2. Integrar `Scrapling` como motor principal de extracción para sitios web complejos y antibots.
3. Incorporar puntuaciones Elo de `clubelo.com`.
4. Garantizar la fiabilidad y calidad de los datos (Filtro Anti-Basura) antes de que toquen la DB o el RAG.

## Arquitectura de Ingesta

### 1. Programador de Tareas (Scheduler)
- **Tecnología:** `APScheduler` (BackgroundScheduler) ejecutado en paralelo dentro de la misma instancia de `main.py` (FastAPI).
- **Cron Diario (Ingesta):** Se ejecutará todos los días a las 02:00 AM (UTC).
  - Activa secuencialmente: Scraper de Noticias, The-Odds API, Understat xG y Clubelo.
- **Cron Semanal (Retraining):** Se ejecutará todos los lunes a las 04:00 AM (UTC).
  - Llama a los métodos en `src.ml.train` para recalcular pesos con los nuevos resultados recolectados.

### 2. Motor de Scraping Mejorado
- **Scrapling:** Sustituirá a `Playwright` o requests básicos donde sea necesario (ej. Understat o lectura profunda de BBC), aprovechando sus capacidades de bypassing y rendimiento asíncrono.
- **Nueva Fuente - Clubelo:** Se descargará el CSV/API de `http://api.clubelo.com` para los equipos de la Premier League. El `TeamNormalizer` existente (`thefuzz`) se usará para alinear los nombres de Clubelo con los de la DB.

### 3. Validación Anti-Basura (Data Quality Gate)
Ningún dato pasará a `data/raw`, a la DB Relacional o a ChromaDB sin pasar dos barreras:
1. **Validación de Esquema (Pydantic):** Cada scraper retornará objetos Pydantic estrictos (ej. `NewsArticle`, `MatchOdds`, `EloScore`). Si el modelo detecta strings vacíos, campos `None` obligatorios, o fechas inválidas, el dato se descarta.
2. **Validación Heurística (Volumen):**
   - Si la cuota de extracción de noticias cae un 80% respecto a la media de la semana, se frena la ingesta de noticias y se lanza un error en los logs (para evitar llenar el RAG de "nada").
   - Las probabilidades de apuestas deben estar en el rango de (1.0, 100.0).
   - Si un scraper devuelve una lista vacía, el proceso se aborta para esa fuente en ese ciclo.

### 4. Actualización del RAG y ML
- **ChromaDB / LlamaIndex:** Solo los documentos validados y con fechas recientes se indexarán. Se purgarán noticias o datos demasiado antiguos si fuese necesario, o simplemente se enriquecerá la colección diariamente.
- **Modelos ML:** Las métricas de Clubelo (Elo Score) se añadirán como *Features* a los inputs de entrenamiento junto con los xG (Understat).

## Componentes a Modificar / Crear
- `src/ingestion/scrapers/scrapling_base.py` (Nuevo wrapper de Scrapling).
- `src/ingestion/scrapers/clubelo.py` (Nuevo scraper).
- `src/ingestion/scheduler.py` (Configuración de APScheduler).
- `src/ingestion/validators.py` (Esquemas Pydantic y reglas heurísticas).
- `src/main.py` (Arranque del scheduler junto a FastAPI).
- `src/ml/features.py` y `src/ml/train.py` (Incorporar Clubelo Elo).
- Modificar dependencias: `pip install apscheduler scrapling-playwright` (o versión respectiva).

## Manejo de Errores
- Si falla la validación, los errores se escribirán en el endpoint de Auditoría (System Health) que ya existe (`/api/health/audit`).
- FastAPI no se caerá si el scheduler falla; los errores se confinan al hilo del scheduler.