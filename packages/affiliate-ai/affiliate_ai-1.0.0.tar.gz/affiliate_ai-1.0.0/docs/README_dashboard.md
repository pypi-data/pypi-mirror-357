# 🧩 Intégrer le module Dashboard IA

## 📂 Fichier
- `api/routes/dashboard.py` → ajoute la route `/admin`

## 🧰 Intégration dans server.py
```python
from api.routes.dashboard import dashboard_bp
app.register_blueprint(dashboard_bp)
```

## 📦 Accès
- http://localhost:5000/admin
