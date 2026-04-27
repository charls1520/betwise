# BetWise ⚽🤖

BetWise es una plataforma avanzada de análisis y predicción de apuestas deportivas enfocada en el fútbol europeo. Utiliza modelos de Machine Learning y una arquitectura RAG (Retrieval-Augmented Generation) para ofrecer sugerencias de apuestas con valor matemático ("Value Edge") y un asistente conversacional inteligente.

## 🌟 Características Principales

*   **Motor de Ingestión Automático:** Recolección diaria de cuotas (Odds API), estadísticas avanzadas (Understat xG) y ratings históricos (Clubelo).
*   **Modelos de Machine Learning:** Predicción de probabilidades reales de partidos utilizando Gradient Boosting y Random Forest, ajustados semanalmente.
*   **Detección de Apuestas de Valor (Value Edge):** Comparación automatizada entre las probabilidades inferidas por el modelo y las cuotas de las casas de apuestas para identificar oportunidades matemáticas rentables.
*   **Asistente Inteligente (RAG):** Chatbot potenciado por LLMs de código abierto (vía Ollama o LlamaIndex) que responde preguntas sobre los próximos partidos basándose en el contexto en tiempo real y noticias scrapeadas.
*   **Panel de Control en Tiempo Real:** Dashboard interactivo desarrollado en React/Vite para visualizar partidos próximos y sugerencias de apuestas.

---

## 🏗️ Arquitectura del Sistema

*   **Frontend:** React, Vite, TailwindCSS.
*   **Backend:** FastAPI (Python), APScheduler (Cron Jobs integrados).
*   **Base de Datos Relacional:** PostgreSQL (Datos estructurados, perfiles, logs).
*   **Base de Datos Vectorial:** ChromaDB (Almacenamiento de embeddings para RAG).
*   **Orquestación:** Docker y Docker Compose.

---

## 🚀 Cómo Ejecutar en Entorno Local (Desarrollo)

El proyecto utiliza Docker para facilitar el desarrollo local con recarga en caliente (hot-reload). Asegúrate de tener Docker y Docker Compose instalados.

1. **Configurar el Entorno:**
   Copia el archivo de configuración de entorno y ajústalo con tus claves API (Odds API, OpenRouter, etc.):
   ```bash
   cp .env.example .env
   ```

2. **Levantar los Servicios:**
   ```bash
   docker-compose up -d --build
   ```

Esto iniciará los servicios locales:
*   **Frontend:** `http://localhost:5173`
*   **Backend (API):** `http://localhost:8080`
*   **PostgreSQL:** `localhost:5432`
*   **ChromaDB:** `localhost:8000`

Para detener los servicios:
```bash
docker-compose down
```

---

## 🌍 Despliegue en Producción (VPS / Dokploy)

Para desplegar la aplicación en un VPS utilizando un orquestador como **Dokploy**, se han creado configuraciones optimizadas para producción (`Dockerfile.prod` y `docker-compose.prod.yml`).

1. En el panel de Dokploy, crea una nueva aplicación basada en Docker Compose.
2. Como ruta del archivo Compose, especifica: `docker-compose.prod.yml`
3. En la sección **Environment**, pega todas las variables de tu archivo `.env`.
   * **¡Importante!** Asegúrate de definir `VITE_API_URL` apuntando a la IP pública o dominio de tu backend (ej. `http://<IP-VPS>:8080` o `https://api.midominio.com`).
4. Inicia el despliegue.

Esta configuración utiliza Nginx para servir el Frontend estático compilado y desactiva el hot-reload en el Backend para máximo rendimiento.

---

## ⚙️ Comandos Útiles dentro del Contenedor (Producción)

Dado que los procesos de scraping y entrenamiento están programados internamente con APScheduler, normalmente no necesitas ejecutarlos manualmente. Sin embargo, si necesitas forzar una actualización:

**Entrenamiento Manual del Modelo de ML:**
```bash
docker exec -it betwise_backend_prod bash -c "export PYTHONPATH='/app' && python src/ml/train.py"
```

**Ejecución Manual del Scraping (Ingestión):**
```bash
docker exec -it betwise_backend_prod bash -c "export PYTHONPATH='/app' && python src/ingestion/tasks.py"
```

*(Nota: En desarrollo local, el nombre del contenedor es `betwise_backend` en lugar de `betwise_backend_prod`).*

---

## 📝 Licencia y Contacto

Desarrollado para análisis predictivo en mercados deportivos.
