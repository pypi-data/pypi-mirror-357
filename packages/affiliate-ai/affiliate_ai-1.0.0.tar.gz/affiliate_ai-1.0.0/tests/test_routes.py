import unittest
from affiliate_ai.ui.routes.controle import controle_bp
from flask import Flask

class TestControleRoutes(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(controle_bp)
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_formulaire_controle(self):
        response = self.client.get("/controle")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Contrôle manuel".encode("utf-8"), response.data)

    def test_logs_endpoint(self):
        response = self.client.get("/controle/logs")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"[", response.data)

if __name__ == '__main__':
    unittest.main()
