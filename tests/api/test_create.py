import pytest


def test_create_returns_201_with_id(client):
    res = client.post("/api/applications", json={"company": "SIRCLO", "position": "QA Intern"})
    assert res.status_code == 201
    body = res.get_json()
    assert body["id"] == 1
    assert body["status"] == "Wishlist"


def test_created_record_can_be_read_back(client, make_app):
    created = make_app(company="BFI Finance", position="Data Analyst Intern")
    res = client.get(f"/api/applications/{created['id']}")
    assert res.status_code == 200
    assert res.get_json() == created


@pytest.mark.parametrize("body,field", [
    ({"position": "QA"}, "company"),
    ({"company": "Acme"}, "position"),
    ({"company": "   ", "position": "QA"}, "company"),
    ({"company": 123, "position": "QA"}, "company"),
    ({"company": "Acme", "position": "QA", "status": "Ghosted"}, "status"),
    ({"company": "Acme", "position": "QA", "status": "Applied"}, "applied_date"),
    ({"company": "Acme", "position": "QA", "salary": 5}, "body"),
])
def test_invalid_input_returns_400_naming_the_field(client, body, field):
    res = client.post("/api/applications", json=body)
    assert res.status_code == 400
    assert field in res.get_json()["details"]


def test_invalid_input_is_not_saved(client):
    client.post("/api/applications", json={"company": "Acme"})
    assert client.get("/api/applications").get_json() == []


@pytest.mark.parametrize("payload", ["not json", "[1, 2]", "null"])
def test_non_object_body_returns_400(client, payload):
    res = client.post("/api/applications", data=payload, content_type="application/json")
    assert res.status_code == 400


def test_html_in_notes_is_stored_as_plain_text(client):
    script = "<script>alert(1)</script>"
    created = client.post("/api/applications",
                          json={"company": "Acme", "position": "QA", "notes": script}).get_json()
    assert created["notes"] == script


def test_sql_like_input_is_stored_literally(client, make_app):
    name = "Robert'); DROP TABLE applications;--"
    make_app(company=name)
    rows = client.get("/api/applications").get_json()
    assert [r["company"] for r in rows] == [name]
