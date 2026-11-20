"""Unit tests for the business rules (no HTTP)."""
from datetime import date

import pytest

from app.rules import STATUSES, TRANSITIONS, ValidationError, check_transition, validate_new

TODAY = date(2027, 3, 1)


def test_minimal_record_gets_defaults():
    clean = validate_new({"company": "Acme", "position": "QA Intern"}, today=TODAY)
    assert clean == {"company": "Acme", "position": "QA Intern", "location": "", "notes": "",
                     "status": "Wishlist", "applied_date": None}


def test_whitespace_is_trimmed():
    clean = validate_new({"company": "  Acme  ", "position": "\tQA\n"}, today=TODAY)
    assert (clean["company"], clean["position"]) == ("Acme", "QA")


@pytest.mark.parametrize("applied", ["2027-03-01", "2027-02-28", "2024-02-29"])
def test_dates_up_to_today_are_accepted(applied):
    assert validate_new({"company": "A", "position": "B", "status": "Applied",
                         "applied_date": applied}, today=TODAY)["applied_date"] == applied


def test_date_one_day_in_the_future_is_rejected():
    with pytest.raises(ValidationError) as exc:
        validate_new({"company": "A", "position": "B", "status": "Applied",
                      "applied_date": "2027-03-02"}, today=TODAY)
    assert exc.value.errors == {"applied_date": "cannot be in the future"}


@pytest.mark.parametrize("bad", ["2027-02-30", "01-03-2027", "20270301", "yesterday", 20270301])
def test_malformed_dates_are_rejected(bad):
    with pytest.raises(ValidationError) as exc:
        validate_new({"company": "A", "position": "B", "applied_date": bad}, today=TODAY)
    assert "applied_date" in exc.value.errors


def test_boundary_lengths():
    ok = validate_new({"company": "x" * 100, "position": "B"}, today=TODAY)
    assert len(ok["company"]) == 100
    with pytest.raises(ValidationError) as exc:
        validate_new({"company": "x" * 101, "position": "B"}, today=TODAY)
    assert exc.value.errors["company"] == "must be at most 100 characters"


@pytest.mark.parametrize("current,new", [(c, n) for c in STATUSES for n in TRANSITIONS[c]])
def test_every_allowed_transition_passes(current, new):
    check_transition(current, new)


@pytest.mark.parametrize("current,new", [
    (c, n) for c in STATUSES for n in STATUSES if n != c and n not in TRANSITIONS[c]
])
def test_every_forbidden_transition_fails(current, new):
    with pytest.raises(ValidationError):
        check_transition(current, new)


def test_final_statuses_have_no_way_out():
    assert TRANSITIONS["Accepted"] == set() and TRANSITIONS["Rejected"] == set()
