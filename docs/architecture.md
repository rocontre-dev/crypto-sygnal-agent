# Architecture Overview

This document describes the architecture of the CryptoSignalAgent platform.

## Design Principles

The platform is built following these key principles:

1. **Clean Architecture** - Separation of concerns with distinct layers
2. **SOLID Principles** - Maintainable and scalable code
3. **Type Safety** - TypeScript on frontend, Pydantic on backend
4. **Async First** - Asynchronous operations for better performance
5. **Containerization** - Docker for consistent environments

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│    Frontend     │────▶│     Backend     │────▶│    Database     │
│   (React/Vite)  │     │   (FastAPI)     │     │  (PostgreSQL)   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Backend Architecture

The backend follows a layered architecture pattern with a domain-driven design approach:

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                             │
│  (Routes, Request/Response handling, Validation)             │
├─────────────────────────────────────────────────────────────┤
│                      Services Layer                          │
│  (Business Logic, Orchestration)                             │
├─────────────────────────────────────────────────────────────┤
│                     Domain Layer                             │
│  (Entities, Enums, Exceptions, Interfaces)                   │
├─────────────────────────────────────────────────────────────┤
│                    Repository Layer                          │
│  (Data Access, CRUD Operations)                              │
├─────────────────────────────────────────────────────────────┤
│                       Models Layer                           │
│  (Database Models, Entities)                                 │
└─────────────────────────────────────────────────────────────┘
```

### Layer Descriptions

#### API Layer (`app/api/`)
- Handles HTTP requests and responses
- Route definitions
- Request validation
- Response serialization

#### Services Layer (`app/services/`)
- Business logic implementation
- Orchestration between repositories
- External API integrations
- Complex computations

#### Domain Layer (`app/domain/`)
The domain layer is the heart of the application, containing core business logic:

- **Entities** (`domain/entities/`) - Core business objects with identity and behavior
- **Enums** (`domain/enums/`) - Type-safe constants for fixed value sets
- **Exceptions** (`domain/exceptions/`) - Domain-specific error classes
- **Interfaces** (`domain/interfaces/`) - Abstract contracts for services and repositories

#### Repository Layer (`app/repositories/`)
- Data access abstraction
- CRUD operations
- Query building
- Transaction management

#### Models Layer (`app/models/`)
- Database table definitions
- Entity relationships
- Base model with common fields

## Frontend Architecture

The frontend follows a component-based architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                        Pages Layer                           │
│  (Page components, Route handling)                           │
├─────────────────────────────────────────────────────────────┤
│                     Components Layer                         │
│  (Reusable UI components)                                    │
├─────────────────────────────────────────────────────────────┤
│                      Services Layer                          │
│  (API calls, External integrations)                          │
├─────────────────────────────────────────────────────────────┤
│                        Hooks Layer                           │
│  (Custom React hooks, State management)                      │
├─────────────────────────────────────────────────────────────┤
│                         Types Layer                          │
│  (TypeScript type definitions)                               │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

The database is designed to support future modules:

```
┌──────────────────┐    ┌──────────────────────┐
│   market_data    │    │ technical_indicators │
├──────────────────┤    ├──────────────────────┤
│ id               │    │ id                   │
│ symbol           │    │ symbol               │
│ timestamp        │    │ indicator_type       │
│ open_price       │    │ timeframe            │
│ high_price       │    │ timestamp            │
│ low_price        │    │ value                │
│ close_price      │    │ created_at           │
│ volume           │    │ updated_at           │
│ created_at       │    └──────────────────────┘
│ updated_at       │
└──────────────────┘    ┌──────────────────────┐
                        │       signals        │
┌──────────────────┐    ├──────────────────────┤
│ ai_explanations  │    │ id                   │
├──────────────────┤    │ symbol               │
│ id               │    │ signal_type          │
│ signal_id (FK)   │    │ strength             │
│ explanation      │    │ timestamp            │
│ model_version    │    │ explanation          │
│ created_at       │    │ created_at           │
│ updated_at       │    │ updated_at           │
└──────────────────┘    └──────────────────────┘

┌──────────────────┐
│ backtest_results │
├──────────────────┤
│ id               │
│ strategy_name    │
│ start_date       │
│ end_date         │
│ initial_capital  │
│ final_capital    │
│ total_return     │
│ sharpe_ratio     │
│ max_drawdown     │
│ total_trades     │
│ winning_trades   │
│ losing_trades    │
│ created_at       │
│ updated_at       │
└──────────────────┘
```

## Technology Decisions

### Why FastAPI?
- High performance (on par with Node.js and Go)
- Automatic API documentation
- Type validation with Pydantic
- Async support out of the box

### Why React + Vite?
- Fast development with HMR
- Excellent TypeScript support
- Large ecosystem
- Component reusability

### Why PostgreSQL?
- Reliable and battle-tested
- Excellent for complex queries
- JSON support for flexible data
- Strong consistency guarantees

## Security Considerations

- CORS configuration for cross-origin requests
- Environment variables for sensitive data
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy ORM

## Scalability

The architecture supports horizontal scalability:
- Stateless backend services
- Database connection pooling
- Async operations for high concurrency
- Container-based deployment