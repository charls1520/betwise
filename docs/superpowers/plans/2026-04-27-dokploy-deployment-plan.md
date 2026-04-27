# Dokploy Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create production Dockerfiles and a Compose file for deploying the application via Dokploy using random ports.

**Architecture:** A multi-stage Docker build for the React frontend served by Nginx, and a production Dockerfile for the Python backend. Both orchestrated by a new `docker-compose.prod.yml` file, exposing high random ports.

**Tech Stack:** Docker, Nginx, Python (Uvicorn), React (Vite).

---

### Task 1: Create Production Backend Dockerfile

**Files:**
- Create: `backend/Dockerfile.prod`

- [ ] **Step 1: Write the Dockerfile.prod**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    scrapling install

# Copy application code
COPY . .

# Expose backend port
EXPOSE 8080

# Command to start the application in production mode without reload
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--loop", "asyncio"]
```

- [ ] **Step 2: Commit**

```bash
git add backend/Dockerfile.prod
git commit -m "feat: add production Dockerfile for backend"
```

### Task 2: Create Production Frontend Dockerfile

**Files:**
- Create: `frontend/Dockerfile.prod`
- Create: `frontend/nginx.conf`

- [ ] **Step 1: Write the Nginx configuration file**

```nginx
server {
    listen 80;
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
}
```

- [ ] **Step 2: Write the Dockerfile.prod**

```dockerfile
# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install

# Copy all files and build
COPY . .

RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:alpine

# Copy the built assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (internal to the container)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **Step 3: Commit**

```bash
git add frontend/Dockerfile.prod frontend/nginx.conf
git commit -m "feat: add production Dockerfile and nginx config for frontend"
```

### Task 3: Create Production Docker Compose File

**Files:**
- Create: `docker-compose.prod.yml`

- [ ] **Step 1: Write the docker-compose.prod.yml**

```yaml
services:
  db:
    image: postgres:15-alpine
    container_name: betwise_db_prod
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-betwise_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-betwise_db}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  chromadb:
    image: chromadb/chroma:latest
    container_name: betwise_chromadb_prod
    restart: unless-stopped
    volumes:
      - chroma_data:/chroma/chroma

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: betwise_backend_prod
    restart: unless-stopped
    ports:
      - "34568:8080" # Exposed random high port for backend
    volumes:
      - huggingface_cache:/root/.cache/huggingface
    environment:
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - CHROMA_SERVER_HOST=chromadb
      - CHROMA_SERVER_HTTP_PORT=8000
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL}
      - LLM_MODEL_NAME=${LLM_MODEL_NAME}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - EMBEDDING_MODEL_NAME=${EMBEDDING_MODEL_NAME}
      - ODDS_API_KEY=${ODDS_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
    depends_on:
      - db
      - chromadb

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        # Pass VITE_API_URL during build stage for static generation
        VITE_API_URL: ${VITE_API_URL}
    container_name: betwise_frontend_prod
    restart: unless-stopped
    ports:
      - "34567:80" # Exposed random high port for frontend
    environment:
      - VITE_API_URL=${VITE_API_URL}
    depends_on:
      - backend

volumes:
  postgres_data:
  chroma_data:
  huggingface_cache:
```

- [ ] **Step 2: Update frontend Dockerfile.prod to accept ARG**

We need to modify the frontend Dockerfile to use the ARG during the build process so React can embed it.

Modify `frontend/Dockerfile.prod` by adding `ARG VITE_API_URL` and `ENV VITE_API_URL=$VITE_API_URL` before `RUN npm run build`.

```dockerfile
# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install

# Copy all files and build
COPY . .

# Accept build argument for API URL
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:alpine

# Copy the built assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 (internal to the container)
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **Step 3: Commit**

```bash
git add docker-compose.prod.yml frontend/Dockerfile.prod
git commit -m "feat: add production docker-compose and update frontend builder with ARG"
```

### Task 4: Dokploy Deployment Instructions

**Files:**
- Create: `docs/DOKPLOY_DEPLOYMENT.md`

- [ ] **Step 1: Write the deployment guide**

```markdown
# Dokploy Deployment Guide for Betwise

This document provides step-by-step instructions on how to deploy Betwise to your VPS using Dokploy.

## Prerequisites
- A VPS running Dokploy.
- Your project hosted on GitHub.

## Steps to Deploy

1.  **Log in** to your Dokploy dashboard.
2.  Navigate to the **Projects** section and create a new project (e.g., `betwise-project`).
3.  Inside the project, click **Create Application**.
4.  Select **Compose** as the application type.
5.  **Configure the Application:**
    -   **Name:** Give it a name like `betwise-compose`.
    -   **Source:** Choose **GitHub**. Select your repository `charls1520/betwise`.
    -   **Branch:** Select the branch `betwise-estable`.
    -   **Compose Path:** Enter `./docker-compose.prod.yml`
6.  **Set Environment Variables:**
    Go to the **Environment** tab of your Compose application and paste all the variables from your `.env` file. 
    
    **Crucial Configuration:**
    Since you are not using a domain, set the `VITE_API_URL` to the public IP of your VPS and the backend port we defined (`34568`).
    
    ```env
    # Example Environment Variables
    POSTGRES_USER=betwise_user
    POSTGRES_PASSWORD=your_secure_password
    POSTGRES_DB=betwise_db
    
    OLLAMA_BASE_URL=http://your_ollama_url
    LLM_MODEL_NAME=llama3
    OPENROUTER_API_KEY=your_key
    EMBEDDING_MODEL_NAME=nomic-embed-text
    ODDS_API_KEY=your_key
    TELEGRAM_BOT_TOKEN=your_bot_token
    TELEGRAM_CHAT_ID=your_chat_id
    
    # IMPORTANT: Point this to your VPS Public IP and backend port 34568
    VITE_API_URL=http://<YOUR_VPS_PUBLIC_IP>:34568
    ```
7.  Click **Deploy** or **Save and Deploy**.
8.  Dokploy will build the Docker images and start the containers. Check the **Deployments** or **Logs** tab to see the progress.

## Accessing the Application

Once deployed successfully, you can access your application at:
- **Frontend:** `http://<YOUR_VPS_PUBLIC_IP>:34567`
- **Backend API:** `http://<YOUR_VPS_PUBLIC_IP>:34568`
```

- [ ] **Step 2: Update SPEC.md**

Update `docs/SPEC.md` to reflect the new deployment options.

```bash
# Add a brief section about deployment in docs/SPEC.md manually if it exists, otherwise just commit the guide.
```

- [ ] **Step 3: Commit**

```bash
git add docs/DOKPLOY_DEPLOYMENT.md
git commit -m "docs: add Dokploy deployment guide"
```
