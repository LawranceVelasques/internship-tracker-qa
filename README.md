# Internship Tracker — QA Automation Project

A small web app for tracking internship applications, built as the **system under test** for a QA portfolio project. The focus is the testing: a written test plan, 29 documented test cases mapped to requirements, **81 automated tests** across three levels, a real bug report, and CI on every push.

## What's tested

| Level | Tool | Tests |
|-------|------|-------|
| Unit — validation & status rules | pytest | 44 |
| API — every endpoint and error case | pytest + Flask test client | 32 |
| End-to-end — the UI in a real browser | Playwright (Chromium) | 5 |

Techniques: equivalence partitioning, boundary value analysis, state transition testing (every allowed and forbidden status change is generated from the transition table), and negative testing (malformed JSON, wrong types, unknown fields, HTML/SQL-like input).

- 📄 [Test plan](docs/TEST_PLAN.md) — scope, requirements, approach, exit criteria
- ✅ [Test cases](docs/TEST_CASES.md) — 29 cases, each linked to a requirement and its automated test
- 🐞 [Bug reports](docs/BUG_REPORTS.md) — a bug the end-to-end tests caught, with cause and fix

## The app

REST API (Flask + SQLite) and a one-page UI.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/applications?status=` | List, optionally filtered by status |
| POST | `/api/applications` | Create |
| GET / PATCH / DELETE | `/api/applications/<id>` | Read, update, delete |
| GET | `/api/stats` | Count per status and interview rate |

Status workflow: `Wishlist → Applied → Interview → Offer → Accepted`, with `Rejected` reachable from any open stage. `Accepted` and `Rejected` are final.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium

flask --app "app:create_app('tracker.db')" run       # open http://127.0.0.1:5000
pytest                     # all tests
pytest -m "not e2e"        # unit + API only (no browser needed)
pytest -m e2e              # browser tests only
```

## Project structure

```
app/            the system under test (Flask API, rules, UI)
tests/          test_rules.py (unit) · api/ (API) · e2e/ (Playwright)
docs/           test plan, test cases, bug reports
.github/        CI: runs all tests and uploads JUnit reports
```
