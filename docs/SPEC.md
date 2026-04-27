---
# Spec — BetWise

**Última actualización:** 11 de Abril de 2026

---

## Descripción

BetWise es un asistente de apuestas deportivas híbrido para la Premier League. Combina un dashboard con predicciones automáticas basadas en Machine Learning para diversos mercados y una interfaz interactiva de chat soportada por una arquitectura RAG (Retrieval-Augmented Generation) para responder a consultas complejas utilizando noticias recientes y estadísticas.

---

## Features

- **Arquitectura Base**: Backend FastAPI con base de datos relacional (SQLite) y frontend React.
- **UI & Dashboard**: Interfaz dinámica con paneles laterales colapsables, visualización de nombres completos de equipos, ligas dinámicas, y hora del partido ajustada a zona horaria local (UTC-5).
- **Motor de Ingesta (Data Lake -> ETL)**: Pipeline que permite guardar datos crudos en JSON y normalizar los nombres de los equipos con `thefuzz` antes de pasarlos a la base de datos relacional.
- **Motor RAG (LlamaIndex)**: Integración local de LlamaIndex con embeddings de HuggingFace, base de datos vectorial ChromaDB y LLM Ollama para responder consultas sobre contexto no estructurado.
- **Motor de Machine Learning**: Modelos estadísticos independientes (`scikit-learn`) para predecir probabilidades en mercados de Ganador (1X2) y Goles Totales (Over/Under) en base a Goles Esperados (xG), Elo, métricas de fatiga (días de descanso), estadísticas recientes de tiro (tiros a puerta), e indicadores de fin de temporada.
- **Notificador Telegram**: Sistema de alertas integradas al pipeline diario que envía de forma individual todos los pronósticos procesados (incluyendo alerta verde para predicciones con `Value Edge`) a un canal privado, garantizando rate limits y retry handling robustos.

---

## Arquitectura

- **Backend**: FastAPI (Python) que expone una API REST para el frontend.
- **Frontend**: React (Vite) en TypeScript.
- **Base de Datos**: PostgreSQL para persistencia relacional (Equipos).
- **Base de Datos Vectorial**: ChromaDB local.
- **Enfoque de Arquitectura**: Monolito Python ("Python-First") que sirve datos y maneja los procesos de IA (LlamaIndex + Ollama) y web scraping.
- **Infraestructura Local**: Docker y Docker Compose para orquestar el entorno de desarrollo (PostgreSQL, ChromaDB, Frontend y Backend), manteniendo Ollama ejecutado nativamente en la máquina host.

---

## Tecnologías

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, pytest, thefuzz, python-Levenshtein, scikit-learn, pandas, numpy, joblib.
- **RAG & IA**: LlamaIndex, Ollama (ejecutado en host), HuggingFace.
- **Frontend**: Node.js 20+, React, Vite, TypeScript, Tailwind CSS.
- **Base de datos**: PostgreSQL, ChromaDB.
- **Infraestructura**: Docker, Docker Compose.
---