# Backend Docs Refactor — Fun with Flags

Dieses Dokument fasst alle veralteten Stellen in der Dokumentation zusammen, die durch die
Überarbeitung des Backends entstanden sind. Der zentrale Grund: Das Spiel-API wurde von einem
zustandslosen `GET /flags/random`-Endpunkt auf ein **server-seitiges Session-System** umgebaut.

---

## Hintergrund: Was hat sich im Backend geändert?

| Bereich | Alt | Neu |
|---|---|---|
| Spiel-API | `GET /flags/random?exclude=DE&FR` | Session-basiert: `POST /game/session` → `GET /game/flag` → `POST /game/answer` |
| Flag-Response | `country_name`, `flag_url` (CDN-Link) | `question_id`, `flag_svg` (SVG eingebettet), kein `country_name` |
| Antwort-Validierung | Client-seitig im Frontend | Server-seitig via `POST /game/answer` |
| Score-Tracking | Frontend berechnet und sendet Score | Server trackt Score in `GameSessionStore` (in-memory) |
| Highscore speichern | `POST /highscores/` Body: `{ score }` | `POST /highscores/` Body: `{ session_id }` |
| Neuer Endpunkt | — | `GET /highscores/me` (eigener Highscore, protected) |
| Flag-Persistenz | Laut alter Doku: in der DB | Ausschließlich im Arbeitsspeicher (`FlagCache`) |
| Cache-Aktualisierung | Laut alter Doku: stündlich | Nur einmalig beim App-Start |
| Neue Service-Klasse | — | `GameSessionStore` in `services/game_session.py` |
| Neue Tests (Unit) | — | `tests/unit/test_game_session.py` (17 Tests) |
| Neue Tests (Integration) | — | `tests/integration/test_security.py` (13 Tests) |
| Security-Tests | Nur manuell / OWASP ZAP geplant | Automatisiert mit pytest implementiert |

---

## Betroffene Dateien im Überblick

| Prio | Datei | Schwere |
|---|---|---|
| 🔴 1 | `docs/test-concept.md` | Fundamental veraltet — falsche Endpunkte, fehlende Test-Dateien, falsches CI |
| 🔴 2 | `src/backend/README.md` | Endpunkte und "How Flags Work" komplett falsch |
| 🔴 3 | `docs/architecture/06_runtime_view.md` | Zwei sachlich falsche Aussagen zur Architektur |
| 🟡 4 | `docs/architecture/08_crosscutting_concepts.md` | Zwei sachlich falsche Aussagen zum Caching |
| 🟡 5 | `docs/architecture/11_risks_and_technical_debts.md` | Technical Debt 1 beschreibt falschen Sachverhalt |
| 🟢 6 | `README.md` (Root) | Kleinigkeit: falscher venv-Name + Requirements-Datei |

---

## Schritt-für-Schritt-Anpassungen

---

### Schritt 1 — `docs/test-concept.md` ✅ ERLEDIGT

#### 1.1 ✅ Sektion 3.1 — Neue Unit-Test-Datei ergänzen

Nach der Tabelle `tests/unit/test_dependencies.py` eine neue Sektion einfügen:

```markdown
#### `tests/unit/test_game_session.py`

| Test case | What is verified |
|---|---|
| `test_create_session_returns_unique_ids` | Zwei Sessions erhalten verschiedene UUIDs |
| `test_create_session_initial_state` | Score, best, seen, current_question_id sind initial leer/0 |
| `test_get_session_returns_same_object` | `get_session()` gibt dasselbe Objekt zurück |
| `test_get_session_unknown_returns_none` | Unbekannte session_id → `None` |
| `test_store_question_adds_country_to_seen` | Country-Code landet in `session.seen` |
| `test_store_question_returns_unique_ids` | Zwei Fragen erhalten verschiedene UUIDs |
| `test_validate_correct_answer_increments_score` | Richtiger Answer → score +1, correct=True |
| `test_validate_wrong_answer_resets_score` | Falscher Answer → score=0, correct=False |
| `test_best_score_preserved_after_wrong_answer` | `best` bleibt bei 3 nachdem score resettet wird |
| `test_seen_flags_cleared_after_wrong_answer` | `seen`-Set wird bei falschem Answer geleert |
| `test_cleanup_expired_removes_old_sessions` | Inaktive Sessions (>TTL) werden gelöscht |
| `test_cleanup_expired_keeps_active_sessions` | Aktive Sessions bleiben erhalten |
| `test_validate_answer_removes_question` | Frage wird nach Beantwortung aus `_questions` entfernt |
| `test_validate_answer_invalid_question_id_raises` | Unbekannte question_id → `ValueError` |
| `test_get_best_score_unknown_session_returns_none` | Unbekannte session_id → `None` |
| `test_delete_session_removes_session` | Session + Score nicht mehr abrufbar |
| `test_delete_session_removes_orphaned_questions` | Offene Fragen der Session werden mitgelöscht |
```

---

#### 1.2 ✅ Sektion 3.2 — `test_flags.py` → `test_game.py` (Tabelle komplett ersetzen)

Den kompletten `#### tests/integration/test_flags.py`-Block **löschen** und ersetzen durch:

```markdown
#### `tests/integration/test_game.py`

| Test case | HTTP | Expected |
|---|---|---|
| `test_create_session_returns_session_id` | `POST /game/session` | `201`, Body enthält `session_id` |
| `test_get_flag_returns_correct_fields` | `GET /game/flag?session_id=...` | `200`, Keys: `question_id`, `flag_svg`, `options` |
| `test_get_flag_no_correct_answer_in_response` | `GET /game/flag?session_id=...` | `country_name` nie im Response |
| `test_get_flag_svg_is_valid` | `GET /game/flag?session_id=...` | `flag_svg` enthält `<svg`-Markup, keine CDN-URL |
| `test_get_flag_has_four_options` | `GET /game/flag?session_id=...` | `options` hat genau 4 Einträge |
| `test_get_flag_unknown_session` | `GET /game/flag?session_id=invalid` | `404` |
| `test_answer_correct` | `POST /game/answer` | `200`, `correct=true`, `score=1` |
| `test_answer_wrong` | `POST /game/answer` | `200`, `correct=false`, `score=0` |
| `test_answer_invalid_question_id` | `POST /game/answer` | `400` |
| `test_answer_question_can_only_be_used_once` | `POST /game/answer` (zweites Mal) | `400` |
| `test_score_increments_on_consecutive_correct_answers` | 3× korrekte Antwort | score steigt auf 3 |
| `test_score_resets_on_wrong_answer` | 3× korrekt, dann falsch | score=0 |
| `test_seen_flags_not_repeated` | 5× `GET /game/flag` | Keine SVG doppelt |
| `test_all_flags_shown_returns_404` | Alle Flags gesehen | `404` |
```

---

#### 1.3 ✅ Sektion 3.2 — `test_security.py` als neue Sektion ergänzen

Nach der `test_flag_cache_load.py`-Sektion einfügen:

```markdown
#### `tests/integration/test_security.py` (Penetration / Auth-Bypass)

| Test case | What is verified |
|---|---|
| `test_sql_injection_in_username_rejected` | SQL-Injection im Username → `422` |
| `test_xss_payload_in_username_rejected` | XSS-Payload im Username → `422` |
| `test_oversized_username_rejected` | Username > 50 Zeichen → `422` |
| `test_blank_password_rejected` | Leerzeichen-only Passwort → `422` |
| `test_too_short_password_rejected` | Passwort < Mindestlänge → `422` |
| `test_no_token_get_highscores_rejected` | Kein Bearer-Token → `401` |
| `test_no_token_post_highscores_rejected` | Kein Bearer-Token → `401` |
| `test_forged_jwt_rejected` | Manipulierter JWT → `401` |
| `test_expired_jwt_rejected` | Abgelaufener JWT → `401` |
| `test_jwt_wrong_secret_rejected` | JWT mit falschem Secret → `401` |
| `test_garbage_token_rejected` | Kein valides JWT-Format → `401` |
| `test_arbitrary_score_in_body_rejected` | Body `{ score: 99999999 }` statt `session_id` → `422` |
| `test_nonexistent_session_rejected` | Unbekannte `session_id` → `404` |
```

---

#### 1.4 ✅ Sektion 3.2 — `test_highscores.py`-Tabelle korrigieren

Zwei Korrekturen in der bestehenden Tabelle:

1. `test_get_highscores_no_token` → **`403` → `401`**
2. `test_save_score_no_token` → **`403` → `401`**

Außerdem fehlen diese neuen Test-Cases — am Ende der Tabelle ergänzen:

```markdown
| `test_save_score_unknown_session` | `POST /highscores/` mit unbekannter `session_id` | `404` |
| `test_save_score_updates_when_new_personal_best` | Neuer Rekord → `is_new_best=true`, `highscore=5` | `201` |
| `test_save_score_not_new_personal_best` | Kein neuer Rekord → `is_new_best=false`, alter Rekord bleibt | `201` |
| `test_get_my_highscore_authenticated` | `GET /highscores/me` (gültiger JWT) | `200`, `{username, score}` |
| `test_get_my_highscore_no_token` | `GET /highscores/me` (kein Token) | `401` |
| `test_get_my_highscore_invalid_token` | `GET /highscores/me` (ungültiger Token) | `401` |
| `test_get_my_highscore_no_score_yet` | Noch kein Highscore gespeichert | `404` |
| `test_get_my_highscore_only_own` | Nutzer B sieht nur eigenen Score, nicht den von Nutzer A | Isolation |
```

Auch den Body-Hinweis bei `test_save_score_authenticated` anpassen:
> Body ist `{ "session_id": "..." }`, kein `{ "score": ... }`

---

#### 1.5 ✅ Sektion 3.3 — E2E-Flows aktualisieren

Den "Guest game flow" ersetzen:

**Alt:**
> `GET /flags/random` 5× mit wachsender `exclude`-Liste → verify no repeat → final call returns `404`

**Neu:**
> `POST /game/session` → `GET /game/flag` 5× (session_id mitgeben) → `POST /game/answer` nach jeder Frage → nach allen Flags: `GET /game/flag` returns `404`

Den "Registered user flow" ergänzen:
> `POST /auth/register` → `POST /auth/login` → `POST /game/session` → N× `GET /game/flag` + `POST /game/answer` → `POST /highscores/` mit `{ session_id }` → `GET /highscores/` → Score in Top-10

---

#### 1.6 ✅ Sektion 3.4 — Security-Tests aktualisieren

Den gesamten DAST/OWASP-ZAP-Abschnitt durch folgenden Text ersetzen:

```markdown
#### Automated Security Tests — `tests/integration/test_security.py`

Die Security-Tests sind als automatisierte pytest-Integration-Tests implementiert und laufen
in der CI-Pipeline. Sie decken drei Kategorien ab:

1. **Input Validation** — SQL-Injection, XSS, oversized Username, Blank/Short Password
2. **Auth Bypass** — Kein Token, Forged JWT, Expired JWT, Wrong Secret, Garbage Token
3. **Score Manipulation** — Direktes Einsenden eines Score-Wertes im Body wird rejected (`422`)

OWASP ZAP kann zusätzlich als DAST-Tool manuell gegen den laufenden Docker-Stack eingesetzt
werden, ist aber kein Teil der automatisierten CI-Pipeline.
```

---

#### 1.7 ✅ Sektion 4 — Coverage-Tabelle entfernt

Die unvollständige Modul-Tabelle (nur 7 von ~15 Dateien aufgelistet) wurde entfernt.
Der Fließtext zur Coverage-Messung über das `app/`-Paket bleibt erhalten.

---

#### 1.8 ✅ Sektion 6 — Test Directory Layout komplett ersetzen

```markdown
src/backend/
├── tests/
│   ├── conftest.py              # Shared fixture: seeded_flag_cache
│   ├── unit/
│   │   ├── test_auth_service.py
│   │   ├── test_flag_cache.py
│   │   ├── test_game_session.py
│   │   └── test_dependencies.py
│   └── integration/
│       ├── conftest.py          # PostgreSQL-Container, async_client Fixture
│       ├── test_health.py
│       ├── test_auth.py
│       ├── test_game.py
│       ├── test_highscores.py
│       ├── test_flag_cache_load.py
│       └── test_security.py
├── app/
│   └── tests/
│       └── test_architecture.py # Architekturtests (pytestarch)
├── sonar-project.properties
├── pytest.ini
└── requirements.lock
```

**Hinweis:** `e2e/`-Verzeichnis und `e2e/test_full_flows.py` entfernen (nicht implementiert).

---

#### 1.9 ✅ Sektion 7 — CI-Snippet ersetzen

```yaml
# .github/workflows/tests.yml (aktueller Stand)
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: src/backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install --only-binary :all: --require-hashes -r requirements.lock
      - run: pytest tests/unit --cov=app --cov-report=xml -v
      - uses: actions/upload-artifact@v4
        with: { name: unit-coverage, path: src/backend/coverage.xml }

  integration-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: src/backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install --only-binary :all: --require-hashes -r requirements.lock
      - run: pytest tests/integration --cov=app --cov-report=xml -v
      - uses: actions/upload-artifact@v4
        with: { name: integration-coverage, path: src/backend/coverage.xml }

  architecture-tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: src/backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install --only-binary :all: --require-hashes -r requirements.lock
      - run: pytest app/tests -v

  sonarqube:
    needs: [unit-tests, integration-tests]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/download-artifact@v4
        with: { name: unit-coverage, path: src/backend/coverage/unit }
      - uses: actions/download-artifact@v4
        with: { name: integration-coverage, path: src/backend/coverage/integration }
      - uses: SonarSource/sonarqube-scan-action@7006c4492b2e0ee0f816d36501671557c97f5995
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

---

### Schritt 2 — `src/backend/README.md`

#### 2.1 Projektstruktur-Tabelle korrigieren

```
models/flag.py      →  löschen (existiert nicht)
models/game.py      →  ergänzen: Pydantic-Schemas für Session/Flag/Answer
services/           →  game_session.py ergänzen: In-memory GameSessionStore
```

Korrigierter `app/`-Block:

```
└── app/
    ├── config.py
    ├── dependencies.py
    ├── database/
    │   ├── engine.py
    │   └── models.py            # SQLAlchemy ORM: User, Highscore
    ├── models/
    │   ├── game.py              # Pydantic: SessionResponse, FlagQuestion, AnswerRequest/Response
    │   ├── user.py              # Pydantic: RegisterRequest, LoginRequest, TokenResponse
    │   └── highscore.py         # Pydantic: HighscoreEntry, SaveSessionRequest, SaveScoreResponse
    ├── repositories/
    │   ├── user.py
    │   └── highscore.py
    ├── routers/
    │   ├── game.py              # POST /game/session, GET /game/flag, POST /game/answer
    │   ├── auth.py              # POST /auth/register, POST /auth/login
    │   └── highscores.py        # GET /highscores/, GET /highscores/me, POST /highscores/
    └── services/
        ├── flag_cache.py        # In-memory Cache für restcountries.com
        ├── game_session.py      # GameSessionStore: Session + Score-Tracking
        ├── auth.py              # Passwort-Hashing + JWT
        ├── highscore.py         # Highscore-Businesslogik
        └── user.py              # User-Businesslogik
```

---

#### 2.2 Endpoints-Tabelle komplett ersetzen

**Public**

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health Check. Gibt gecachte Flag-Anzahl zurück. |
| `POST` | `/game/session` | Startet eine neue Spielsession. Gibt `session_id` zurück. |
| `GET` | `/game/flag` | Nächste Flagge der Session. Query-Param: `session_id`. Gibt `question_id`, `flag_svg`, `options`. |
| `POST` | `/game/answer` | Antwort einreichen. Body: `{ question_id, answer }`. Gibt `{ correct, score, correct_answer }`. |
| `POST` | `/auth/register` | Neuen Account anlegen. Body: `{ username, password }` |
| `POST` | `/auth/login` | Login. Gibt JWT zurück. Body: `{ username, password }` |

**Protected (require `Authorization: Bearer <token>`)**

| Method | Path | Description |
|---|---|---|
| `GET` | `/highscores/` | Top-10-Highscore aller Nutzer. |
| `GET` | `/highscores/me` | Eigener Highscore des eingeloggten Nutzers. |
| `POST` | `/highscores/` | Highscore einer Spielsession speichern. Body: `{ session_id }` |

---

#### 2.3 "How Flags Work"-Sektion komplett neu schreiben

```markdown
## How the Game Works

### 1. Session starten

```
POST /game/session
→ { "session_id": "uuid" }
```

### 2. Nächste Flagge holen

```
GET /game/flag?session_id=<uuid>
→ {
    "question_id": "uuid",
    "flag_svg": "<svg xmlns=...>...</svg>",
    "options": ["Germany", "France", "Brazil", "Japan"]
  }
```

- `flag_svg` enthält das SVG-Markup direkt (kein CDN-Link).
- Die richtige Antwort wird **nie** an den Client gesendet — sie ist
  server-seitig der Session hinterlegt.
- Der Server merkt sich gesehene Flags pro Session automatisch.

### 3. Antwort einreichen

```
POST /game/answer
Body: { "question_id": "uuid", "answer": "Germany" }
→ { "correct": true, "score": 3, "correct_answer": "Germany" }
```

- Score wird server-seitig getrackt und erhöht (korrekt) oder auf 0 resettet (falsch).
- Jede `question_id` kann nur einmal beantwortet werden.

### 4. Highscore speichern (optional, nur für eingeloggte Nutzer)

```
POST /highscores/
Header: Authorization: Bearer <token>
Body: { "session_id": "uuid" }
→ { "highscore": 5, "is_new_best": true }
```

Der Score wird serverseitig aus der Session gelesen — der Client kann keinen
beliebigen Wert einschicken.

### 5. Spielende

Wenn alle Länder in einer Session gezeigt wurden, gibt `GET /game/flag` `404` zurück.
```

---

#### 2.4 Test-Struktur-Abschnitt korrigieren

```
tests/
├── conftest.py                      # Shared fixtures (seeded_flag_cache)
├── unit/
│   ├── test_auth_service.py
│   ├── test_flag_cache.py
│   ├── test_game_session.py         # GameSessionStore-Logik
│   └── test_dependencies.py
└── integration/
    ├── conftest.py                  # PostgreSQL-Container + async_client
    ├── test_health.py
    ├── test_auth.py
    ├── test_game.py                 # Session-basiertes Spiel-API
    ├── test_highscores.py
    ├── test_flag_cache_load.py
    └── test_security.py            # Input Validation, Auth Bypass, Score Manipulation
```

---

### Schritt 3 — `docs/architecture/06_runtime_view.md`

#### 3.1 "Fetch Flag"-Abschnitt — zwei Sätze korrigieren

**Satz 1 löschen/ersetzen:**
> ~~"All flags are queried from the Persistence component and are cached in the Backend."~~

**Korrekt:**
> All flags are prefetched from the external public API on startup and stored exclusively in-memory (`FlagCache`). They are never written to the database.

**Satz 2 löschen/ersetzen:**
> ~~"This is done every hour to ensure that the information is up to date."~~

**Korrekt:**
> The flag cache is loaded once on application startup. There is no periodic refresh of flag data. (A separate background task cleans up expired game sessions every hour, but does not reload flags.)

---

#### 3.2 "Guess Country - Correct Guess" — Beschreibung anpassen

**Satz löschen/ersetzen:**
> ~~"The Frontend validates the guess and adjusts the highscore."~~

**Korrekt:**
> The Player submits their guess via `POST /game/answer`. The Backend validates the answer server-side, increments the session score on a correct guess, and returns `{ correct: true, score, correct_answer }` to the Frontend.

---

#### 3.3 "Guess Country - Incorrect Guess" — Beschreibung anpassen

**Satz löschen/ersetzen:**
> ~~"The current highscore is forwarded to the Backend to be persisted."~~

**Korrekt:**
> The Player submits their guess via `POST /game/answer`. The Backend resets the session score to 0 and returns `{ correct: false, score: 0, correct_answer }`. The score is only persisted when the user explicitly calls `POST /highscores/` with their `session_id`.

---

### Schritt 4 — `docs/architecture/08_crosscutting_concepts.md`

#### 4.1 "Prefetch & Caching"-Abschnitt — zwei Korrekturen

**Satz 1 ersetzen:**
> ~~"On application startup the Backend fetches all flags from the public API and stores them inside the Persistence component."~~

**Korrekt:**
> On application startup the Backend fetches all flags (metadata + SVG images) from the public API and stores them exclusively in-memory (`FlagCache`). Flag data is never written to the database.

**Satz 2 ersetzen:**
> ~~"Additionally the Backend caches the fetched flags. The cache is refreshed periodically."~~

**Korrekt:**
> The flag cache is loaded once at startup and serves all flag requests for the lifetime of the process. There is no periodic refresh. A separate background task removes expired game sessions every hour.

---

### Schritt 5 — `docs/architecture/11_risks_and_technical_debts.md`

#### 5.1 Technical Debt 1 — Beschreibung korrigieren

**Alt:**
> **Highscore stored in memory only** — The active highscore is not persisted mid-session. A backend restart loses the current highscore.

**Neu:**
> **Active game session stored in memory only** — The current in-game score (streak) is tracked in the server-side `GameSessionStore` which is in-memory only. A backend restart loses all active sessions and their in-progress scores. Saved highscores in the database are not affected. Mitigation: Acceptable for MVP; consider persistent session storage if required.

---

### Schritt 6 — `README.md` (Root)

#### 6.1 Architecture Tests — venv-Name und Requirements korrigieren

**Alt:**
```bash
python -m venv venv
source venv/bin/activate
# Windows
venv\Scripts\activate
pip install -r requirements.txt
```

**Neu:**
```bash
python -m venv .venv
source .venv/bin/activate
# Windows
.venv\Scripts\activate
pip install --only-binary :all: --require-hashes -r requirements.lock
```

---

## Zusammenfassung: Alle Änderungen auf einen Blick

| # | Datei | Was ändern |
|---|---|---|
| # | Datei | Was ändern | Status |
|---|---|---|---|
| 1 | `docs/test-concept.md` | Neue Sektion `test_game_session.py` (17 Tests) hinzufügen | ✅ |
| 2 | `docs/test-concept.md` | `test_flags.py`-Tabelle → `test_game.py` (Session-API-Tests) ersetzen | ✅ |
| 3 | `docs/test-concept.md` | Neue Sektion `test_security.py` (13 Tests) hinzufügen | ✅ |
| 4 | `docs/test-concept.md` | `test_highscores.py`: Status-Codes 403→401, neue Test-Cases ergänzen | ✅ |
| 5 | `docs/test-concept.md` | E2E-Flows: `GET /flags/random` → Session-basierter Flow | ✅ |
| 6 | `docs/test-concept.md` | Sektion 3.4: DAST/ZAP → automatisierte `test_security.py` | ✅ |
| 7 | `docs/test-concept.md` | Coverage-Tabelle (unvollständig) komplett entfernt, Fließtext bleibt | ✅ |
| 8 | `docs/test-concept.md` | Test Directory Layout: `test_game.py`, `test_security.py`, `test_game_session.py`, kein `e2e/` | ✅ |
| 9 | `docs/test-concept.md` | CI-Snippet: Python 3.12, 4 separate Jobs, `requirements.lock` | ✅ |
| 10 | `src/backend/README.md` | Projektstruktur: `models/flag.py` → `models/game.py`, `game_session.py` ergänzen | ⬜ |
| 11 | `src/backend/README.md` | Endpoints-Tabelle komplett ersetzen (Session-API, `/highscores/me`) | ⬜ |
| 12 | `src/backend/README.md` | "How Flags Work" → "How the Game Works" (Session-Flow) | ⬜ |
| 13 | `src/backend/README.md` | Test-Struktur: `test_game.py`, `test_security.py`, `test_game_session.py` | ⬜ |
| 14 | `docs/architecture/06_runtime_view.md` | "Fetch Flag": kein DB-Store, kein periodischer Refresh | ⬜ |
| 15 | `docs/architecture/06_runtime_view.md` | "Correct Guess": Frontend validiert nicht mehr, Backend validiert via `/game/answer` | ⬜ |
| 16 | `docs/architecture/06_runtime_view.md` | "Incorrect Guess": Score-Persistierung ist expliziter User-Schritt | ⬜ |
| 17 | `docs/architecture/08_crosscutting_concepts.md` | "Prefetch & Caching": Flags nicht in DB, kein periodischer Refresh | ⬜ |
| 18 | `docs/architecture/11_risks_and_technical_debts.md` | Technical Debt 1: "Highscore" → "aktive Spielsession" | ⬜ |
| 19 | `README.md` (Root) | `venv` → `.venv`, `requirements.txt` → `requirements.lock` | ⬜ |