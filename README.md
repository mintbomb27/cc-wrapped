# Credit Card Wrapped 💳
#### Generated using: Antigravity + Claude Sonnet 4.5

A comprehensive credit card statement analyzer that helps you understand your spending patterns, categorize transactions, and generate insightful reports.

## Features

- 📊 **Transaction Analysis**: Upload credit card statements (PDF) and automatically parse transactions
- 🏷️ **Smart Categorization**: ML-powered transaction categorization
- 💰 **Accurate Spend Tracking**: Excludes bill payments and includes cashback in reports
- 📈 **Detailed Reports**: Get insights into your spending by category
- 📁 **Multi-Statement Support**: Upload and analyze multiple statements at once

## Quick Start with Docker (Recommended)

The easiest way to run the application is using Docker Compose:

```bash
# Build and start all services
docker-compose up --build

# Or use the Makefile
make build
make up
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

For detailed Docker instructions, see [DOCKER.md](DOCKER.md).

## Manual Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the backend server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

## Project Structure

```
cc-wrapped/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── core/        # Core configurations
│   │   ├── models/      # Database models
│   │   └── services/    # Business logic
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # React + Vite frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── lib/        # Utilities and API client
│   │   └── App.jsx     # Main app component
│   ├── Dockerfile
│   └── nginx.conf      # Nginx configuration for production
├── docker-compose.yaml  # Docker Compose configuration
├── Makefile            # Convenient make commands
└── DOCKER.md           # Detailed Docker documentation
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **PDFPlumber**: PDF parsing
- **Scikit-learn**: Machine learning for categorization
- **Gunicorn + Uvicorn**: Production ASGI server

### Frontend
- **React**: UI library
- **Vite**: Build tool and dev server
- **Axios**: HTTP client
- **TailwindCSS**: Utility-first CSS framework
- **Nginx**: Production web server

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check endpoint
- `GET /api/v1/cards/` - List all cards
- `POST /api/v1/cards/` - Create a new card
- `POST /api/v1/cards/{card_id}/upload-statement/` - Upload statement(s)
- `GET /api/v1/cards/{card_id}/transactions/` - Get transactions for a card
- `GET /api/v1/cards/{card_id}/report/` - Get spending report for a card

## Development

### Using Make Commands

```bash
make help              # Show all available commands
make build             # Build Docker images
make up                # Start services
make up-detached       # Start in background
make logs              # View logs
make logs-backend      # View backend logs only
make restart           # Restart all services
make clean             # Stop and remove volumes
make test              # Test if services are responding
```

### Running Tests

```bash
# Backend tests (if available)
cd backend
pytest

# Frontend tests (if available)
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.
