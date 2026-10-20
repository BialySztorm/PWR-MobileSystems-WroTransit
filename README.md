# WroTransit

WroTransit is a monorepo for a real-time public transport tracker for Wrocław.

## Structure

- `app/` – Flutter mobile app skeleton
- `backend/` – FastAPI backend skeleton
- `docker-compose.yml` – local infrastructure for db/api/ingest

## Requirements

- Flutter SDK (stable)
- Python 3.12
- Docker + Docker Compose

## Run mobile app

```bash
cd app
flutter pub get
flutter run
```

## Run backend locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn api.main:app --reload
```

## Run with Docker Compose

```bash
docker compose up --build
```

## Tests

```bash
cd backend
pytest
```
