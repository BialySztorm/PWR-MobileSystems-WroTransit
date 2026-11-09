# WroTransit – założenia projektowe

Projekt na kurs *Mobilne systemy informatyczne – Projekt* (PWr, semestr zimowy 2026/27).
Autorzy: Andrzej Manderla, Igor Wojtun.

## 1. Cel

Aplikacja mobilna z bieżącymi pozycjami tramwajów i autobusów we Wrocławiu, odjazdami z przystanków
i szacowanymi opóźnieniami. Funkcjonalnie to uproszczony odpowiednik JakDojade, ograniczony do
Wrocławia i do informacji o pojazdach i odjazdach.

Miasto publikuje rozkład (GTFS) i pozycje pojazdów, ale **nie publikuje opóźnień** (brak GTFS-Realtime).
Opóźnienia wyznaczamy sami, porównując pozycję GPS pojazdu z rozkładem. To główna logika biznesowa projektu.

### Poza zakresem

- wyszukiwanie połączeń z przesiadkami (planer podróży),
- bilety i płatności,
- inne miasta,
- iOS jako platforma docelowa (tylko jeśli wyjdzie przy okazji).

## 2. Źródła danych

| Dane | Źródło | Zawartość | Odświeżanie |
|---|---|---|---|
| Rozkład jazdy | Portal otwartych danych Wrocławia, archiwum GTFS (`opendata.cui.wroclaw.pl`) | przystanki, linie, kursy, godziny, kształty tras, kalendarz | import raz na dobę |
| Pozycje pojazdów | publiczny interfejs pozycji pojazdów MPK (mapa na stronie przewoźnika) i/lub zbiór „lokalizacja pojazdów” na portalu otwartych danych | współrzędne, linia, typ, identyfikator pojazdu | co ~10 s |

Pliki GTFS używane w projekcie: `stops.txt`, `routes.txt`, `trips.txt`, `stop_times.txt`,
`shapes.txt`, `calendar.txt`, `calendar_dates.txt`.

> **Do sprawdzenia:** dokładny adres i format endpointu pozycji pojazdów – nie jest formalnie
> udokumentowany i może się zmienić. Dlatego:
> - dostęp do źródła tylko przez adapter (`VehiclePositionSource`), łatwy do podmiany,
> - każdy odczyt zapisujemy w bazie → tryb **replay** (odtwarzanie nagranych danych) do testów i demo.

## 3. Użytkownicy

| Rola | Dostęp |
|---|---|
| Pasażer bez konta | mapa pojazdów, wyszukiwanie, odjazdy, przebieg linii, przystanki w pobliżu |
| Pasażer zalogowany | j.w. + ulubione przystanki i linie, powiadomienia |

## 4. Wymagania funkcjonalne

| ID | Wymaganie | Priorytet |
|---|---|---|
| FR1 | Mapa z bieżącymi pozycjami pojazdów, filtrowanie po linii i typie (tramwaj/autobus) | wysoki |
| FR2 | Wyszukiwanie przystanków i linii | wysoki |
| FR3 | Tablica odjazdów z przystanku z szacowanym opóźnieniem | wysoki |
| FR4 | Przebieg linii z położeniem pojazdów względem przystanków | średni |
| FR5 | Lokalizacja użytkownika: najbliższe przystanki i najbliższe odjazdy z nich | średni |
| FR6 | Rejestracja i logowanie | średni |
| FR7 | Ulubione przystanki i linie zapisane na koncie | średni |
| FR8 | Powiadomienie o pojeździe zbliżającym się do ulubionego przystanku | niski |

## 5. Wymagania niefunkcjonalne

| ID | Wymaganie |
|---|---|
| NFR1 | Pozycje pojazdów w aplikacji nie starsze niż 30 s |
| NFR2 | Android jako platforma docelowa (iOS opcjonalnie) |
| NFR3 | Komunikacja przez HTTPS, hasła jako skrót (bcrypt/argon2), sesja przez JWT |
| NFR4 | Mapa, odjazdy i wyszukiwanie działają bez logowania |
| NFR5 | Odpowiedź API dla odjazdów < 1 s przy typowym obciążeniu |
| NFR6 | Aplikacja nie wysypuje się bez sieci – pokazuje ostatnie dane i komunikat |

## 6. Architektura

```
 [GTFS (open data)]   [Pozycje pojazdów]
          \                 /
           v               v
        ┌───────────────────────┐
        │   ingest (Python)     │  import GTFS, polling pozycji, wyznaczanie opóźnień
        └──────────┬────────────┘
                   v
        ┌───────────────────────┐
        │ PostgreSQL + PostGIS  │
        └──────────┬────────────┘
                   v
        ┌───────────────────────┐
        │   API (FastAPI)       │  REST/JSON, autoryzacja JWT
        └──────────┬────────────┘
                   v  HTTPS/JSON
        ┌───────────────────────┐
        │ Aplikacja (Flutter)   │
        └───────────────────────┘
```

Aplikacja **nie łączy się** bezpośrednio ze źródłami miejskimi – wszystko idzie przez backend.

### Stos

| Warstwa | Technologia |
|---|---|
| Aplikacja | Flutter (Dart), `flutter_map` + OpenStreetMap, `go_router`, `geolocator`, stan: Riverpod (lub Bloc – do ustalenia) |
| API | Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic |
| Baza | PostgreSQL 16 + PostGIS |
| Ingest | Python, zadanie cykliczne (APScheduler lub pętla w osobnym kontenerze) |
| Powiadomienia | Firebase Cloud Messaging (FR8) |
| Infrastruktura | Docker Compose, GitHub Actions |

### Struktura repozytorium

```
app/                      # Flutter
  lib/core/               # config, HTTP client, theme, routing
  lib/features/{map,stops,lines,nearby,favourites,auth}/
backend/
  api/                    # routers, schemas, services
  ingest/                 # GTFS import, vehicle polling, delay estimation
  db/migrations/
  tests/
docs/
docker-compose.yml
.github/workflows/ci.yml
```

## 7. Model danych

Tabele rozkładowe (z GTFS, odtwarzane przy każdym imporcie):

| Tabela | Kluczowe pola |
|---|---|
| `stops` | `stop_id`, `code`, `name`, `geom` (Point, 4326) |
| `routes` | `route_id`, `short_name` (numer linii), `type` (tramwaj/autobus) |
| `trips` | `trip_id`, `route_id`, `service_id`, `direction_id`, `shape_id`, `headsign` |
| `stop_times` | `trip_id`, `stop_sequence`, `stop_id`, `arrival_time`, `departure_time`, `shape_dist` |
| `shapes` | `shape_id`, `geom` (LineString, 4326) |
| `calendar`, `calendar_dates` | dni kursowania |

Tabele bieżące:

| Tabela | Kluczowe pola |
|---|---|
| `vehicle_positions` | `id`, `vehicle_id`, `line`, `geom` (Point), `recorded_at`, `trip_id` (nullable), `shape_dist` (nullable), `delay_s` (nullable) |
| `vehicle_state` | ostatni stan każdego pojazdu (widok/tabela do szybkich zapytań mapy) |

Tabele użytkowników:

| Tabela | Kluczowe pola |
|---|---|
| `users` | `id`, `email`, `password_hash`, `created_at` |
| `favourite_stops` | `user_id`, `stop_id` |
| `favourite_lines` | `user_id`, `route_id` |
| `devices` | `user_id`, `fcm_token`, `notify_enabled` |

Historia pozycji: przechowywana np. 7 dni (potem czyszczona), wystarczy do replay i analizy.

## 8. API (szkic)

| Metoda | Ścieżka | Opis | Auth |
|---|---|---|---|
| GET | `/health` | status | – |
| GET | `/vehicles?line=&type=` | bieżące pozycje pojazdów | – |
| GET | `/stops?q=` | wyszukiwanie przystanków | – |
| GET | `/stops/nearby?lat=&lon=&radius=` | przystanki w promieniu | – |
| GET | `/stops/{id}/departures` | odjazdy z opóźnieniem | – |
| GET | `/lines?q=` | wyszukiwanie linii | – |
| GET | `/lines/{id}/route?direction=` | kształt trasy, przystanki, pojazdy na trasie | – |
| GET | `/nearby/departures?lat=&lon=` | najbliższe odjazdy z przystanków w pobliżu (FR5) | – |
| POST | `/auth/register` | rejestracja | – |
| POST | `/auth/login` | logowanie → JWT | – |
| GET | `/me` | dane konta | JWT |
| GET/POST/DELETE | `/me/favourites/stops[/{id}]` | ulubione przystanki | JWT |
| GET/POST/DELETE | `/me/favourites/lines[/{id}]` | ulubione linie | JWT |
| POST | `/me/devices` | rejestracja tokenu FCM | JWT |

Odświeżanie w aplikacji: polling `/vehicles` i `/departures` co 10 s (WebSocket opcjonalnie w Sprincie 6).

## 9. Wyznaczanie opóźnienia

Dla każdej odczytanej pozycji pojazdu:

1. **Rzutowanie na trasę** – `ST_LineLocatePoint(shape, position)` → przebyta odległość wzdłuż trasy.
   Odrzucamy pozycje dalej niż ~50 m od trasy (błąd GPS / zjazd do zajezdni).
2. **Przypisanie do kursu** – spośród kursów danej linii aktywnych dziś (`calendar`) wybieramy ten,
   którego planowe położenie o tej godzinie jest najbliższe pozycji pojazdu; uwzględniamy kierunek ruchu
   (rosnąca odległość wzdłuż trasy między kolejnymi odczytami). Przypisanie utrzymujemy między odczytami.
3. **Czas planowy w tym punkcie** – interpolacja liniowa między sąsiednimi przystankami z `stop_times`
   po `shape_dist`.
4. **Opóźnienie** = czas odczytu − czas planowy; wygładzane (np. mediana z ostatnich 3 odczytów).
5. **Odjazd z przystanku** = planowy odjazd + bieżące opóźnienie kursu. Kurs bez przypisanego pojazdu
   → wyświetlany jako „rozkład”.

## 10. Podział pracy

| Osoba | Obszary |
|---|---|
| Igor Wojtun | aplikacja mobilna (interfejs, nawigacja, mapa, ekrany), przetwarzanie danych po stronie aplikacji, wyznaczanie opóźnień |
| Andrzej Manderla | backend i API (REST, autoryzacja, konta, ulubione), przetwarzanie danych po stronie serwera (import GTFS, pobieranie pozycji, baza PostGIS), infrastruktura i jakość (repo, CI, Docker, testy) |
| Wspólnie | dokumentacja, raporty, prezentacja |

> Moduł opóźnień działa w backendzie (`backend/ingest/delay/`), a odpowiada za niego Igor.
> Andrzej dostarcza dla niego dane (pozycje i rozkład w bazie) i interfejs zapisu wyników.

## 11. Ryzyka

| Ryzyko | Przeciwdziałanie |
|---|---|
| Zmiana lub wyłączenie źródła pozycji | adapter źródła, nagrane dane, tryb replay |
| Niedokładny GPS w zabudowie | rzutowanie na trasę, odrzucanie odległych punktów |
| Błędne przypisanie pojazdu do kursu | heurystyka z kierunkiem ruchu, utrzymanie przypisania między odczytami |
| Brak czasu pod koniec semestru | FR8 (powiadomienia) jako pierwsze do wycięcia |

## 12. Konwencje

- kod, komentarze, commity – po angielsku; dokumentacja – po polsku,
- gałęzie: `main` (tag `sprint-N` na koniec sprintu), `develop`, `feature/<nazwa>`; merge przez PR,
- commity: Conventional Commits (`feat(map): add vehicle markers`),
- CI: `flutter analyze`, `flutter test`, `pytest` na każdym PR,
- użycie narzędzi AI zapisujemy na bieżąco – do tabeli NSI w raportach.