---
# Spec — BetWise

**Última actualización:** 11 de Abril de 2026

---

## Descripción

BetWise es un asistente de apuestas deportivas híbrido para la Premier League. Combina un dashboard con predicciones automáticas basadas en Machine Learning para diversos mercados y una interfaz interactiva de chat soportada por una arquitectura RAG (Retrieval-Augmented Generation) para responder a consultas complejas utilizando noticias recientes y estadísticas.

---

## Features

- **Arquitectura Base**: Backend FastAPI con base de datos relacional (SQLite) y frontend React.
- **Motor de Ingesta (Data Lake -> ETL)**: Pipeline que permite guardar datos crudos en JSON y normalizar los nombres de los equipos con `thefuzz` antes de pasarlos a la base de datos relacional.

---

## Arquitectura

- **Backend**: FastAPI (Python) que expone una API REST para el frontend.
- **Frontend**: React (Vite) en TypeScript.
- **Base de Datos**: SQLite para el desarrollo inicial de modelos relacionales (Equipos).
- **Enfoque de Arquitectura**: Monolito Python ("Python-First") que sirve datos y en un futuro manejará los procesos de IA y web scraping.

---

## Tecnologías

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, pytest, thefuzz, python-Levenshtein.
- **Frontend**: Node.js, React, Vite, TypeScript.
- **Base de datos**: SQLite.
---