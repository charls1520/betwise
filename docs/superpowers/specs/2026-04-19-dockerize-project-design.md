# Design Spec: Dockerización del Proyecto (Entorno de Desarrollo)

## Contexto
El objetivo es dockerizar el proyecto "BetWise" para un entorno de **desarrollo local** (Opción 1: Todo en Docker). El proyecto consta de:
- **Backend:** FastAPI (Python)
- **Frontend:** React + Vite (Node.js)
- **Servicios de Datos Adicionales:** PostgreSQL y ChromaDB.
- **Modelos de IA Locales:** Ollama (se asume que se ejecutará fuera de Docker o se conectará a la red host debido a requisitos de GPU, pero se configurará la red para permitir el acceso).

## Arquitectura de Contenedores

Se utilizará `docker-compose.yml` para orquestar los siguientes servicios:

### 1. `db` (PostgreSQL)
- **Imagen:** `postgres:15-alpine` (ligera).
- **Volumen:** Volumen con nombre `postgres_data` para persistencia de datos entre reinicios del contenedor.
- **Variables de entorno:** Configuración básica de usuario, contraseña y nombre de la base de datos (por ejemplo, `POSTGRES_USER=user`, `POSTGRES_PASSWORD=pass`, `POSTGRES_DB=betwise`).
- **Puertos:** Expuesto en `5432:5432`.

### 2. `chromadb`
- **Imagen:** `chromadb/chroma:latest`
- **Volumen:** Volumen con nombre `chroma_data` para persistencia de la base de datos vectorial.
- **Puertos:** Expuesto en `8000:8000`.

### 3. `backend` (FastAPI)
- **Dockerfile:** `backend/Dockerfile.dev` (o `Dockerfile` multipropósito).
- **Imagen base:** `python:3.11-slim` (o la versión específica requerida por las dependencias).
- **Comando:** `uvicorn main:app --host 0.0.0.0 --port 8080 --reload` (hot-reloading activado).
- **Volumen:** Mapeo del directorio `./backend` a `/app` dentro del contenedor para sincronizar cambios en el código en tiempo real.
- **Dependencias:** Instalación desde `requirements.txt`.
- **Variables de entorno:** Conexiones a `db`, `chromadb` y configuración de Ollama (ej. apuntando a `host.docker.internal` si Ollama corre en la máquina host).
- **Puertos:** Expuesto en `8080:8080`.
- **Redes:** Depende de `db` y `chromadb`.

### 4. `frontend` (React + Vite)
- **Dockerfile:** `frontend/Dockerfile.dev` (o `Dockerfile` multipropósito).
- **Imagen base:** `node:20-alpine` (o versión actual LTS).
- **Comando:** `npm run dev -- --host` (para que Vite escuche en todas las interfaces).
- **Volumen:** Mapeo del directorio `./frontend` a `/app` (excluyendo o gestionando `node_modules` mediante un volumen anónimo para evitar conflictos con módulos de Windows/Mac).
- **Dependencias:** Instalación mediante `npm install` basada en `package.json`.
- **Puertos:** Expuesto en `5173:5173` (puerto por defecto de Vite).
- **Variables de entorno:** URLs de la API del backend.

## Flujo de Trabajo (Hot Reload)
Al modificar código en `./backend` o `./frontend` en la máquina host, los volúmenes mapeados reflejarán los cambios dentro del contenedor. FastAPI y Vite detectarán estos cambios y se recargarán automáticamente, permitiendo un desarrollo fluido sin necesidad de reconstruir las imágenes constantemente.

## Archivos a Crear o Modificar
1. `docker-compose.yml` (raíz del proyecto).
2. `backend/Dockerfile.dev`
3. `frontend/Dockerfile.dev`
4. `.dockerignore` (en frontend y backend para ignorar `node_modules`, `__pycache__`, entornos virtuales, etc.).
5. Actualización de `docs/SPEC.md` y `docs/MASTER-PLAN.md` (según las reglas del proyecto).
6. Actualización del `README.md` con las instrucciones de ejecución (`docker-compose up -d --build`).

## Consideraciones Adicionales
- **Ollama:** Si usas Ollama localmente para los embeddings o el LLM, el backend en Docker necesitará acceder a `localhost` de tu máquina física. En Windows/Mac con Docker Desktop, esto se hace configurando la URL de Ollama como `http://host.docker.internal:11434`.
- **Variables de Entorno:** Se recomendará usar un archivo `.env` en la raíz (y posiblemente en backend/frontend) para gestionar las credenciales y URLs.

---
*Revisión de Spec completada: Sin placeholders, la arquitectura coincide con la Opción 1 seleccionada, el alcance es claro.*