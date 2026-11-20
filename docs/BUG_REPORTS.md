# Bug Reports

Bugs found while testing, written in the format I would file in a tracker.

---

## BUG-001 — Interview rate shown as "0%" in the UI but "0.0" in the API

| Field | Value |
|-------|-------|
| Severity | Low (display only) |
| Priority | Medium (inconsistent numbers erode trust in the stats) |
| Found by | `e2e/test_ui.py::test_empty_state` |
| Status | Fixed |

**Steps to reproduce**
1. Start the app with an empty database.
2. Open `/`.
3. Compare the stats line with `GET /api/stats`.

**Expected:** `0 application(s) · interview rate 0.0%`, matching the API's one-decimal value.
**Actual:** `0 application(s) · interview rate 0%`.

**Cause:** the API returns `0.0`, but JSON has no separate float type, so the browser receives the number `0` and prints it without a decimal. Any whole-number rate (0, 50, 100) lost its decimal place.

**Fix:** format the rate with `toFixed(1)` in `index.html`. The end-to-end test now guards it.

---

## BUG-002 — A new application can be created straight as "Accepted", skipping the status flow

| Field | Value |
|-------|-------|
| Severity | Medium (wrong data, and the interview rate is inflated) |
| Priority | High |
| Found by | Exploratory testing in the UI |
| Status | Fixed |

**Steps to reproduce**
1. Open `/`.
2. Add *PT Accelist Lentera Indonesia — Business Analyst Intern*, status **Applied**, date 2026-11-15.
3. Add the same role again with status **Accepted**, date 2026-11-18.

**Expected:** a new application can only start as Wishlist or Applied. Interview, Offer and Accepted are reached by updating it (requirement R4).
**Actual:** the record is saved as Accepted, and the stats line jumps to "interview rate 50.0%" although no interview ever happened.

**Cause:** the status flow was only enforced on updates (`check_transition` in `PATCH`). Creating a record checked only that the status was a known value.

**Fix:** `validate_new` now accepts only Wishlist or Applied when creating (new requirement R2a). The form only offers those two, and the status of an existing row is changed from a dropdown in the table, which lists only the allowed next steps.
**Regression tests:** `test_rules.py::test_new_application_cannot_skip_the_flow`, `api/test_business_rules.py::test_create_with_later_status_is_400`, `test_create_as_accepted_no_longer_inflates_interview_rate`, `e2e/test_ui.py::test_new_form_offers_only_starting_statuses`.

---

## BUG-003 — The same role can be added twice

| Field | Value |
|-------|-------|
| Severity | Low |
| Priority | Medium |
| Found by | Exploratory testing in the UI (same steps as BUG-002) |
| Status | Fixed |

**Expected:** one open application per company and position.
**Actual:** *PT Accelist Lentera Indonesia — Business Analyst Intern* was saved twice with no warning, so the totals double-count it.

**Open question raised with the product owner:** should applying again be allowed? Decision: yes, but only after the earlier application is closed (Accepted or Rejected), for example when re-applying to a later batch.

**Fix:** creating an application returns **409 Conflict** when an open application exists for the same company and position. The match ignores case and extra spaces, so `pt accelist  lentera indonesia` counts as the same company. The UI shows the message and adds nothing (new requirement R9).
**Regression tests:** `test_rules.py::test_same_role_ignores_case_and_spacing`, `api/test_business_rules.py::test_duplicate_open_application_is_409`, `test_same_company_different_position_is_allowed`, `test_can_apply_again_after_a_closed_application`, `e2e/test_ui.py::test_duplicate_shows_error`.

---

## Template

```
## BUG-XXX — <short title>
Severity / Priority / Found by / Status
Steps to reproduce:
Expected:
Actual:
Cause (if known):
Fix:
```
