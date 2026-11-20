from datetime import date

import pytest

from app import create_app

TODAY = date(2027, 3, 1)  # fixed "today" so date rules give the same result every run


@pytest.fixture
def client():
    app = create_app(":memory:", today=TODAY)
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def make_app(client):
    """Create an application through the API and return its JSON."""
    def _make(**overrides):
        body = {"company": "Acme", "position": "QA Intern", "location": "Tangerang",
                "status": "Applied", "applied_date": "2027-02-01", "notes": ""}
        body.update(overrides)
        res = client.post("/api/applications", json=body)
        assert res.status_code == 201, res.get_json()
        return res.get_json()
    return _make
