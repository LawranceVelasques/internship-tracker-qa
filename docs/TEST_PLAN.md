# Test Plan — Internship Tracker

## 1. Scope
The system under test is a small web app for tracking internship applications: a REST API (Flask + SQLite) and a single-page UI.

**In scope:** creating, reading, updating and deleting applications; input validation; the status workflow; the statistics endpoint; the main UI flows.
**Out of scope:** authentication (the app has none), performance and load, browsers other than Chromium, mobile layouts.

## 2. Requirements under test

| ID | Requirement |
|----|-------------|
| R1 | Company and position are required, non-blank text, at most 100 characters each. |
| R2 | Status is one of Wishlist, Applied, Interview, Offer, Accepted, Rejected. Default: Wishlist. |
| R2a | A new application starts as Wishlist or Applied; later statuses are only reached by updating it. *(added after BUG-002)* |
| R3 | Applied date is a valid `YYYY-MM-DD` date, not in the future. It is required once status is past Wishlist. |
| R4 | Status may only move forward: Wishlist → Applied → Interview → Offer → Accepted. Rejected can be reached from any open stage. Accepted and Rejected are final. |
| R5 | Invalid requests return HTTP 400 with the failing field named, and save nothing. |
| R6 | Unknown records return 404; unsupported methods return 405. |
| R7 | `/api/stats` counts applications per status, and the interview rate = (Interview + Offer + Accepted) ÷ (all except Wishlist). |
| R8 | The UI lists applications, adds one from the form, changes a status from the table, shows validation errors, and deletes a row. |
| R9 | Only one open application per company and position (case and spacing ignored); a new one is allowed once the old one is Accepted or Rejected. *(added after BUG-003)* |

## 3. Approach

| Level | Tool | What it covers |
|-------|------|----------------|
| Unit | pytest | Validation and status rules in `app/rules.py`, without HTTP |
| API | pytest + Flask test client | Every endpoint, status codes, response bodies, error cases |
| End-to-end | Playwright (Chromium) | The page as a user sees it, against a real running server |

Techniques used: **equivalence partitioning** (valid/invalid statuses), **boundary value analysis** (100 vs 101 characters; today vs tomorrow; 29 Feb in a leap year), **state transition testing** (every allowed and every forbidden status change, generated from the transition table), and **negative testing** (wrong types, malformed JSON, unknown fields, HTML and SQL-like input). **Exploratory testing** in the UI found BUG-002 and BUG-003; each fix came with regression tests.

"Today" is fixed at 2027-03-01 in tests so date rules give the same result on every run.

## 4. Environment
Python 3.12, Flask 3, SQLite in memory (a fresh database per test), Chromium via Playwright. Tests run on every push in GitHub Actions.

## 5. Entry and exit criteria
- **Entry:** the app starts and `GET /` returns 200.
- **Exit:** all tests pass in CI; every requirement R1–R9 is covered by at least one test (see [TEST_CASES.md](TEST_CASES.md)); every bug found is logged in [BUG_REPORTS.md](BUG_REPORTS.md).

## 6. Risks
- Date rules depend on the current day → mitigated by injecting a fixed date.
- UI tests can be flaky on timing → mitigated by Playwright's auto-waiting `expect` assertions instead of sleeps.
