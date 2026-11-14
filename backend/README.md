# Backend

FastAPI + PostgreSQL/PostGIS backend for WroTransit. For full repo setup (starting the
database, importing GTFS data, running everything together) see the
[root README](../README.md).

## Components

- `api/` — FastAPI app: REST endpoints for stops, routes, vehicles and departures, backed
  by raw SQL/PostGIS queries over the schedule and live-position tables.
- `ingest/` — two offline jobs that populate the database:
  - `gtfs_import.py` — rebuilds the schedule tables (`stops`, `routes`, `trips`,
    `stop_times`, `shapes`, `calendar*`) from a local GTFS archive. Run once after
    downloading a feed; safe to re-run.
  - `vehicle_polling.py` — polls live vehicle positions every ~10 s and writes them to
    `vehicle_positions` (history) and `vehicle_state` (latest per vehicle). The source is
    pluggable (`ingest/sources.py`, `VehiclePositionSource`):
    - `SOURCE=mpk` (default) — polls MPK Wrocław's undocumented `bus_position` endpoint.
    - `SOURCE=replay` — replays a previously recorded session (JSONL file under
      `data/recordings/`) instead of hitting the network — for tests and demos.
- `db/migrations/` — Alembic migrations for the schema above.
- `tests/` — pytest suite covering the API endpoints and the ingest jobs.

## Running the API

```bash
cd backend
uvicorn api.main:app --reload
```

Interactive API docs (Swagger UI) are served automatically at `http://localhost:8000/docs`
(raw OpenAPI schema at `/openapi.json`) — nothing extra to configure.

## Running the vehicle polling job

```bash
cd backend
python -m ingest.vehicle_polling          # SOURCE=mpk by default
SOURCE=replay python -m ingest.vehicle_polling
```

Also runs as the `ingest` service in `docker-compose.yml`.

Config (env vars, see `ingest/config.py`):

| Var | Default | Meaning |
|---|---|---|
| `SOURCE` | `mpk` | `mpk` or `replay` |
| `POLL_INTERVAL_S` | `10` | seconds between polls (ignored by `replay`, which follows the recorded timing) |
| `HTTP_TIMEOUT_S` | `5` | MPK HTTP request timeout |
| `RECORDINGS_DIR` | `backend/data/recordings` | where raw MPK responses are recorded / read from for replay |
| `REPLAY_FILE` | newest file in `RECORDINGS_DIR` | explicit recording to replay |
| `REPLAY_SPEED` | `1.0` | replay speed multiplier |

## Logging

Both `api` and `ingest` share the same structured logging setup
(`ingest/logging_config.py`, `LOG_LEVEL` env var, default `INFO`). The API also logs one
line per request (method, path, status, duration).

## Tests

```bash
cd backend
pytest
```

Tests run against a real PostgreSQL+PostGIS database, not SQLite — several endpoints use
PostGIS functions (`ST_X`/`ST_Y`/`ST_DWithin`) that SQLite doesn't have. Point them at a
dedicated test database via `TEST_DATABASE_URL`
(default `postgresql+psycopg://wrotransit:wrotransit@localhost:5432/wrotransit_test`);
see the root README for how to create it.
