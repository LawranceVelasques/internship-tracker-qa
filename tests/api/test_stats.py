def test_stats_when_empty(client):
    assert client.get("/api/stats").get_json() == {
        "total": 0,
        "by_status": {s: 0 for s in ["Wishlist", "Applied", "Interview", "Offer", "Accepted", "Rejected"]},
        "interview_rate_pct": 0.0,
    }


def test_interview_rate_ignores_wishlist(client, make_app):
    make_app(status="Wishlist", applied_date=None)   # not submitted, so not counted
    make_app(status="Applied")
    make_app(status="Applied")
    second = make_app(status="Applied")
    client.patch(f"/api/applications/{second['id']}", json={"status": "Interview"})
    stats = client.get("/api/stats").get_json()
    assert stats["total"] == 4
    assert stats["by_status"]["Interview"] == 1
    assert stats["interview_rate_pct"] == 33.3   # 1 of 3 submitted


def test_stats_follow_deletes(client, make_app):
    app_id = make_app()["id"]
    client.delete(f"/api/applications/{app_id}")
    assert client.get("/api/stats").get_json()["total"] == 0
