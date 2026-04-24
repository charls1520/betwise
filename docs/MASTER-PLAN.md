---
# Master Plan — BetWise

**Última actualización:** 23 de Abril de 2026

---

## Visión

BetWise es un asistente web de apuestas deportivas enfocado en la Premier League. Combina un dashboard con predicciones de valor (basadas en ML) y un chat interactivo con RAG (LlamaIndex/LightRAG) para responder consultas detalladas sobre partidos usando datos históricos y noticias recientes.

---

## Sub-proyectos

### 1. Arquitectura Base (Completo)
- [x] Brainstorming y Diseño
- [x] Backend FastAPI (Python) con Healthcheck
- [x] Modelos iniciales de Base de Datos Relacional
- [x] Frontend React (Vite) conectado al Backend

### 2. Motor de Ingesta y Normalización (Completo)
- [x] Brainstorming y Diseño
- [x] Scripts de scraping para estadísticas y cuotas (Almacenamiento crudo en Data Lake)
- [x] Motor de normalización difusa de nombres de equipos
- [x] Automatización (Cron Jobs) de actualización diaria (ETL Pipeline Básico)

### 3. Motor RAG y ML (En progreso)
- [x] Brainstorming y Diseño RAG
- [x] Integración de LlamaIndex y base de datos vectorial para noticias
- [ ] Entrenamiento de modelo ML ligero para predicciones
- [x] Interfaz de chat en el Frontend

### 4. Fuentes de Datos Reales (Completo)
- [x] Brainstorming y Diseño Scraping
- [x] Scraper de Noticias RSS (BBC)
- [x] Cliente API de Cuotas (The-Odds-API)
- [x] Orquestador de tareas diarias

### 5. Motor de Machine Learning (Completo)
- [x] Brainstorming y Diseño ML
- [x] Feature Engineering y Extracción de Datos
- [x] Entrenamiento de modelos (1X2 y Over/Under)
- [x] Pipeline de Inferencia

### 6. Integración Final (Completo)
- [x] Brainstorming y Diseño de Integración
- [x] Endpoint unificado de Dashboard
- [x] Conexión de Endpoint Chat con RAG
- [x] Integración de React con Endpoints Reales

### 7. Rediseño UI y Modelo Gemma (Completo)
- [x] Brainstorming y Diseño UI/Gemma
- [x] Actualizar LlamaIndex a Gemma4:26b
- [x] Configurar Tema Tailwind Dark Mode
- [x] Rediseñar Dashboard y ChatPanel

### 8. Integración Real ML & Scraping (Completo)
- [x] Brainstorming y Diseño Scraping/ML Real
- [x] Strict Team Normalizer (Threshold 95%)
- [x] Understat Scraper (xG Real)
- [x] Integrar Data Real en Dashboard Inference

### 9. Motor de Scraping con Playwright (Completo)
- [x] Brainstorming y Diseño de Scraper con Navegador Headless
- [x] Instalar dependencias de Playwright
- [x] Implementar scraper asíncrono para Understat

### 10. Motor de Fiabilidad y Sugerencias (Completo)
- [x] Brainstorming y Diseño de Reglas
- [x] Implementar Filtros de Valor y Thresholds
- [x] Inicializar RAG con Datos Reales
- [x] Integrar Sugerencias en Frontend

### 11. Entrenamiento de Modelo ML con Datos Históricos (Completo)
- [x] Brainstorming y Diseño de Entrenamiento
- [x] Ingesta de datos históricos desde football-data.co.uk
- [x] Actualización de Feature Engineering para histórico
- [x] Script de Entrenamiento Real

### 12. Panel de Auditoría y System Health (Completo)
- [x] Brainstorming y Diseño del Panel de Auditoría
- [x] Endpoint Backend de Auditoría
- [x] Modal Frontend de System Health
- [x] Integración en la Interfaz

### 13. Dockerización del Entorno de Desarrollo (Completo)
- [x] Brainstorming y Diseño de Arquitectura Local
- [x] Configurar `docker-compose.yml` para PostgreSQL y ChromaDB
- [x] Crear Dockerfiles de desarrollo para Frontend y Backend
- [x] Extraer variables de entorno a `.env`
- [x] Actualizar documentación y README

### 14. Cron Jobs, Scrapling y Mejora de Ingesta (Completo)
- [x] Brainstorming y Diseño de Ingesta y Validación (Completo)
- [x] Integrar APScheduler en FastAPI
- [x] Validadores anti-basura estrictos con Pydantic y reglas heurísticas
- [x] Reemplazar scraping estático con motor dinámico `Scrapling`
- [x] Agregar nuevo scraper para `clubelo.com` y entrenar con nuevas métricas
- [x] Configurar job semanal de retraining de Machine Learning

### 15. Entrenamiento con xG y Elo Históricos (Completo)
- [x] Brainstorming y Diseño de Ingesta Histórica (Completo)
- [x] Desarrollar Scraper histórico para Clubelo
- [x] Desarrollar Scraper histórico (Scrapling) para Understat
- [x] Unir (Merge) datos de football-data.co.uk con Clubelo y Understat
- [x] Entrenar modelo usando features `xg_diff` y `elo_diff`

### 16. Sistema de Caché Persistente para Ingesta Histórica (Completo)
- [x] Brainstorming y Diseño de Sistema de Caché (Completo)
- [x] Implementar mecanismo de caché local
- [x] Evitar consultas reduntantes a APIs
- [x] Validación estricta anti-vacíos (Cero Vacíos)

### 17. Filtro Temporal Estricto (48 Horas) (Completo)
- [x] Brainstorming y Diseño de Filtro Temporal (Completo)
- [x] Configurar scraper de Odds API para filtrar `commence_time` a 48h máximo
- [x] Implementar zona horaria `America/Bogota` (UTC-5) para todas las validaciones
- [x] Actualizar tests para reflejar el filtro de 48 horas

### 18. Auto-Healing Team Normalizer via LLM (Completo)
- [x] Brainstorming y Diseño de Auto-Healing (Completo)
- [x] Reescribir `TeamNormalizer` para cargar/guardar alias desde `team_aliases.json`
- [x] Implementar integración con LLM (Ollama) para resolver nombres con bajo threshold
- [x] Actualizar tests unitarios con mocks de caché y llamadas LLM

### 19. Intelligent Chat RAG con Integración de ML (Completo)
- [x] Brainstorming y Diseño de Integración (Completo)
- [x] Refactorizar API para exponer cálculos de *Value Edge* en local
- [x] Inyectar resultados de ML y contexto matemático en Prompt de Chat
- [x] Aplicar Normalizador (Auto-Healing) sobre el input del usuario
- [x] Validar Chat E2E (Sin consumo de API externa)

### 20. Integración Dinámica de OpenRouter (Completo)
- [x] Brainstorming y Diseño de Integración (Completo)
- [x] Refactorizar `config.py` para cargar dinámicamente el modelo según `.env`
- [x] Configurar variables `OPENROUTER_API_KEY` y `LLM_MODEL_NAME`
- [x] Instalar soporte para OpenAI en LlamaIndex (`llama-index-llms-openai`)
- [x] Actualizar y ejecutar tests de configuración de RAG

### 21. Expansión Multi-Liga (Top 5 Europeas) (Completo)
- [x] Brainstorming y Diseño de Expansión Multi-Liga (Completo)
- [x] Configurar diccionario de IDs (`config.py`) para EPL, La Liga, Serie A, Bundesliga, Ligue 1
- [x] Parametrizar scraper de The-Odds-API y Understat
- [x] Refactorizar el cron de ingesta (`tasks.py`) para iterar sobre ligas
- [x] Refactorizar Ingesta Histórica y ML para entrenar multi-liga

### 22. Rate Limits y Prevención Anti-Bot (Completo)
- [x] Brainstorming y Diseño de Anti-Bloqueos (Completo)
- [x] Implementar pausas humanizadas y cabeceras en peticiones HTTP
- [x] Bloquear carga de recursos innecesarios en Playwright
- [x] Aislar errores para no romper el bucle masivo
- [x] Configurar reintentos exponenciales en endpoints problemáticos

### 23. Mitigación de Rate Limits del LLM (Completo)
- [x] Brainstorming y Diseño de LLM Rate Limits (Completo)
- [x] Aplicar `tenacity` a la llamada de `Settings.llm` en el Normalizador
- [x] Configurar backoff exponencial para salvar respuestas 429
- [x] Manejar `RetryError` en el bloque principal para evitar caídas
- [x] Asegurar que las pruebas pasen con la nueva arquitectura de reintentos

### 24. Mejoras de UI: Datos Completos y Menús Colapsables (Completo)
- [x] Brainstorming y Diseño de UI Completa y Menús
- [x] Actualizar endpoint `/api/dashboard` con data dinámica (hora y liga)
- [x] Actualizar interfaz en React y componentes de Partido para soportar nombres y UTC-5
- [x] Implementar menús laterales colapsables (`DashboardPanel` dinámico, `ChatPanel` colapsable)

### 25. Refinamiento de Calidad de ML y Scrapers (Completado)
- [x] Brainstorming y Diseño de Refinamiento de Calidad
- [x] Parametrizar ligas en scraper de Understat
- [x] Implementar validadores de suficiencia de historial
- [x] Mejorar Feature Engineering (Rolling Averages e Imputación de NaNs)
- [x] Actualizar modelo global y manejo de NaNs en entrenamiento

### 26. Ingesta de Datos 100% Reales (Pendiente)
- [x] Brainstorming y Diseño de Ingesta 100% Real
- [ ] Tolerancia Cero a Vacíos (Hard Fails en Understat contra Cloudflare)
- [ ] Cruce de datos Understat por Equipo y Año (sin usar Fecha)
- [ ] Descarga Masiva (Bulk Download) de Clubelo para evitar rate limits
- [ ] Actualización del motor de orquestación histórica

### 27. Migración a Scrapling y Sistema de Logs (En progreso)
- [x] Brainstorming y Diseño de Migración y Logging
- [x] Implementar sistema de logs centralizado (`loguru`)
- [x] Reemplazar Playwright por API/Requests en `understat_historical.py`
- [ ] Actualizar dependencias (remover Playwright completamente del proyecto, refactorizando `understat.py`)
- [x] Refactorizar scripts de ingesta para usar el nuevo logger en lugar de `print()`

### 28. Limpieza de Hardcodes y Mocks (Completo)
- [x] Brainstorming y Diseño de Limpieza del Backend
- [x] Remoción de Fallbacks y Keys Hardcodeadas (tasks.py)
- [x] Limpieza de Mocks en Reglas de Fiabilidad (reliability.py)
- [x] Limpieza de Archivos de Entorno y Configuración (.env)
- [x] Diseño y Plan de Frontend & Infra
- [x] Refactor Frontend a variables de entorno
- [x] Actualización Docker Compose

### 29. Optimización de Ingesta, ML y Frontend (Completo)
- [x] Brainstorming y Diseño de Optimizaciones
- [x] Implementar Ingesta Delta (Filtro por origen y Caché de Estado)
- [x] Añadir validación y umbrales de regresión al entrenamiento ML
- [x] Implementar Short Polling en el Frontend para actualizaciones en tiempo real

### 30. Entrenamiento de ML Continuo con Data Lake (Completo)
- [x] Brainstorming y Diseño de la Integración
- [x] Modificar pipeline de ML (`train.py`) para leer partidos finalizados desde el Data Lake (`data/raw/`)
- [x] Concatenar data histórica (`merged_history_cache.csv`) con datos recientes de la temporada en curso
- [x] Actualizar el orquestador de ingesta para automatizar el re-entrenamiento con toda la información disponible

### 31. Auditoría Integral de Datos y Almacenamiento (Completo)
- [x] Brainstorming y Diseño de la Auditoría
- [x] Implementar validador de integridad del Data Lake (`data/raw/`)
- [x] Implementar verificador estadístico del caché histórico (NaNs, distribuciones)
- [x] Implementar conteo y métricas de salud para bases de datos (SQLite, ChromaDB)
- [x] Generar un reporte Markdown unificado de auditoría (`docs/audits/`)

---

## Próximos pasos

| Acción | Tipo | Prioridad |
|--------|------|-----------|
| Testing manual E2E y Bugfixing | Manual/IA | Alta |
| Recolectar feedback de usuarios | Manual | Media |

---

## Archivos clave

BetWise/
├── AGENTS.md
├── docs/
│   ├── MASTER-PLAN.md
│   ├── SPEC.md
│   └── superpowers/
│       ├── specs/
│       └── plans/
---