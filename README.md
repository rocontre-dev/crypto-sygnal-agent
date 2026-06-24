# CryptoSignalAgent

A production-ready full-stack cryptocurrency signal analysis platform built with modern technologies.

## Project Description

CryptoSignalAgent is a comprehensive platform for cryptocurrency market analysis that provides:

- **Technical Analysis**: Calculate and analyze technical indicators
- **Signal Generation**: Generate trading signals based on market data
- **AI-Powered Explanations**: Get AI-generated explanations for trading signals
- **Backtesting**: Test strategies against historical data
- **Alerts**: Receive notifications via Telegram (future feature)

The platform is designed with clean architecture principles, ensuring maintainability, scalability, and separation of concerns.

## Tech Stack

### Frontend
- **React 18** - UI library
- **Vite 5** - Build tool and development server
- **TypeScript 5** - Type safety

### Backend
- **Python 3.12** - Programming language
- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations

### Database
- **PostgreSQL 15** - Relational database

### Containerization
- **Docker** - Container platform
- **Docker Compose** - Multi-container orchestration

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)

### Running with Docker Compose

1. Clone the repository:
```bash
git clone <repository-url>
cd CryptoSignalAgent
```

2. Start all services:
```bash
docker compose up --build
```

3. Access the applications:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

4. Stop all services:
```bash
docker compose down
```

### Local Development

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment file:
```bash
cp .env.example .env
```

5. Update the `.env` file with your configuration.

6. Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy environment file:
```bash
cp .env.example .env
```

4. Start the development server:
```bash
npm run dev
```

## Project Structure

```
CryptoSignalAgent/
├── frontend/                    # React + Vite + TypeScript frontend
│   ├── public/                  # Static assets
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API service layer
│   │   ├── hooks/               # Custom React hooks
│   │   ├── types/               # TypeScript type definitions
│   │   ├── assets/              # Images, fonts, etc.
│   │   ├── App.tsx              # Main application component
│   │   ├── main.tsx             # Application entry point
│   │   └── vite-env.d.ts        # Vite type declarations
│   ├── .env.example             # Environment variables template
│   ├── Dockerfile               # Docker configuration
│   ├── index.html               # HTML entry point
│   ├── package.json             # Node dependencies
│   ├── tsconfig.json            # TypeScript configuration
│   └── vite.config.ts           # Vite configuration
│
├── backend/                     # Python + FastAPI backend
│   ├── app/
│   │   ├── api/                 # API routes and endpoints
│   │   │   └── v1/              # API version 1
│   │   │       ├── health.py    # Health check endpoint
│   │   │       └── router.py    # Main API router
│   │   ├── core/                # Core configuration
│   │   │   ├── config.py        # Application settings
│   │   │   └── logging_config.py # Logging configuration
│   │   ├── models/              # SQLAlchemy database models
│   │   │   └── base.py          # Base model class
│   │   ├── schemas/             # Pydantic schemas
│   │   │   └── health.py        # Health response schema
│   │   ├── repositories/        # Data access layer
│   │   │   └── base.py          # Base repository
│   │   ├── services/            # Business logic layer
│   │   ├── utils/               # Utility functions
│   │   ├── config/              # Configuration files
│   │   ├── tests/               # Test files
│   │   ├── main.py              # FastAPI application entry
│   │   └── database.py          # Database connection
│   ├── .env.example             # Environment variables template
│   ├── Dockerfile               # Docker configuration
│   ├── requirements.txt         # Python dependencies
│   └── alembic.ini              # Alembic configuration
│
├── database/                    # Database initialization
│   └── init.sql                 # Database schema and tables
│
├── docs/                        # Documentation
│   ├── api.md                   # API documentation
│   ├── architecture.md          # Architecture overview
│   └── development.md           # Development guide
│
├── docker-compose.yml           # Docker Compose configuration
└── README.md                    # This file
```

## API Endpoints

### Health Check
- `GET /api/v1/health` - Check API health status

### Root
- `GET /` - Welcome message and API information

## Environment Variables

### Backend (.env)
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=crypto_signal
POSTGRES_USER=crypto_user
POSTGRES_PASSWORD=crypto_password
OPENAI_API_KEY=your-api-key-here
DEBUG=False
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## Future Modules

The architecture is prepared for the following future modules:

1. **Market Data Collector** - Collect price data from cryptocurrency exchanges
2. **Technical Indicators Engine** - Calculate RSI, MACD, Bollinger Bands, etc.
3. **Signal Engine** - Generate trading signals based on technical analysis
4. **AI Explanation Engine** - Generate AI-powered explanations for signals
5. **Telegram Alerts** - Send trading alerts via Telegram
6. **Backtesting** - Test strategies against historical data

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Database Migrations

The project uses Alembic for database migrations.

### Create a new migration
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback migrations
```bash
alembic downgrade -1
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.