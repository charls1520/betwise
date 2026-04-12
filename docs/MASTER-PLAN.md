---
# Master Plan — BetWise

**Última actualización:** 11 de Abril de 2026

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

### 7. Rediseño UI y Modelo Gemma (En progreso)
- [x] Brainstorming y Diseño UI/Gemma
- [ ] Actualizar LlamaIndex a Gemma4:26b
- [ ] Configurar Tema Tailwind Dark Mode
- [ ] Rediseñar Dashboard y ChatPanel

---

## Próximos pasos

| Acción | Tipo | Prioridad |
|--------|------|-----------|
| Ejecutar plan de Rediseño UI y Gemma | Con IA | Alta |
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