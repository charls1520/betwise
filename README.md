# BetWise

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