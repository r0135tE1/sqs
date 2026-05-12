# Backend Cleanup — Fun with Flags

Analyse des Backend-Codes gegen die SQS-Projektcheckliste.
Fokus: Softwarequalität, Testabdeckung, CI-Pipeline, statische Analyse. 

---

> **Regeln für dieses Dokument:**
> - Code-Änderungen werden **nur auf explizite Anfrage** durchgeführt.
> - Es wird **ausschließlich Backend-Code** betrachtet (`src/backend/`).

---

## Schritt-für-Schritt-Plan (gemeinsame Review)

Wir gehen Ordner für Ordner durch. Wenn du sagst **„bereit"**, erkläre ich den nächsten Ordner.
Der aktuelle Schritt ist mit **→ AKTUELL** markiert.

---

### Schritt 1 — CI & Projekt-Konfiguration  `✅ REVIEWED`

```
sonar-project.properties
.github/workflows/tests.yml
.github/workflows/build.yml
```

> **Notiz:** SonarQube (`sonar.coverage.skip=true`, `build.yml`) und die Architekturtests (auskommentierter CI-Job) sind **bewusst zurückgestellt** — werden separat angegangen.
> Issues #1, #2, #3, #4 bleiben offen, aber außerhalb des aktuellen Scopes.

---

### Schritt 2 — `src/backend/` (Root-Dateien)  `✅ REVIEWED`

```
src/backend/main.py
src/backend/pytest.ini
src/backend/requirements.txt
src/backend/dev-requirements.txt
```

---

### Schritt 3 — `src/backend/app/` (Einstiegspunkt + Config)  `✅ REVIEWED`

```
src/backend/app/config.py
src/backend/app/dependencies.py
```

---

### Schritt 4 — `src/backend/app/database/`  `✅ REVIEWED`

```
src/backend/app/database/engine.py
src/backend/app/database/models.py
```

---

### Schritt 5 — `src/backend/app/models/`  `✅ REVIEWED`

```
src/backend/app/models/user.py
src/backend/app/models/game.py
src/backend/app/models/highscore.py
```

---

### Schritt 6 — `src/backend/app/repositories/`  `✅ REVIEWED`

```
src/backend/app/repositories/user.py
src/backend/app/repositories/highscore.py
```

---

### Schritt 7 — `src/backend/app/services/`  `✅ REVIEWED`

```
src/backend/app/services/auth.py
src/backend/app/services/flag_cache.py
src/backend/app/services/game_session.py
src/backend/app/services/highscore.py
src/backend/app/services/user.py
```

---

### Schritt 8 — `src/backend/app/routers/`  `✅ REVIEWED`

```
src/backend/app/routers/auth.py
src/backend/app/routers/game.py
src/backend/app/routers/highscores.py
```

---

### Schritt 9 — `src/backend/app/tests/` (Architekturtests)  `✅ REVIEWED`

```
src/backend/app/tests/test_architecture.py
```

---

### Schritt 10 — `src/backend/tests/` (Fixtures)  `✅ REVIEWED`

```
src/backend/tests/conftest.py
src/backend/tests/integration/conftest.py
```

---

### Schritt 11 — `src/backend/tests/unit/`  `✅ REVIEWED`

```
src/backend/tests/unit/test_auth_service.py
src/backend/tests/unit/test_flag_cache.py
src/backend/tests/unit/test_game_session.py
src/backend/tests/unit/test_dependencies.py
```

---

### Schritt 12 — `src/backend/tests/integration/`  `→ AKTUELL`

```
src/backend/tests/integration/test_health.py
src/backend/tests/integration/test_auth.py
src/backend/tests/integration/test_game.py
src/backend/tests/integration/test_highscores.py
src/backend/tests/integration/test_flag_cache_load.py
```

---

### Schritt 13 — Fixes umsetzen

Alle identifizierten Issues aus dem Cleanup (siehe unten) gemeinsam beheben.

---

## Gesamtstatus

| Anforderung (Checkliste) | Status | Problem |
|---|---|---|
| Unit-Tests | ✅ | vorhanden & laufen in CI |
| Integration-Tests | ✅ | vorhanden & laufen in CI |
| e2e-Tests | ❌ | nur im Testkonzept beschrieben, kein Code |
| Penetration-Tests | ⚠️ | OWASP ZAP erwähnt, nicht implementiert |
| Architekturtests | ⚠️ | Code vorhanden, CI-Job auskommentiert |
| Lauffähige GitHub-Pipeline | ⚠️ | unit + integration laufen, arc-tests fehlen in CI |
| Statische Analyse ≥80% Coverage | ❌ | `sonar.coverage.skip=true` — Coverage komplett deaktiviert |
| Resilience / Ausfallsichere Muster | ✅ | FlagCache mit graceful degradation |
| arc42-Dokumentation | ✅ | vollständig vorhanden |
| ADRs | ✅ | 6 ADRs dokumentiert |

---

## Kritische Issues (Note-relevant)

### 1. `sonar.coverage.skip=true` — Coverage komplett deaktiviert

**Datei:** `sonar-project.properties`, Zeile 8

```properties
sonar.coverage.skip=true  # <- MUSS entfernt werden
```

Die Checkliste fordert explizit: *„Ein Tool zur statischen Codeanalyse zeigt keine offenen Issues und eine Testabdeckung von mindestens 80%."*

SonarCloud sieht aktuell **0% Coverage**, weil der Wert manuell übersprungen wird. Das verfehlt die Kernanforderung.

**Fix:**
```properties
# sonar-project.properties
sonar.projectKey=r0135tE1_sqs
sonar.organization=wellensittich

sonar.sources=src/backend/app
sonar.tests=src/backend/tests
sonar.python.version=3.12
sonar.python.coverage.reportPaths=src/backend/coverage.xml

sonar.exclusions=**/venv/**,**/.venv/**,**/node_modules/**,**/__pycache__/**,**/*.pdf
sonar.c.file.suffixes=-
sonar.cpp.file.suffixes=-
sonar.objc.file.suffixes=-
```

Außerdem muss der `build.yml`-Job erst die Tests laufen lassen, bevor Sonar aufgerufen wird (sonst gibt es keine `coverage.xml`):

```yaml
# .github/workflows/build.yml — Sonar-Job anpassen
jobs:
  sonarqube:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: funwithflags
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r src/backend/requirements.txt -r src/backend/dev-requirements.txt
        working-directory: .
      - name: Run tests and collect coverage
        run: pytest tests/unit tests/integration --cov=app --cov-report=xml --cov-fail-under=80
        working-directory: src/backend
        env:
          JWT_SECRET: ci-secret
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/funwithflags
      - uses: SonarSource/sonarqube-scan-action@v6
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

---

### 2. Architekturtests laufen nicht in CI

**Datei:** `.github/workflows/tests.yml`, Zeilen 49–64

```yaml
# backend-architecture:   <-- komplett auskommentiert
#   name: Backend Architecture Tests
#   ...
#   - name: Run architecture tests
#     run: pytest app/tests -v
```

Es gibt 10 Architekturtests (`app/tests/test_architecture.py`), die sicherstellen, dass Abhängigkeitsrichtungen eingehalten werden. Diese laufen **nie** in CI. Jeder Commit kann die Architekturinvarianten brechen, ohne dass CI rot wird.

**Fix:** Job einkommentieren und korrekt konfigurieren:

```yaml
backend-architecture:
  name: Backend Architecture Tests
  runs-on: ubuntu-latest
  defaults:
    run:
      working-directory: src/backend
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.12"
        cache: pip
    - name: Install dependencies
      run: pip install -r requirements.txt -r dev-requirements.txt
    - name: Run architecture tests
      run: pytest app/tests -v
      env:
        JWT_SECRET: ci-secret
```

---

### 3. Architekturtests werden von `pytest.ini` nicht gefunden

**Datei:** `pytest.ini`

```ini
testpaths = tests
```

`app/tests/test_architecture.py` liegt außerhalb von `tests/`. Ein simples `pytest` aus `src/backend/` findet die Architekturtests **nicht**. Sie müssen entweder:

- nach `tests/architecture/test_architecture.py` verschoben werden (empfohlen), oder
- `testpaths` um `app/tests` erweitert werden.

Verschieben ist besser, weil dann ein einziger `pytest`-Aufruf die gesamte Testpyramide abdeckt.

---

### 4. Coverage-Schwellwert nicht in CI erzwungen

**Datei:** `.github/workflows/tests.yml`

```yaml
- name: Run unit tests
  run: pytest tests/unit --cov=app --cov-report=xml -v
  #                                                    ^ kein --cov-fail-under
```

Beide Jobs (unit + integration) verwenden kein `--cov-fail-under=80`. CI ist grün, auch wenn Coverage auf 20% fällt. Das Testkonzept beschreibt die Anforderung richtig, sie ist aber nicht durchgesetzt.

**Fix:** `--cov-fail-under=80` an jeden `pytest`-Aufruf anhängen, der Coverage misst.

---

### 5. Keine e2e-Tests implementiert

Das Testkonzept (`docs/test-concept.md`, Kapitel 3.3) beschreibt drei vollständige Flows in `tests/e2e/test_full_flows.py`. Das Verzeichnis existiert nicht.

Die Checkliste fordert e2e-Tests **mit UI-Automatisierung** als Teil der vollständigen Testpyramide.

**Minimalumsetzung ohne UI-Automatisierung** (gegen laufendes Docker Compose):

```
src/backend/tests/e2e/
└── test_full_flows.py   # httpx gegen http://localhost:8000
```

Flows die mindestens abgedeckt sein müssen:
1. Guest-Flow: Session erstellen → 5× Flag holen (ohne Wiederholung) → alle Flags zeigen → 404
2. Auth-Flow: Register → Login → Highscore speichern → Highscore abrufen
3. Token-Expiry: abgelaufenes Token → 401

---

## High Priority

### 6. Test- und Build-Abhängigkeiten in `requirements.txt`

**Datei:** `requirements.txt`, Zeilen 14–15

```
pytestarch>=2.0.0   # Nur für Architekturtests
pytest>=9.0.3       # Nur für Tests
```

Diese Pakete gehören in `dev-requirements.txt`. Im Produktions-Dockerfile werden sie unnötigerweise installiert, was das Image vergrößert.

**Fix:** Aus `requirements.txt` entfernen, in `dev-requirements.txt` eintragen.

---

### 7. `test_get_highscores_no_token` — falsche Statuscode-Erwartung

**Datei:** `tests/integration/test_highscores.py`, Zeile 37

```python
async def test_get_highscores_no_token(async_client):
    response = await async_client.get("/highscores/")
    assert response.status_code == 401  # <- FALSCH
```

FastAPIs `HTTPBearer(auto_error=True)` (Standard) gibt **403** zurück, wenn kein `Authorization`-Header vorhanden ist. **401** wird nur zurückgegeben, wenn `get_current_user` ein ungültiges Token ablehnt.

Gleiches Problem in `test_save_score_no_token` (Zeile 60).

**Fix:**
```python
assert response.status_code == 403  # kein Header -> 403 from HTTPBearer
```

---

### 8. `GameSessionStore` — kein Session-Cleanup

**Datei:** `app/services/game_session.py`

```python
class GameSessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, GameSession] = {}
        self._questions: dict[str, _Question] = {}
```

Sessions werden niemals gelöscht. Beantwortete Fragen werden in `validate_answer` via `del self._questions[question_id]` entfernt (gut), aber Sessions bleiben ewig im RAM. In einem laufenden Produktionssystem akkumulieren Sessions ohne Obergrenze.

**Kurzfristiger Fix** (akzeptabel für MVP): im `11_risks_and_technical_debts.md` als bekannte Technical Debt eintragen (dort steht `Highscore stored in memory only`, aber Session-Leak fehlt).

**Mittelfristiger Fix:** TTL-basiertes Cleanup, z.B. mit `asyncio.create_task` und einem Background-Task der alte Sessions löscht.

---

## Medium Priority

### 9. Direkter Zugriff auf interne State in Integrationstests

**Dateien:** `tests/integration/test_game.py` (Zeilen 65, 108, 135), `tests/integration/test_highscores.py` (Zeile 19)

```python
correct = game_session_store._questions[qid].correct_answer  # interne State
```

Integrationstests greifen auf `_questions` (privates Attribut) zu, um die korrekte Antwort zu erhalten. Das ist eine Verletzung der Kapselung und macht Tests fragil gegenüber internen Refactorings.

**Alternative:** `seeded_flag_cache` enthält fixe Länder mit bekannten Namen. Tests könnten über den `options`-Array die korrekte Antwort ermitteln (alle Options sind bekannt), ohne internal State anzufassen. Oder: einen eigenen Hilfs-Router nur für Tests anbieten — aber das wäre Over-Engineering für diesen Umfang.

Für das Projekt akzeptabel, sollte aber dokumentiert werden.

---

### 10. Penetrations-Tests nicht implementiert

Das Testkonzept beschreibt OWASP ZAP als DAST-Tool. Es gibt keinen ZAP-CI-Job und keine Skripte. Die Checkliste sagt explizit: *„Penetrations Tests: Hier sind v.a. Tests gemeint, die eure abgesicherten Endpunkte testen."*

Das kann auch einfach als erweiterter Integrationstest umgesetzt werden, z.B.:

```python
# tests/integration/test_security.py
async def test_sql_injection_in_username_is_rejected(async_client):
    response = await async_client.post(
        "/auth/register",
        json={"username": "'; DROP TABLE users;--", "password": "password123"}
    )
    assert response.status_code == 422  # Pydantic-Pattern-Validator greift

async def test_oversized_score_rejected(async_client):
    # Score-Wert kann vom Client gar nicht gesendet werden (SaveSessionRequest hat kein score-Feld)
    token = await _register_and_login(async_client, "pentest_user")
    response = await async_client.post(
        "/highscores/",
        json={"score": 99999999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422

async def test_forged_jwt_rejected(async_client):
    response = await async_client.get(
        "/highscores/",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.forged.payload"}
    )
    assert response.status_code == 401
```

Diese Tests existieren zum Teil schon (`test_arbitrary_score_rejected` in `test_highscores.py`). Es fehlt eine explizit als Penetrationstest ausgewiesene Datei/Sektion.

---

## Low / Style

### 11. Überflüssige Inline-Kommentare

Die Checkliste selbst fordert keine Code-Kommentare, aber der Code enthält viele Kommentare, die nur das Offensichtliche wiederholen:

| Datei | Kommentar | Problem |
|---|---|---|
| `main.py:13` | `#API-Startup: cache Flags and run Server` | `lifespan` und `flag_cache.load()` sind selbsterklärend |
| `main.py:27` | `#Middelware allowing CORS for Backend-Frontend Communication` | Tippfehler: "Middelware" statt "Middleware" |
| `main.py:40` | `#Endpoint for Monitoring` | `/health`-Route sagt das selbst |
| `config.py:5` | `#Central Config-Values from .env or default values` | `class Settings(BaseSettings)` ist eindeutig |
| `engine.py:7` | `#define DB connection` | `create_async_engine` ist selbsterklärend |
| `database/models.py:7` | `#Base class` | `class Base(DeclarativeBase)` sagt das |
| `database/models.py:11` | `#DB Table for Users` | `__tablename__ = "users"` sagt das |

**Fix:** Alle offensichtlichen Kommentare entfernen. Nur den Kommentar in `flag_cache.py` (Klassen-Docstring) und den Kommentar im `user.py`-Validator behalten — diese erklären das Nicht-Offensichtliche.

---

### 12. Testkonzept referenziert `test_flags.py`, Datei heißt `test_game.py`

**Datei:** `docs/test-concept.md`, Kapitel 3.2

Das Dokument beschreibt `tests/integration/test_flags.py`, die tatsächliche Datei ist `tests/integration/test_game.py`. Kleiner Dokumentationsbruch.

---

### 13. `pytest.ini` — `testpaths = tests` ohne Architekturtests

Zusammen mit Issue #3: wenn Architekturtests nach `tests/architecture/` verschoben werden, sollte `pytest.ini` nicht geändert werden müssen — sie werden automatisch gefunden.

---

## Was bereits gut ist

- **Repository-Pattern** sauber umgesetzt: Routers → Services → Repositories → Database. Keine direkten DB-Queries in Routers.
- **Architekturtests** decken 10 Abhängigkeitsregeln ab — gute Abdeckung der Schichtenarchitektur.
- **FlagCache-Resilience**: Fehler beim Startup-Load (HTTP-Error, JSON-Error, non-200) werden abgefangen, Cache bleibt leer, kein Crash. Vollständig mit `respx` getestet.
- **JWT-Security**: Expired, tampered und garbage tokens werden korrekt abgelehnt (Unit- und Integrationstests vorhanden).
- **Score-Manipulation verhindert**: `SaveSessionRequest` enthält kein `score`-Feld. Score wird serverseitig aus der Session gelesen — Client kann keinen Wert manipulieren. Explizit getestet.
- **Input-Validierung**: `RegisterRequest` hat `pattern=r"^[a-zA-Z0-9_-]+$"` und `min_length=8` — SQL-Injection im Username wird schon durch Pydantic blockiert.
- **Pydantic v2 + SQLAlchemy 2.x** moderne Versionen, kein Legacy-Code.
- **6 ADRs** mit klaren Konsequenzen dokumentiert.
- **arc42** vollständig (Kapitel 01–12 vorhanden).

---

## Priorisierte To-Do-Liste

| Prio | Task | Aufwand |
|---|---|---|
| 🔴 1 | `sonar.coverage.skip=true` entfernen + `sonar-project.properties` vervollständigen | ~15 min |
| 🔴 2 | `build.yml` so anpassen dass Coverage-XML vor Sonar-Scan erzeugt wird | ~30 min |
| 🔴 3 | Architekturtests nach `tests/architecture/` verschieben, CI-Job einkommentieren | ~20 min |
| 🔴 4 | `--cov-fail-under=80` zu allen pytest-Aufrufen in CI hinzufügen | ~5 min |
| 🔴 5 | e2e-Tests implementieren (`tests/e2e/test_full_flows.py`) | ~2–3h |
| 🟠 6 | `pytestarch` + `pytest` aus `requirements.txt` in `dev-requirements.txt` verschieben | ~5 min |
| 🟠 7 | `test_get_highscores_no_token` + `test_save_score_no_token`: 401 → 403 | ~5 min |
| 🟠 8 | `GameSessionStore`-Leak in `11_risks_and_technical_debts.md` dokumentieren | ~10 min |
| 🟡 9 | Sicherheitstests in eigene Datei `tests/integration/test_security.py` auslagern | ~30 min |
| 🟡 10 | Offensichtliche Inline-Kommentare + Tippfehler "Middelware" entfernen | ~10 min |
| 🟡 11 | `test-concept.md`: `test_flags.py` → `test_game.py` korrigieren | ~2 min |
