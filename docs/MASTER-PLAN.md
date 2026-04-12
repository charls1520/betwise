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

### 2. Motor de Ingesta y Normalización (En progreso)
- [x] Brainstorming y Diseño
- [ ] Scripts de scraping para estadísticas y cuotas
- [ ] Motor de normalización difusa de nombres de equipos
- [ ] Automatización (Cron Jobs) de actualización diaria

### 3. Motor RAG y ML (Pendiente)
- [ ] Integración de LlamaIndex y base de datos vectorial para noticias
- [ ] Entrenamiento de modelo ML ligero para predicciones
- [ ] Interfaz de chat en el Frontend

---

## Próximos pasos

| Acción | Tipo | Prioridad |
|--------|------|-----------|
| Ejecutar plan de Ingesta y Normalización | Con IA | Alta |
| Configurar LlamaIndex | Con IA | Media |

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