# Development Guide

This guide provides instructions for setting up a development environment and contributing to the CryptoSignalAgent project.

## Development Environment Setup

### Prerequisites

- **Docker** and **Docker Compose** - For containerized development
- **Python 3.12+** - For backend development
- **Node.js 20+** - For frontend development
- **Git** - For version control
- **PostgreSQL client tools** (optional) - For direct database access

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CryptoSignalAgent
   ```

2. **Set up environment variables**

   Backend:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Frontend:
   ```bash
   cd ../frontend
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services with Docker**
   ```bash
   docker compose up --build
   ```

### Backend Development

#### Local Setup (without Docker)

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Running Tests
```bash
pytest
pytest -v              # Verbose output
pytest --cov=app       # With coverage
```

#### Code Style
The project uses standard Python formatting. Consider using:
- `black` for code formatting
- `isort` for import sorting
- `flake8` for linting

### Frontend Development

#### Local Setup (without Docker)

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server**
   ```bash
   npm run dev
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

#### Running Tests
```bash
npm test
```

### Database Development

#### Connecting to the Database

Using `psql`:
```bash
psql -h localhost -p 5432 -U crypto_user -d crypto_signal
```

#### Running Migrations

The project uses Alembic for database migrations.

**Create a new migration:**
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

**Apply all migrations:**
```bash
alembic upgrade head
```

**Rollback one migration:**
```bash
alembic downgrade -1
```

**View migration history:**
```bash
alembic history
```

### Docker Development

#### Start all services
```bash
docker compose up
```

#### Start in detached mode
```bash
docker compose up -d
```

#### Stop all services
```bash
docker compose down
```

#### Stop and remove volumes (clean slate)
```bash
docker compose down -v
```

#### View logs
```bash
docker compose logs -f          # All services
docker compose logs -f backend  # Specific service
```

#### Run commands inside containers
```bash
docker compose exec backend bash
docker compose exec frontend sh
docker compose exec postgres psql -U crypto_user -d crypto_signal
```

#### Rebuild a specific service
```bash
docker compose build backend
docker compose up -d backend
```

### Debugging

#### Backend Debugging

Add breakpoints using Python's built-in debugger:
```python
import pdb; pdb.set_trace()
```

Or use an IDE with debugging support.

#### Frontend Debugging

Use browser developer tools. React Developer Tools extension is recommended.

#### Viewing Logs

```bash
# All logs
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend
```

## Common Issues and Solutions

### Port Already in Use

If ports 5173, 8000, or 5432 are already in use:

1. Find and kill the process:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F

   # Linux/Mac
   lsof -i :8000
   kill -9 <PID>
   ```

2. Or change the port in `docker-compose.yml`

### Database Connection Issues

1. Ensure PostgreSQL container is running:
   ```bash
   docker compose ps
   ```

2. Check database logs:
   ```bash
   docker compose logs postgres
   ```

3. Verify connection string in `.env`

### Frontend Build Issues

1. Clear node_modules and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Clear Vite cache:
   ```bash
   rm -rf node_modules/.vite
   ```

## Git Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

3. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Adding New Features

### New API Endpoint

1. Create route in `backend/app/api/v1/`
2. Add Pydantic schema in `backend/app/schemas/`
3. Add tests in `backend/app/tests/`
4. Update API documentation

### New React Component

1. Create component in `frontend/src/components/`
2. Add TypeScript types in `frontend/src/types/`
3. Write tests
4. Export from component index

### New Database Model

1. Create model in `backend/app/models/`
2. Create migration:
   ```bash
   alembic revision --autogenerate -m "Add new model"
   ```
3. Create repository in `backend/app/repositories/`
4. Add tests

## Performance Tips

- Use async operations where possible
- Implement proper database indexing
- Use connection pooling
- Enable caching where appropriate
- Optimize frontend bundle size

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)