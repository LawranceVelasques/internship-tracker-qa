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
