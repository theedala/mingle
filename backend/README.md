# Mingle Backend

Privacy-first social matching platform API built with FastAPI.

## Tech Stack
- **FastAPI** - Async REST + WebSocket API
- **PostgreSQL** - User profiles, preferences, reputation
- **Redis** - Sessions, presence, caching, pub/sub
- **MongoDB** - Chat messages (flexible schema)
- **ClickHouse** - Analytics & ML data pipeline

## Setup

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv sync

# Start databases
docker-compose up -d

# Run migrations
uv run alembic upgrade head

# Start server
uv run uvicorn app.main:app --reload
```

## Project Structure
```
backend/
├── app/
│   ├── api/           # REST endpoints
│   ├── core/          # Config, security
│   ├── db/            # Database connections
│   ├── models/        # SQLAlchemy/Pydantic models
│   ├── matching/      # Algorithm engine
│   ├── chat/          # WebSocket handlers
│   ├── privacy/       # Anonymity logic
│   └── analytics/     # Data pipeline
├── tests/
├── alembic/           # Migrations
└── docker-compose.yml
```
