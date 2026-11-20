"""Rules added after exploratory testing found BUG-002 and BUG-003 (see docs/BUG_REPORTS.md)."""
import pytest


@pytest.mark.parametrize("status", ["Interview", "Offer", "Accepted", "Rejected"])
def test_create_with_later_status_is_400(client, status):
    """BUG-002"""
    res = client.post("/api/applications", json={"company": "PT Accelist", "position": "BA Intern",
                                                  "status": status, "applied_date": "2027-02-18"})
    assert res.status_code == 400
    assert res.get_json()["details"]["status"] == "a new application must start as Wishlist or Applied"
    assert client.get("/api/applications").get_json() == []


def test_create_as_accepted_no_longer_inflates_interview_rate(client):
    """BUG-002: the wrong record used to push the interview rate up."""
    client.post("/api/applications", json={"company": "A", "position": "B", "status": "Applied",
                                           "applied_date": "2027-02-15"})
    client.post("/api/applications", json={"company": "C", "position": "D", "status": "Accepted",
                                           "applied_date": "2027-02-18"})
    assert client.get("/api/stats").get_json()["interview_rate_pct"] == 0.0


def test_duplicate_open_application_is_409(client, make_app):
    """BUG-003"""
    first = make_app(company="PT Accelist Lentera Indonesia", position="Business Analyst Intern")
    res = client.post("/api/applications", json={"company": "pt accelist lentera  indonesia",
                                                  "position": "Business Analyst Intern"})
    assert res.status_code == 409
    assert f"(id {first['id']})" in res.get_json()["details"]["application"]
    assert len(client.get("/api/applications").get_json()) == 1


def test_same_company_different_position_is_allowed(client, make_app):
    make_app(company="SIRCLO", position="QA Intern")
    assert client.post("/api/applications", json={"company": "SIRCLO",
                                                  "position": "Data Intelligence Intern"}).status_code == 201


@pytest.mark.parametrize("final", ["Rejected", "Accepted"])
def test_can_apply_again_after_a_closed_application(client, make_app, final):
    """A closed application (e.g. rejected last batch) does not block applying again."""
    old = make_app(company="GLI", position="QA Intern", status="Applied")
    if final == "Accepted":
        for step in ["Interview", "Offer"]:
            client.patch(f"/api/applications/{old['id']}", json={"status": step})
    client.patch(f"/api/applications/{old['id']}", json={"status": final})
    assert client.post("/api/applications", json={"company": "GLI", "position": "QA Intern"}).status_code == 201
