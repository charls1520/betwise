# Dokploy Deployment Design

## Overview
This document specifies the design for deploying the Betwise project to a VPS using Dokploy. The deployment will use Dokploy's "Compose" feature, creating production-ready Docker images and mapping them to random ports for access via the server's public IP address, since a custom domain is not currently available.

## Architecture

The deployment will consist of four main services orchestrated via Docker Compose:
1.  **Frontend:** A React/Vite application built into static assets and served using a lightweight web server (e.g., Nginx or a lightweight Node.js server like `serve`).
2.  **Backend:** A Python backend running via an ASGI/WSGI server (e.g., Uvicorn or Gunicorn) to handle API requests and scheduled tasks.
3.  **Database (PostgreSQL):** Relational database for storing structured application data.
4.  **Vector Database (ChromaDB):** For storing and querying embeddings.

## Components to Create

### 1. Production Dockerfiles

Currently, the project uses `Dockerfile.dev` files optimized for local development with hot-reloading. For production, we need efficient, secure, and static builds.

*   `backend/Dockerfile.prod`:
    *   Base image: A lightweight Python image (e.g., `python:3.11-slim`).
    *   Action: Install dependencies from `requirements.txt`, copy application code.
    *   Command: Start the application using a production server (e.g., `uvicorn main:app --host 0.0.0.0 --port 8080`).
*   `frontend/Dockerfile.prod`:
    *   Base image (Builder): Node.js to install dependencies and run `npm run build`.
    *   Base image (Runner): Nginx (Alpine) to serve the static files generated in the `dist/` directory.
    *   Action: Multi-stage build to keep the final image size minimal.

### 2. Production Docker Compose File

A new file named `docker-compose.prod.yml` will be created in the root directory.

*   **Services:** `db`, `chromadb`, `backend`, and `frontend`.
*   **Build Contexts:** The `backend` and `frontend` services will point to their respective `Dockerfile.prod` files.
*   **Port Mapping (Random Ports):**
    *   Frontend will be mapped to a random, non-standard high port (e.g., `34567`) so it can be accessed via `http://<VPS_PUBLIC_IP>:34567`.
    *   Backend will be mapped to another non-standard port (e.g., `34568`).
*   **Environment Variables:** All secrets and configuration (database credentials, API keys, LLM settings, Telegram tokens) will be passed through environment variables configured within the Dokploy dashboard.
*   **Volumes:** Named volumes will be used for `postgres_data` and `chroma_data` to ensure data persistence across container restarts.

## Data Flow & Access

1.  The user accesses the application by navigating to `http://<VPS_PUBLIC_IP>:<FRONTEND_RANDOM_PORT>` in their browser.
2.  The Nginx container serves the static frontend assets.
3.  The frontend communicates with the backend API. To achieve this, the frontend must be built with the correct `VITE_API_URL` pointing to the public IP and the backend's mapped port (e.g., `http://<VPS_PUBLIC_IP>:<BACKEND_RANDOM_PORT>`). This variable must be set during the Dokploy build process.
4.  The backend communicates internally with the PostgreSQL and ChromaDB containers using Docker's internal network (e.g., `db:5432` and `chromadb:8000`).

## Dokploy Configuration Strategy

The actual deployment steps to be executed by the user in the Dokploy dashboard will be documented in the implementation plan. The general strategy is:
1.  Create a "Compose" application in Dokploy.
2.  Link the GitHub repository and specify the `betwise-estable` branch.
3.  Set the Compose file path to `./docker-compose.prod.yml`.
4.  Inject all necessary `.env` variables directly into the Dokploy UI before deploying.

## Error Handling & Reliability

*   **Restart Policies:** All services in `docker-compose.prod.yml` will have `restart: always` or `restart: unless-stopped` to ensure they recover from crashes or server reboots.
*   **Logs:** Dokploy handles container logs automatically, allowing the user to view backend and frontend logs directly from the dashboard.