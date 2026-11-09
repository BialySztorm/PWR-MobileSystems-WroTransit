# WroTransit – plan sprintów

Harmonogram według kursu na ePortalu. Każdy sprint kończy się raportem (LaTeX, szablon PWr)
i tagiem `sprint-N` na `main`. Szczegóły techniczne: [ZALOZENIA.md](ZALOZENIA.md).

Oznaczenia: **[I]** Igor, **[A]** Andrzej, **[I+A]** wspólnie.

---

## Sprint 0 – Tydzień 2: wybór tematu i plan

**Cel kursu:** wybór projektu, opis funkcjonalności, wstępna architektura.

- [x] [I+A] Temat i zakres (co jest poza zakresem) — sekcja 1 ZALOZENIA.md
- [x] [A] Rozpoznanie źródeł danych: GTFS, pozycje pojazdów — sekcja 2 ZALOZENIA.md
- [x] [I+A] Wymagania funkcjonalne i niefunkcjonalne — sekcje 4–5 ZALOZENIA.md
- [x] [I+A] Wstępna architektura i stos technologiczny — sekcja 6 ZALOZENIA.md
- [x] [I] Opis metody wyznaczania opóźnień — sekcja 9 ZALOZENIA.md
- [x] [I+A] Plan sprintów, podział pracy, ryzyka — ten plik + sekcje 10–11 ZALOZENIA.md
- [x] [I+A] Raport — `docs/MSI_Sprint_0_report.pdf`

**Gotowe gdy:** raport oddany.

---

## Sprint 1 – Tygodnie 3–4: makiety UI, struktura aplikacji, repozytorium

**Cel kursu:** makiety UI, struktura aplikacji, repozytorium Git.

- [x] [I] User flow między ekranami — rys. 1 w `docs/MSI_Sprint_1_report.pdf` (diagram nawigacji między ekranami)
- [x] [I] Makiety: mapa, tablica odjazdów, przebieg linii, profil/logowanie, przystanki w pobliżu — rys. 2 w `docs/MSI_Sprint_1_report.pdf` (low-fidelity, TikZ); „przystanki w pobliżu” nie ma osobnej makiety — ujęte jako element mapy
- [x] [A] Repozytorium: gałęzie `main`/`develop`, ochrona `main`, szablon PR — gałąź robocza nazwana `dev` zamiast `develop` (świadomie); ochrona `main` świadomie pominięta (za mały/za szybki projekt na ten narzut); szablon PR: `.github/PULL_REQUEST_TEMPLATE.md`
- [x] [I] Szkielet aplikacji Flutter: `core/`, `features/`, routing, dolna nawigacja, puste ekrany
- [x] [A] Szkielet backendu: FastAPI z `/health`, struktura `api/`, `ingest/`, `db/`
- [x] [A] `docker-compose.yml`: `db` (PostGIS), `api`, `ingest`
- [x] [A] CI: `flutter analyze`, `flutter test`, `pytest`
- [x] [I+A] README z instrukcją uruchomienia
- [x] [I+A] Raport — `docs/MSI_Sprint_1_report.pdf`

**Gotowe gdy:** `docker compose up` stawia bazę i API, aplikacja się buduje i pokazuje nawigację, CI jest zielone.

---

## Sprint 2 – Tygodnie 5–6: podstawowy interfejs, nawigacja, model danych

**Cel kursu:** podstawowy interfejs, nawigacja, model danych.

**Aplikacja [I]**
- [x] Ekran mapy: `flutter_map`, OSM, centrum na Wrocławiu, przyciski filtra tramwaj/autobus — lepiej niż wymagane: realne znaczniki przystanków i narysowane trasy linii w widocznym obszarze mapy (`?bbox=` na `/stops` i `/shapes`), przełącznik Tramwaje/Autobusy realnie filtruje narysowane trasy po `route_type`; pojazdy na mapie zostają Sprintem 3 (brak jeszcze danych z pollingu)
- [x] Ekran wyszukiwania przystanków i linii — pole wyszukiwania (debounce 300 ms) nad listami Stops/Lines, `?q=` na `/stops` i `/routes`; na prawdziwym API, nie na danych testowych
- [x] Ekran tablicy odjazdów — `StopDetailScreen` pokazuje realne odjazdy z `/stops/{id}/departures` (linia, kierunek, godzina); pociągnięte przed grafik z Sprintu 3 (`/stops/{id}/departures`), bo model już to wspiera
- [x] Ekran przebiegu linii (layout, dane testowe) — `LineDetailScreen`, uporządkowana lista przystanków; dane z prawdziwego API, nie testowe
- [x] Nawigacja między ekranami zgodnie z user flow — zakładka Lines + trasy szczegółów `/stops/:id`, `/lines/:id`, zgodne z diagramem w `docs/MSI_Sprint_1_report.pdf`
- [x] Modele danych po stronie aplikacji (Dart): `Stop`, `Line`, `Vehicle`, `Departure` — wszystkie gotowe (`lib/features/*/data/models/`)
- [x] Lokalizacja użytkownika na mapie (`geolocator`, obsługa uprawnień) — przycisk lokalizacji, obsługa odmowy uprawnień/wyłączonej usługi, niebieski znacznik + recentrowanie

**Backend i dane [A]**
- [x] Migracje Alembic: tabele GTFS z geometrią PostGIS (`stops`, `routes`, `trips`, `stop_times`, `shapes`, `calendar*`) — pełny schemat (`geoalchemy2`), zweryfikowany na realnych danych Wrocławia (2429 przystanków, 133 linie, 41 790 kursów, 1 131 610 wierszy `stop_times`)
- [x] Migracje: `vehicle_positions`, `vehicle_state`, `users`, `favourite_*`, `devices` — schemat gotowy (puste do Sprintu 3/5, zgodnie z planem)
- [x] Indeksy przestrzenne (GIST) na `stops.geom`, `shapes.geom`
- [x] Import GTFS: pobranie archiwum, parsowanie, załadowanie do bazy, budowa geometrii — `ingest/gtfs_import.py`, `stop_times` ładowane przez `psycopg COPY` (wydajność przy 1,1 mln wierszy); **źródło**: oficjalny URL wroclaw.pl blokuje automatyczne pobieranie (Cloudflare bot-fight, potwierdzone), więc import czyta lokalny plik `backend/data/wroclaw.gtfs.zip` (zwierciadło Mobility Database, do ręcznego odświeżenia co jakiś czas — plik gitignored)
- [x] Diagram ERD do raportu — `docs/erd.md` (Mermaid)

**Wspólnie**
- [x] [I+A] Uzgodnienie kontraktu API (schematy JSON) – na tej podstawie Igor robi dane testowe — schematy Pydantic (`StopRead`, `RouteRead`, `DepartureRead`, `VehicleStateRead`) i realne dane z importu zastępują potrzebę osobnych danych testowych
- [x] [I+A] Raport — `docs/MSI_Sprint_2_report.pdf`

**Gotowe gdy:** rozkład GTFS jest w bazie, aplikacja ma wszystkie główne ekrany z nawigacją na danych testowych.
**Stan:** zrobione, na realnych (nie testowych) danych — lepiej niż wymagało minimum sprintu. Jedno zastrzeżenie: zaimportowany snapshot GTFS (zwierciadło) ma `calendar` ważny do 2025-12-12 — `/stops/{id}/departures` poprawnie zwraca pustą listę, dopóki nie wgra się świeższego archiwum.

---

## Sprint 3 – Tygodnie 7–8: backend, komunikacja API

**Cel kursu:** backend, komunikacja API.

**Backend [A]**
- [ ] Adapter źródła pozycji pojazdów (`VehiclePositionSource`) + implementacja dla MPK
- [ ] Polling pozycji co ~10 s → zapis do `vehicle_positions`, aktualizacja `vehicle_state`
- [ ] Nagrywanie danych i tryb replay (`SOURCE=replay`)
- [ ] Endpointy: `/vehicles`, `/stops`, `/stops/nearby`, `/lines`, `/lines/{id}/route` — **zrobione wcześniej w Sprincie 2**: `/vehicles` (z filtrem `line`, dane z `vehicle_state`), `/stops` (z `?q=`), `/routes` (z `?q=`, nazwa ujednolicona z GTFS — nie `/lines`), `/routes/{id}/route`; **brakuje** `/stops/nearby` (zapytanie przestrzenne po GIST — model już to wspiera, zapytanie jeszcze nie napisane)
- [x] `/stops/{id}/departures` – na razie tylko rozkład, bez opóźnień — **zrobione wcześniej w Sprincie 2**, bo `stop_times`/`calendar` już są; join po aktywnym dziś `service_id`, bez uwzględnienia `calendar_dates` (ten feed ma pusty plik, więc na razie no-op)
- [ ] Dokumentacja OpenAPI (automatyczna z FastAPI), przykłady odpowiedzi — Swagger pod `/docs` dostępny automatycznie (nic do zrobienia), ale **brak** dopisanych przykładów odpowiedzi
- [x] Testy endpointów (pytest + testowa baza) — **zrobione wcześniej w Sprincie 2** dla `/stops`, `/routes` (w tym kształt trasy), `/vehicles`, `/stops/{id}/departures`; testy przeszły z SQLite in-memory na realny Postgres (serwis `db` w CI) — SQLite nie ma funkcji PostGIS (`ST_X`/`ST_Y`), których endpointy teraz używają
- [ ] CORS, obsługa błędów, logowanie — **zrobione częściowo wcześniej w Sprincie 2**: middleware CORS jest (wymagane, żeby apka web w ogóle działała), `HTTPException` 404 jest; **brak** ustrukturyzowanego logowania

**Aplikacja [I]**
- [x] Klient HTTP (`dio`/`http`), konfiguracja adresu API — **zrobione wcześniej w Sprincie 2**: `ApiClient` na `package:http` + `AppConfig.apiBaseUrl`
- [ ] Mapa na żywych danych z `/vehicles`, odświeżanie co 10 s — mapa ma już filtry tramwaj/autobus i znacznik użytkownika (Sprint 2), ale brak markerów pojazdów i pollingu (`vehicle_state` jest puste do czasu pollingu)
- [x] Wyszukiwanie przez `/stops?q=` i `/lines?q=` — **zrobione wcześniej w Sprincie 2** (endpoint ujednolicony jako `/routes?q=`, nie `/lines?q=`), z debounce w UI
- [ ] Obsługa braku sieci i błędów (NFR6) — częściowo: ekrany pokazują błąd przez `AsyncValue.when`/`FutureProvider`, ale brak retry i trybu offline (ostatnie znane dane)

**Wspólnie**
- [ ] [I+A] Raport

**Gotowe gdy:** aplikacja pokazuje prawdziwe pojazdy na mapie i wyszukuje przystanki przez API.

---

## Sprint 4 – Tygodnie 9–10: logika biznesowa, integracja frontend–backend

**Cel kursu:** logika biznesowa, integracja frontend–backend.

**Wyznaczanie opóźnień [I]** (moduł w `backend/ingest/delay/`)
- [ ] Rzutowanie pozycji na kształt trasy (`ST_LineLocatePoint`), odrzucanie punktów > 50 m od trasy
- [ ] Przypisanie pojazdu do kursu (linia, kierunek ruchu, najbliższy planowo kurs dziś aktywny)
- [ ] Interpolacja czasu planowego po `shape_dist`
- [ ] Obliczanie i wygładzanie opóźnienia, zapis `trip_id`, `delay_s`
- [ ] Testy na nagranych danych (replay) – kilka przypadków ręcznie sprawdzonych

**Backend [A]**
- [ ] `/stops/{id}/departures` z opóźnieniem (planowy odjazd + opóźnienie kursu, status „rozkład”)
- [ ] `/lines/{id}/route` z pozycją pojazdów względem przystanków
- [ ] `/nearby/departures` (FR5)
- [ ] Cache / optymalizacja zapytań odjazdów (NFR5)

**Aplikacja [I]**
- [ ] Tablica odjazdów na żywych danych, oznaczenie opóźnień kolorem
- [ ] Przebieg linii na żywych danych
- [ ] Panel „W pobliżu” na mapie – najbliższe przystanki i odjazdy (FR5)
- [ ] Przejścia mapa → pojazd → przebieg linii

**Wspólnie**
- [ ] [I+A] Test end-to-end: przystanek → odjazdy → linia na prawdziwych danych
- [ ] [I+A] Raport

**Gotowe gdy:** FR1–FR5 działają end-to-end, opóźnienia wyświetlają się w aplikacji.

---

## Sprint 5 – Tygodnie 11–12: autoryzacja użytkownika, rozwój funkcjonalności

**Cel kursu:** autoryzacja użytkownika, rozwój funkcjonalności.

**Backend [A]**
- [ ] `/auth/register`, `/auth/login` – hashowanie haseł, JWT (access + refresh)
- [ ] Middleware autoryzacji, `/me`
- [ ] Ulubione: `/me/favourites/stops`, `/me/favourites/lines`
- [ ] `/me/devices` – rejestracja tokenu FCM
- [ ] Wysyłanie powiadomień: pojazd zbliża się do ulubionego przystanku (FR8)
- [ ] Testy autoryzacji (brak tokenu, zły token, wygasły token)

**Aplikacja [I]**
- [ ] Ekrany logowania i rejestracji, walidacja formularzy
- [ ] Bezpieczne przechowywanie tokenu (`flutter_secure_storage`), automatyczne odświeżanie
- [ ] Ulubione: dodawanie gwiazdką, ekran „Ulubione”
- [ ] Integracja FCM, ustawienia powiadomień w profilu

**Wspólnie**
- [ ] [I+A] Raport

**Gotowe gdy:** FR6–FR7 działają, FR8 działa lub świadomie przesunięte/wycięte.

---

## Sprint 6 – Tygodnie 13–14: optymalizacja, UX/UI, testy, stabilizacja

**Cel kursu:** optymalizacja, UX/UI, testy i stabilizacja.

**Aplikacja [I]**
- [ ] Dopracowanie wyglądu: kolory, ikony pojazdów, tryb ciemny (opcjonalnie)
- [ ] Klastrowanie znaczników przy oddaleniu mapy, płynne przesuwanie pojazdów
- [ ] Stany puste, ładowanie, błędy
- [ ] Testy widgetów kluczowych ekranów
- [ ] Testy z użytkownikami (2–3 osoby) – krótkie badanie użyteczności, wnioski do raportu

**Backend [A]**
- [ ] Pomiar czasów odpowiedzi, optymalizacja zapytań (EXPLAIN, indeksy)
- [ ] Czyszczenie starej historii pozycji
- [ ] Testy integracyjne, pokrycie testami
- [ ] Wdrożenie do demo (serwer/VPS lub lokalnie przez Docker + tunel) – do ustalenia

**Delay [I]**
- [ ] Ocena dokładności opóźnień: porównanie z obserwacjami na przystanku / z innym źródłem

**Wspólnie**
- [ ] [I+A] Poprawki błędów, zamrożenie funkcjonalności
- [ ] [I+A] Raport

**Gotowe gdy:** aplikacja stabilna na demo, brak znanych błędów krytycznych.

---

## Prezentacja – Tygodnie 14–15

**Cel kursu:** demo aplikacji, omówienie architektury, ocena projektów.

- [ ] [I+A] Slajdy (szablon PWr): problem, architektura, wyznaczanie opóźnień, demo, wnioski
- [ ] [A] Przygotowanie demo w trybie replay (zapas, gdy źródło live nie działa)
- [ ] [I] Nagranie wideo demo (zapas, gdy coś nie zadziała na żywo)
- [ ] [I+A] Próba prezentacji, podział kto co mówi