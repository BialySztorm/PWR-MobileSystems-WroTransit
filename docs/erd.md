# ERD – model danych WroTransit

Stan po Sprincie 2: pełny schemat GTFS (odtwarzany przy każdym imporcie), tabele na bieżące
pozycje pojazdów (puste do Sprintu 3) i tabele użytkowników (puste do Sprintu 5).

```mermaid
erDiagram
    ROUTES ||--o{ TRIPS : "obsługuje"
    SHAPES ||--o{ TRIPS : "kształt trasy"
    CALENDAR ||--o{ TRIPS : "wzorzec kursowania"
    TRIPS ||--o{ STOP_TIMES : "rozkład kursu"
    STOPS ||--o{ STOP_TIMES : "obsługiwany przez"
    TRIPS ||--o{ VEHICLE_POSITIONS : "przypisany kurs"
    TRIPS ||--o{ VEHICLE_STATE : "przypisany kurs"
    USERS ||--o{ FAVOURITE_STOPS : "ma ulubione"
    STOPS ||--o{ FAVOURITE_STOPS : "ulubiony przez"
    USERS ||--o{ FAVOURITE_LINES : "ma ulubione"
    ROUTES ||--o{ FAVOURITE_LINES : "ulubiona przez"
    USERS ||--o{ DEVICES : "posiada"

    STOPS {
        string stop_id PK
        string stop_code
        string name
        geometry geom "POINT, 4326, GIST"
    }
    ROUTES {
        string route_id PK
        string short_name
        string long_name
        int type "0=tram, 3=bus"
    }
    TRIPS {
        string trip_id PK
        string route_id FK
        string service_id "FK-like, no constraint"
        int direction_id
        string shape_id FK
        string headsign
    }
    STOP_TIMES {
        string trip_id PK, FK
        int stop_sequence PK
        string stop_id FK
        int arrival_time_s
        int departure_time_s
    }
    SHAPES {
        string shape_id PK
        geometry geom "LINESTRING, 4326, GIST"
    }
    CALENDAR {
        string service_id PK
        bool monday
        bool tuesday
        bool wednesday
        bool thursday
        bool friday
        bool saturday
        bool sunday
        date start_date
        date end_date
    }
    CALENDAR_DATES {
        int id PK
        string service_id "no FK constraint"
        date date
        int exception_type "1=added, 2=removed"
    }
    VEHICLE_POSITIONS {
        int id PK
        string vehicle_id
        string line
        geometry geom "POINT, 4326"
        datetime recorded_at
        string trip_id FK "nullable"
        int delay_s "nullable"
    }
    VEHICLE_STATE {
        string vehicle_id PK
        string line
        geometry geom "POINT, 4326, nullable"
        datetime recorded_at
        string trip_id FK "nullable"
        int delay_s "nullable"
    }
    USERS {
        int id PK
        string email UK
        string password_hash
        datetime created_at
    }
    FAVOURITE_STOPS {
        int user_id PK, FK
        string stop_id PK, FK
    }
    FAVOURITE_LINES {
        int user_id PK, FK
        string route_id PK, FK
    }
    DEVICES {
        int id PK
        int user_id FK
        string fcm_token
        bool notify_enabled
    }
```

## Uwagi

- `trips.service_id` i `calendar_dates.service_id` nie mają ograniczenia FK — `calendar_dates.txt`
  może zawierać `service_id`, którego nie ma w `calendar.txt` (serwis zdefiniowany tylko przez
  wyjątki), więc sztywny FK blokowałby poprawny import części realnych feedów GTFS.
- `VEHICLE_POSITIONS`/`VEHICLE_STATE`/`USERS`/`FAVOURITE_*`/`DEVICES` mają gotowy schemat, ale są
  puste do czasu implementacji pollingu pojazdów (Sprint 3) i autoryzacji (Sprint 5).
- Indeksy GIST: `stops.geom`, `shapes.geom` (zapytania przestrzenne pod przyszłe
  `/stops/nearby`).
