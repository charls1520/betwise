# Dockerización del Proyecto Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dockerizar el entorno de desarrollo local para BetWise incluyendo Frontend, Backend, PostgreSQL y ChromaDB, manteniendo Ollama de forma nativa.

**Architecture:** Múltiples contenedores orquestados vía `docker-compose.yml`. Los servicios de frontend (Vite) y backend (FastAPI) usarán volúmenes mapeados para hot-reloading. Se empleará un archivo `.env` centralizado para la configuración.

**Tech Stack:** Docker, Docker Compose, PostgreSQL, ChromaDB, FastAPI, React/Vite.

---

### Task 1: Configurar Variables de Entorno y `.gitignore`

**Files:**
- Create: `.env.example`
- Modify: `.gitignore` (raíz del proyecto, si no existe crearlo)

- [ ] **Step 1: Crear archivo de ejemplo de variables de entorno**

Crea el archivo `.env.example` en la raíz del proyecto.

```env
# Configuración de Base de Datos PostgreSQL
POSTGRES_USER=betwise_user
POSTGRES_PASSWORD=betwise_password
POSTGRES_DB=betwise_db

# Configuración de ChromaDB
CHROMA_SERVER_HOST=chromadb
CHROMA_SERVER_HTTP_PORT=8000

# Configuración de Modelos de IA (Ollama local)
# En Windows/Mac, host.docker.internal apunta a la máquina host
OLLAMA_BASE_URL=http://host.docker.internal:11434
LLM_MODEL_NAME=llama3
EMBEDDING_MODEL_NAME=nomic-embed-text

# Configuración del Frontend
VITE_API_URL=http://localhost:8080
```

- [ ] **Step 2: Asegurar que `.env` esté ignorado en git**

Modifica (o crea) el archivo `.gitignore` en la raíz del proyecto para incluir:

```gitignore
# Variables de entorno
.env
```

- [ ] **Step 3: Commit de la configuración de entorno**

```bash
git add .env.example .gitignore
git commit -m "chore: setup environment variables and gitignore"
```

---

### Task 2: Crear archivos `.dockerignore`

**Files:**
- Create: `backend/.dockerignore`
- Create: `frontend/.dockerignore`

- [ ] **Step 1: Crear `.dockerignore` para el backend**

Crea `backend/.dockerignore`:

```dockerignore
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.venv/
venv/
env/
.env
```

- [ ] **Step 2: Crear `.dockerignore` para el frontend**

Crea `frontend/.dockerignore`:

```dockerignore
node_modules/
dist/
.env
```

- [ ] **Step 3: Commit de los archivos ignore**

```bash
git add backend/.dockerignore frontend/.dockerignore
git commit -m "chore: add dockerignore files"
```

---

### Task 3: Crear Dockerfile de Desarrollo para Backend

**Files:**
- Create: `backend/Dockerfile.dev`

- [ ] **Step 1: Escribir el Dockerfile del backend**

Crea el archivo `backend/Dockerfile.dev`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# El código se montará vía volumen en docker-compose, no copiamos aquí.
# Comando de inicio con hot-reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
```

- [ ] **Step 2: Commit del Dockerfile del backend**

```bash
git add backend/Dockerfile.dev
git commit -m "build: add dev Dockerfile for backend"
```

---

### Task 4: Crear Dockerfile de Desarrollo para Frontend

**Files:**
- Create: `frontend/Dockerfile.dev`

- [ ] **Step 1: Escribir el Dockerfile del frontend**

Crea el archivo `frontend/Dockerfile.dev`:

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install

# El código se montará vía volumen en docker-compose
# Comando de inicio exponiendo el host
CMD ["npm", "run", "dev", "--", "--host"]
```

- [ ] **Step 2: Commit del Dockerfile del frontend**

```bash
git add frontend/Dockerfile.dev
git commit -m "build: add dev Dockerfile for frontend"
```

---

### Task 5: Crear orquestación con `docker-compose.yml`

**Files:**
- Create: `docker-compose.yml`

- [ ] **Step 1: Escribir el archivo `docker-compose.yml`**

Crea el archivo `docker-compose.yml` en la raíz del proyecto:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: betwise_db
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-betwise_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-betwise_password}
      POSTGRES_DB: ${POSTGRES_DB:-betwise_db}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  chromadb:
    image: chromadb/chroma:latest
    container_name: betwise_chromadb
    restart: always
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    container_name: betwise_backend
    ports:
      - "8080:8080"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER:-betwise_user}:${POSTGRES_PASSWORD:-betwise_password}@db:5432/${POSTGRES_DB:-betwise_db}
      - CHROMA_SERVER_HOST=chromadb
      - CHROMA_SERVER_HTTP_PORT=8000
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL}
      - LLM_MODEL_NAME=${LLM_MODEL_NAME}
      - EMBEDDING_MODEL_NAME=${EMBEDDING_MODEL_NAME}
    depends_on:
      - db
      - chromadb

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: betwise_frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=${VITE_API_URL:-http://localhost:8080}
    depends_on:
      - backend

volumes:
  postgres_data:
  chroma_data:
```

- [ ] **Step 2: Commit de `docker-compose.yml`**

```bash
git add docker-compose.yml
git commit -m "build: setup docker-compose for local development"
```

---

### Task 6: Actualizar Documentación (SPEC y MASTER-PLAN)

**Files:**
- Modify: `docs/SPEC.md`
- Modify: `docs/MASTER-PLAN.md`

- [ ] **Step 1: Actualizar `docs/SPEC.md`**

Si el archivo `docs/SPEC.md` existe, actualiza la sección de "Tecnologías usadas" y "Estructura actual" para incluir Docker y Docker Compose, indicando que se usa para desarrollo local y detallando los servicios (PostgreSQL, ChromaDB, Backend, Frontend).

- [ ] **Step 2: Actualizar `docs/MASTER-PLAN.md`**

Si el archivo `docs/MASTER-PLAN.md` existe, marca el paso de "Dockerizar el entorno de desarrollo" como completado (o añádelo si no existía).

- [ ] **Step 3: Commit de la documentación del proyecto**

```bash
# Asumiendo que los archivos existen, modifica esto según sea necesario
git add docs/SPEC.md docs/MASTER-PLAN.md
git commit -m "docs: update SPEC and MASTER-PLAN with docker setup"
```

---

### Task 7: Actualizar `README.md`

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Añadir instrucciones de ejecución**

Edita el archivo `README.md` y añade o reemplaza la sección "Cómo ejecutar":

```markdown
## Cómo ejecutar

El proyecto utiliza Docker para facilitar el desarrollo local. Asegúrate de tener Docker y Docker Compose instalados.

1. Copia el archivo de configuración de entorno y ajústalo si es necesario (especialmente importante para configurar el acceso a Ollama local):
   ```bash
   cp .env.example .env
   ```

2. Levanta todos los servicios:
   ```bash
   docker-compose up -d --build
   ```

Esto iniciará:
- **Frontend:** http://localhost:5173
- **Backend (API):** http://localhost:8080
- **PostgreSQL:** localhost:5432
- **ChromaDB:** localhost:8000

Para detener los servicios:
```bash
docker-compose down
```
```

- [ ] **Step 2: Commit del README**

```bash
git add README.md
git commit -m "docs: add docker instructions to README"
```
