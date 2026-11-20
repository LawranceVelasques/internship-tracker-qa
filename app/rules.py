"""Business rules for an internship application, kept apart from Flask so they can be unit tested."""
from datetime import date

STATUSES = ["Wishlist", "Applied", "Interview", "Offer", "Accepted", "Rejected"]

# Which status can follow which. "Rejected" can be reached from any open stage;
# "Accepted" and "Rejected" are final.
TRANSITIONS = {
    "Wishlist": {"Applied", "Rejected"},
    "Applied": {"Interview", "Offer", "Rejected"},
    "Interview": {"Interview", "Offer", "Rejected"},
    "Offer": {"Accepted", "Rejected"},
    "Accepted": set(),
    "Rejected": set(),
}

MAX_LEN = {"company": 100, "position": 100, "location": 100, "notes": 1000}


class ValidationError(ValueError):
    def __init__(self, errors: dict):
        super().__init__("; ".join(f"{k}: {v}" for k, v in errors.items()))
        self.errors = errors


def _parse_date(value):
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError("must be a date string YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        raise ValueError("must be a valid date in YYYY-MM-DD format")
    if len(value) != 10:
        raise ValueError("must be a valid date in YYYY-MM-DD format")
    return parsed


def validate_new(data, today: date | None = None) -> dict:
    """Return a cleaned record for a new application, or raise ValidationError."""
    today = today or date.today()
    if not isinstance(data, dict):
        raise ValidationError({"body": "must be a JSON object"})
    errors, clean = {}, {}

    for field in ("company", "position"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors[field] = "is required"
        else:
            clean[field] = value.strip()

    for field in ("location", "notes"):
        value = data.get(field, "")
        if value is None:
            value = ""
        if not isinstance(value, str):
            errors[field] = "must be text"
        else:
            clean[field] = value.strip()

    for field, limit in MAX_LEN.items():
        if field in clean and len(clean[field]) > limit:
            errors[field] = f"must be at most {limit} characters"

    status = data.get("status", "Wishlist")
    if status not in STATUSES:
        errors["status"] = f"must be one of {', '.join(STATUSES)}"
    else:
        clean["status"] = status

    try:
        applied = _parse_date(data.get("applied_date"))
        if applied and applied > today:
            errors["applied_date"] = "cannot be in the future"
        clean["applied_date"] = applied.isoformat() if applied else None
    except ValueError as exc:
        errors["applied_date"] = str(exc)

    if clean.get("status") not in (None, "Wishlist") and not clean.get("applied_date") and "applied_date" not in errors:
        errors["applied_date"] = "is required once the status is past Wishlist"

    unknown = set(data) - {"company", "position", "location", "notes", "status", "applied_date"}
    if unknown:
        errors["body"] = f"unknown field(s): {', '.join(sorted(unknown))}"

    if errors:
        raise ValidationError(errors)
    return clean


def check_transition(current: str, new: str) -> None:
    if new not in STATUSES:
        raise ValidationError({"status": f"must be one of {', '.join(STATUSES)}"})
    if new != current and new not in TRANSITIONS[current]:
        raise ValidationError({"status": f"cannot change from {current} to {new}"})
