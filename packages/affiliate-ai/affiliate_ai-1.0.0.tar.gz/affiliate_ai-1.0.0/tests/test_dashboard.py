def test_dashboard_accessible():
    from flask import Flask
    from api.routes.dashboard import dashboard_bp
    app = Flask(__name__)
    app.register_blueprint(dashboard_bp)
    client = app.test_client()
    resp = client.get('/admin')
    assert resp.status_code == 200
