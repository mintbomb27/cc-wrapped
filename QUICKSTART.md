# 🚀 Quick Start Guide

## Running with Docker (5 minutes)

### Step 1: Stop Local Dev Servers
If you have local dev servers running, stop them first:
```bash
# Stop the running processes in your terminals
# Or just close the terminal windows running uvicorn and vite
```

### Step 2: Validate Setup
```bash
./validate-docker.sh
```

### Step 3: Build and Run
```bash
docker-compose up --build
```

**That's it!** 🎉

Access the app at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

---

## Running Locally (Development)

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # or create venv if needed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

Access at http://localhost:5173 (Vite default port)

---

## Common Commands

### Docker
```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose up --build
```

### Makefile Shortcuts
```bash
make help              # Show all commands
make build && make up  # Build and start
make logs              # View logs
make down              # Stop services
make restart           # Restart
```

---

## Troubleshooting

**Port already in use?**
```bash
# Option 1: Stop local servers
# Option 2: Change ports in docker-compose.yaml
```

**Container won't start?**
```bash
docker-compose logs backend
docker-compose logs frontend
```

**Need to reset everything?**
```bash
docker-compose down -v
docker-compose up --build
```

---

## What's Next?

1. Upload a credit card statement PDF
2. View categorized transactions
3. Check the spending report
4. Upload multiple statements to see combined analysis

For more details, see:
- [DOCKER.md](DOCKER.md) - Complete Docker documentation
- [README.md](README.md) - Project overview
- [DOCKER_SETUP_SUMMARY.md](DOCKER_SETUP_SUMMARY.md) - Setup details
