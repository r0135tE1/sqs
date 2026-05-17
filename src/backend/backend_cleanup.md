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

### Schritt 12 — `src/backend/tests/integration/`  `✅ REVIEWED`

```
src/backend/tests/integration/test_health.py
src/backend/tests/integration/test_auth.py
src/backend/tests/integration/test_game.py
src/backend/tests/integration/test_highscores.py
src/backend/tests/integration/test_flag_cache_load.py
```

---

### Schritt 13 — Fixes umsetzen  `→ AKTUELL`

Alle identifizierten Issues aus dem Cleanup (siehe unten) gemeinsam beheben.

---

## Gesamtstatus

| Anforderung (Checkliste) | Status | Problem |
|---|---|---|
| Unit-Tests | ✅ | vorhanden & laufen in CI |
| Integration-Tests | ✅ | vorhanden & laufen in CI |
| e2e-Tests | ❌ | nur im Testkonzept beschrieben, kein Code |
| Penetration-Tests | ⚠️ | OWASP ZAP erwähnt, nicht implementiert |
| Architekturtests | ⚠️ | Code vorhanden, CI-Job auskommentiert (bewusst zurückgestellt) |
| Lauffähige GitHub-Pipeline | ⚠️ | unit + integration laufen, arc-tests fehlen in CI |
| Statische Analyse ≥80% Coverage | ❌ | `sonar.coverage.skip=true` — bewusst zurückgestellt |
| Resilience / Ausfallsichere Muster | ✅ | FlagCache mit graceful degradation |
| arc42-Dokumentation | ✅ | vollständig vorhanden |
| ADRs | ✅ | 6 ADRs dokumentiert |

---

## Offene Issues (zurückgestellt)

### 1. `sonar.coverage.skip=true` — Coverage komplett deaktiviert

**Datei:** `sonar-project.properties`, Zeile 8 — bewusst zurückgestellt, separater Schritt.

**Fix:**
```properties
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

---

### 2. Architekturtests + Coverage nicht in CI

- `backend-architecture`-Job in `tests.yml` ist auskommentiert — bewusst zurückgestellt.
- `--cov-fail-under=80` fehlt in beiden pytest-Aufrufen in CI.
- `app/tests/test_architecture.py` liegt außerhalb von `testpaths = tests`.

**Fix:** CI-Job einkommentieren, `--cov-fail-under=80` ergänzen, Architekturtests nach `tests/architecture/` verschieben oder `testpaths` erweitern.

---

### 3. Keine e2e-Tests implementiert

`tests/e2e/test_full_flows.py` existiert nicht. Mindestens drei Flows nötig:
1. Guest-Flow: Session → 5× Flag holen → 404
2. Auth-Flow: Register → Login → Highscore speichern → abrufen
3. Token-Expiry: abgelaufenes Token → 401

---

### 4. Testkonzept referenziert `test_flags.py`, Datei heißt `test_game.py`

**Datei:** `docs/test-concept.md`, Kapitel 3.2

---

## Was bereits gut ist

- **Repository-Pattern** sauber umgesetzt: Routers → Services → Repositories → Database.
- **Architekturtests** decken 11 Abhängigkeitsregeln ab — alle grün (86/86 Tests).
- **FlagCache-Resilience**: Fehler beim Startup-Load werden abgefangen, Cache bleibt leer, kein Crash.
- **JWT-Security**: Expired, tampered und garbage tokens werden korrekt abgelehnt.
- **Score-Manipulation verhindert**: `SaveSessionRequest` hat kein `score`-Feld, Score wird serverseitig gelesen.
- **Session-Cleanup**: `delete_session` löscht Session + verwaiste Questions nach Highscore-Speicherung.
- **`upsert` gibt `bool` zurück**: Repository-Pattern sauber — keine User-facing Messages im Repository.
- **SVG direkt in `random_flag`**: Kein separater `get_svg`-Call im Router nötig, toter 503-Zweig entfernt.
- **`get_correct_answer`**: Öffentliche Methode statt Direktzugriff auf `_questions` in Tests.
- **13 Security-Tests** in `tests/integration/test_security.py`: Input Validation, Auth Bypass, Score Manipulation.
- **Input-Validierung**: `pattern=r"^[a-zA-Z0-9_-]+$"` blockiert SQL-Injection im Username.
- **Pydantic v2 + SQLAlchemy 2.x** — keine Legacy-Abhängigkeiten.
- **6 ADRs**, **arc42** vollständig vorhanden.

---

## Offene To-Do-Liste

| Prio | Task | Aufwand |
|------|---|---|
| 🔴 1 | `sonar.coverage.skip=true` entfernen + `sonar-project.properties` vervollständigen | ~15 min |
| 🔴 2 | `build.yml` so anpassen dass Coverage-XML vor Sonar-Scan erzeugt wird | ~30 min |
| 🔴 3 | Architekturtests in CI einkommentieren + `--cov-fail-under=80` ergänzen | ~20 min |
| 🔴 4 | e2e-Tests implementieren (`tests/e2e/test_full_flows.py`) | ~2–3h |
| 🟡 5 | `test-concept.md`: `test_flags.py` → `test_game.py` korrigieren | ~2 min |
