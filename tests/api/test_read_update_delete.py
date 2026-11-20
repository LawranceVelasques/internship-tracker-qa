import pytest


def test_list_is_empty_at_start(client):
    assert client.get("/api/applications").get_json() == []


def test_list_filters_by_status(client, make_app):
    make_app(company="A", status="Applied")
    make_app(company="B", status="Wishlist", applied_date=None)
    res = client.get("/api/applications?status=Wishlist").get_json()
    assert [r["company"] for r in res] == ["B"]


def test_list_with_unknown_status_filter_is_400(client):
    assert client.get("/api/applications?status=Unknown").status_code == 400


@pytest.mark.parametrize("method", ["get", "patch", "delete"])
def test_missing_record_is_404(client, method):
    res = getattr(client, method)("/api/applications/999", json={"notes": "x"})
    assert res.status_code == 404
    assert res.get_json() == {"error": "not_found"}


def test_patch_updates_only_given_fields(client, make_app):
    created = make_app()
    res = client.patch(f"/api/applications/{created['id']}", json={"notes": "HR replied"})
    assert res.status_code == 200
    assert res.get_json() == {**created, "notes": "HR replied"}


def test_patch_follows_status_flow(client, make_app):
    app_id = make_app(status="Applied")["id"]
    for step in ["Interview", "Offer", "Accepted"]:
        res = client.patch(f"/api/applications/{app_id}", json={"status": step})
        assert res.status_code == 200, res.get_json()
    assert client.get(f"/api/applications/{app_id}").get_json()["status"] == "Accepted"


def test_patch_rejects_going_back_from_final_status(client, make_app):
    app_id = make_app(status="Applied")["id"]
    client.patch(f"/api/applications/{app_id}", json={"status": "Rejected"})
    res = client.patch(f"/api/applications/{app_id}", json={"status": "Interview"})
    assert res.status_code == 400
    assert res.get_json()["details"]["status"] == "cannot change from Rejected to Interview"


def test_failed_patch_leaves_record_unchanged(client, make_app):
    created = make_app()
    client.patch(f"/api/applications/{created['id']}", json={"applied_date": "2099-01-01"})
    assert client.get(f"/api/applications/{created['id']}").get_json() == created


def test_empty_patch_is_400(client, make_app):
    assert client.patch(f"/api/applications/{make_app()['id']}", json={}).status_code == 400


def test_delete_then_get_is_404(client, make_app):
    app_id = make_app()["id"]
    assert client.delete(f"/api/applications/{app_id}").status_code == 204
    assert client.get(f"/api/applications/{app_id}").status_code == 404


def test_ids_are_not_reused_after_delete(client, make_app):
    first = make_app()["id"]
    client.delete(f"/api/applications/{first}")
    assert make_app()["id"] != first


def test_unsupported_method_is_405(client):
    assert client.put("/api/applications").status_code == 405
