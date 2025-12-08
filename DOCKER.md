# Docker Compose Setup

This guide explains how to run the Credit Card Wrapped application using Docker Compose.

## Prerequisites

- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)

## Quick Start

1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

3. **Stop the services:**
   ```bash
   docker-compose down
   ```

## Available Commands

### Start services in detached mode (background)
```bash
docker-compose up -d
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f backend
```

### Rebuild containers
```bash
docker-compose up --build
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (WARNING: This will delete your database)
```bash
docker-compose down -v
```

### Restart a specific service
```bash
docker-compose restart backend
docker-compose restart frontend
```

## Architecture

The Docker Compose setup includes:

- **Backend Service**: FastAPI application running on port 8000
  - Uses Gunicorn with Uvicorn workers for production
  - Persists database and uploads via volumes
  - Health checks enabled

- **Frontend Service**: Vite React app served by Nginx on port 3000 (mapped from container port 80)
  - Built as a static site
  - Nginx proxies `/api/*` requests to the backend
  - Optimized with gzip compression and caching

## Data Persistence

The following data is persisted using Docker volumes:
- `./backend/cc_wrapped.db` - SQLite database
- `./backend/uploads` - Uploaded PDF statements
- `./backend/model.pkl` - ML model for transaction categorization

## Networking

Both services are connected via a custom Docker network (`cc-wrapped-network`), allowing them to communicate using service names (e.g., `backend:8000`).

## Health Checks

Both services have health checks configured:
- Backend: Checks `/health` endpoint every 30 seconds
- Frontend: Checks Nginx is serving on port 80 every 30 seconds

## Troubleshooting

### Port already in use
If you get a port conflict error, you can change the ports in `docker-compose.yaml`:
```yaml
ports:
  - "3001:80"  # Change 3000 to 3001 for frontend
  - "8001:8000"  # Change 8000 to 8001 for backend
```

### Container won't start
Check the logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Database issues
If you need to reset the database:
```bash
docker-compose down
rm backend/cc_wrapped.db
docker-compose up
```

### Rebuild from scratch
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```
