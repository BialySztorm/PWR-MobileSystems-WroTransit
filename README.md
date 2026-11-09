# WroTransit

WroTransit is a monorepo for a real-time public transport tracker for Wrocław.

## Structure

- `app/` – Flutter mobile app
- `backend/` – FastAPI backend, PostGIS data model, GTFS import
- `docker-compose.yml` – local infrastructure for db/api/ingest

## Requirements

- Flutter SDK (stable) — Windows/web/Android platforms are set up; see `flutter doctor` for
  what's installed on your machine
- Python 3.12
- Docker + Docker Compose (PostgreSQL 16 + PostGIS)

## 1. Database

```bash
docker compose up -d db
cd backend
python -m venv ../.venv && ../.venv/Scripts/pip install -e .[dev]   # or: uv venv ../.venv && uv pip install -p ../.venv -e .[dev]
../.venv/Scripts/python -m alembic -c db/migrations/alembic.ini upgrade head
```

Tests run against a second, separate database so they never touch your dev data:

```bash
docker compose exec db psql -U wrotransit -d wrotransit -c "CREATE DATABASE wrotransit_test;"
```

## 2. GTFS data

The import script reads a local archive — it does not download anything itself, because the
official `wroclaw.pl/open-data` feed blocks automated requests (Cloudflare bot protection).

1. Download the current feed, e.g. from the [Mobility Database mirror](https://mobilitydatabase.org/feeds/gtfs/mdb-980)
   (refreshed daily) or the city's open data portal.
2. Save it as `backend/data/wroclaw.gtfs.zip` (gitignored — this file is never committed).
3. Import it:
   ```bash
   cd backend
   python -m ingest.gtfs_import
   ```
   This rebuilds the schedule tables (`stops`, `routes`, `trips`, `stop_times`, `shapes`,
   `calendar*`) from scratch every time it's run — safe to re-run after downloading a fresher
   archive.

## 3. Run backend locally

```bash
cd backend
../.venv/Scripts/python -m uvicorn api.main:app --reload   # or activate .venv first and drop the prefix
```

## 4. Run mobile app

```bash
cd app
flutter pub get
flutter run            # or: flutter run -d windows / -d chrome / -d android
```

The app expects the API at `http://localhost:8000` (override with `--dart-define=API_BASE_URL=...`).
The backend must be running for the Stops/Lines/Map screens to show data.

## Run everything with Docker Compose

```bash
docker compose up --build
```

Still run the Alembic migration and GTFS import once against this stack (`DATABASE_URL` from
`.env`, see `.env.example`) — Compose only starts the services, it doesn't seed data.

## Tests

```bash
cd backend
../.venv/Scripts/python -m pytest
```

```bash
cd app
flutter analyze
flutter test
```
