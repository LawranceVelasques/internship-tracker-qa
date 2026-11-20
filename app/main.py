from datetime import date

from flask import Flask, abort, jsonify, render_template, request

from . import db, rules


def create_app(database: str = ":memory:", today=None) -> Flask:
    """Build the app. `today` can be fixed in tests so date rules are deterministic."""
    app = Flask(__name__)
    conn = db.connect(database)
    get_today = (lambda: today) if today else date.today

    def row_or_404(app_id: int):
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
        if row is None:
            abort(404)
        return dict(row)

    @app.errorhandler(rules.ValidationError)
    def bad_request(exc):
        return jsonify(error="validation_failed", details=exc.errors), 400

    @app.errorhandler(404)
    def not_found(_):
        return jsonify(error="not_found"), 404

    @app.errorhandler(405)
    def not_allowed(_):
        return jsonify(error="method_not_allowed"), 405

    def json_body():
        data = request.get_json(silent=True)
        if data is None:
            raise rules.ValidationError({"body": "must be a JSON object"})
        return data

    @app.get("/")
    def index():
        return render_template("index.html", statuses=rules.STATUSES)

    @app.get("/api/applications")
    def list_applications():
        status = request.args.get("status")
        if status is not None and status not in rules.STATUSES:
            raise rules.ValidationError({"status": f"must be one of {', '.join(rules.STATUSES)}"})
        sql, args = "SELECT * FROM applications", ()
        if status:
            sql, args = sql + " WHERE status = ?", (status,)
        rows = conn.execute(sql + " ORDER BY id", args).fetchall()
        return jsonify([dict(r) for r in rows])

    @app.post("/api/applications")
    def create_application():
        clean = rules.validate_new(json_body(), today=get_today())
        cur = conn.execute(
            "INSERT INTO applications (company, position, location, status, applied_date, notes)"
            " VALUES (:company, :position, :location, :status, :applied_date, :notes)",
            clean,
        )
        conn.commit()
        return jsonify(row_or_404(cur.lastrowid)), 201

    @app.get("/api/applications/<int:app_id>")
    def get_application(app_id):
        return jsonify(row_or_404(app_id))

    @app.patch("/api/applications/<int:app_id>")
    def update_application(app_id):
        current = row_or_404(app_id)
        changes = json_body()
        if not isinstance(changes, dict) or not changes:
            raise rules.ValidationError({"body": "must be a non-empty JSON object"})
        merged = {k: current[k] for k in ("company", "position", "location", "status", "applied_date", "notes")}
        merged.update(changes)
        clean = rules.validate_new(merged, today=get_today())
        rules.check_transition(current["status"], clean["status"])
        conn.execute(
            "UPDATE applications SET company=:company, position=:position, location=:location,"
            " status=:status, applied_date=:applied_date, notes=:notes WHERE id=:id",
            {**clean, "id": app_id},
        )
        conn.commit()
        return jsonify(row_or_404(app_id))

    @app.delete("/api/applications/<int:app_id>")
    def delete_application(app_id):
        row_or_404(app_id)
        conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        conn.commit()
        return "", 204

    @app.get("/api/stats")
    def stats():
        counts = {s: 0 for s in rules.STATUSES}
        for row in conn.execute("SELECT status, COUNT(*) AS n FROM applications GROUP BY status"):
            counts[row["status"]] = row["n"]
        submitted = sum(counts[s] for s in rules.STATUSES if s != "Wishlist")
        reached_interview = counts["Interview"] + counts["Offer"] + counts["Accepted"]
        rate = round(reached_interview / submitted * 100, 1) if submitted else 0.0
        return jsonify(total=sum(counts.values()), by_status=counts, interview_rate_pct=rate)

    return app
