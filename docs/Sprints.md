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
- [ ] Ekran mapy: `flutter_map`, OSM, centrum na Wrocławiu, przyciski filtra tramwaj/autobus — mapa gotowa (od Sprintu 1), **brak** przycisków filtra tramwaj/autobus
- [ ] Ekran wyszukiwania przystanków i linii (na razie na danych testowych) — są listy Stops/Lines, ale **na prawdziwym API**, nie na danych testowych, i **bez pola wyszukiwania** (samo listowanie)
- [ ] Ekran tablicy odjazdów (layout z makiety, dane testowe) — **nie zrobione**
- [x] Ekran przebiegu linii (layout, dane testowe) — `LineDetailScreen`, uporządkowana lista przystanków; dane z prawdziwego API, nie testowe
- [x] Nawigacja między ekranami zgodnie z user flow — dodana zakładka Lines + trasy szczegółów `/stops/:id`, `/lines/:id` (brak spisanego user flow z Sprintu 1 do porównania 1:1)
- [ ] Modele danych po stronie aplikacji (Dart): `Stop`, `Line`, `Vehicle`, `Departure` — `Stop`, `Line`, `Vehicle`, `RouteStop`/`LineRoute` gotowe; **brak `Departure`**
- [ ] Lokalizacja użytkownika na mapie (`geolocator`, obsługa uprawnień) — **nie zrobione**, `geolocator` nie jest nawet w `pubspec.yaml`

**Backend i dane [A]**
- [ ] Migracje Alembic: tabele GTFS z geometrią PostGIS (`stops`, `routes`, `trips`, `stop_times`, `shapes`, `calendar*`) — zrobiony **uproszczony** model (`Stop`, `Line`, `Route`/`RouteStop`, `Vehicle`), lat/lon jako `Float`, **bez typu PostGIS Geometry** i **bez** `trips`/`stop_times`/`shapes`/`calendar*` — realny GTFS schema zostaje do zrobienia
- [ ] Migracje: `vehicle_positions`, `vehicle_state`, `users`, `favourite_*`, `devices` — jest tylko uproszczona tabela `vehicles`; **brak** `users`/`favourite_*`/`devices` (ulubione na razie tylko w pamięci apki, bez backendu)
- [ ] Indeksy przestrzenne (GIST) na `stops.geom`, `shapes.geom` — **nie zrobione** (nie ma jeszcze kolumn `geom`)
- [ ] Import GTFS: pobranie archiwum, parsowanie, załadowanie do bazy, budowa geometrii — **nie zrobione**, `ingest/gtfs_import.py` wciąż placeholder; dodany tylko `backend/scripts/seed_data.py` z ręcznie wpisanymi danymi testowymi (kilka przystanków/linii dla Wrocławia)
- [ ] Diagram ERD do raportu — **nie zrobione**

**Wspólnie**
- [ ] [I+A] Uzgodnienie kontraktu API (schematy JSON) – na tej podstawie Igor robi dane testowe — powstały schematy Pydantic (`StopRead`, `LineRead`, `RouteRead`, `VehicleRead`) jako efekt implementacji, ale **nie jako uzgodniony wcześniej, spisany kontrakt**
- [ ] [I+A] Raport — do zweryfikowania poza repo

**Gotowe gdy:** rozkład GTFS jest w bazie, aplikacja ma wszystkie główne ekrany z nawigacją na danych testowych.
**Stan:** częściowo — baza ma uproszczony model (nie GTFS), brak ekranu odjazdów i wyszukiwania; nawigacja i przebieg linii działają na prawdziwych (nie testowych) danych z backendu.

---

## Sprint 3 – Tygodnie 7–8: backend, komunikacja API

**Cel kursu:** backend, komunikacja API.

**Backend [A]**
- [ ] Adapter źródła pozycji pojazdów (`VehiclePositionSource`) + implementacja dla MPK
- [ ] Polling pozycji co ~10 s → zapis do `vehicle_positions`, aktualizacja `vehicle_state`
- [ ] Nagrywanie danych i tryb replay (`SOURCE=replay`)
- [ ] Endpointy: `/vehicles`, `/stops`, `/stops/nearby`, `/lines`, `/lines/{id}/route` — **zrobione wcześniej w Sprincie 2**: `/vehicles` (z filtrem `line_id`), `/stops`, `/stops/{id}/lines`, `/lines`, `/lines/{id}/route`; **brakuje** `/stops/nearby` i filtra `type` (tramwaj/autobus — nie ma jeszcze pola typu pojazdu/linii w modelu)
- [ ] `/stops/{id}/departures` – na razie tylko rozkład, bez opóźnień — nie zrobione, zależy od tabel `stop_times`/`calendar` ze Sprintu 2
- [ ] Dokumentacja OpenAPI (automatyczna z FastAPI), przykłady odpowiedzi — Swagger pod `/docs` dostępny automatycznie (nic do zrobienia), ale **brak** dopisanych przykładów odpowiedzi
- [x] Testy endpointów (pytest + testowa baza) — **zrobione wcześniej w Sprincie 2** dla `/stops`, `/lines`, `/vehicles` (SQLite in-memory w `conftest.py`); brak jeszcze dedykowanych testów dla `/routes`
- [ ] CORS, obsługa błędów, logowanie — `HTTPException` 404 jest, ale **brak** middleware CORS i ustrukturyzowanego logowania

**Aplikacja [I]**
- [x] Klient HTTP (`dio`/`http`), konfiguracja adresu API — **zrobione wcześniej w Sprincie 2**: `ApiClient` na `package:http` + `AppConfig.apiBaseUrl`
- [ ] Mapa na żywych danych z `/vehicles`, odświeżanie co 10 s — mapa nadal statyczna (sama warstwa OSM), brak markerów pojazdów i pollingu
- [ ] Wyszukiwanie przez `/stops?q=` i `/lines?q=` — jest tylko pełne listowanie, backend nie przyjmuje jeszcze parametru `q`
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