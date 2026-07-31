# Mapping DB

Web application for managing classification mapping: 84 sources → categories → 3D dimension mappings with vulnerability tags.

## Quick Start

```bash
cp .env.example .env
docker compose up -d
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Database: PostgreSQL 16 on `localhost:5432`

## Development

```bash
# Backend
cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn asyncpg pydantic pydantic-settings httpx
DATABASE_URL="postgresql://mapper:devpassword@localhost:5432/mapping" uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

## Backup

```bash
# Dump database
"/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe" exec mapping-pg pg_dump -U mapper mapping > backup_$(date +%Y%m%d).sql

# Restore
"/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe" exec -i mapping-pg psql -U mapper mapping < backup.sql
```
