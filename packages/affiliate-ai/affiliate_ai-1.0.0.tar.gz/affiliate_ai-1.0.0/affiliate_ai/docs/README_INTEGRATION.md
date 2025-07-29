# 📦 PhoenixProject – Moteur IA de Publication Automatisée

Ce module vous permet de brancher une intelligence artificielle sur votre site pour :
- Publier automatiquement des avis sur Reddit et d'autres plateformes
- Suivre les revenus estimés
- Planifier des publications
- Contrôler l'IA via une interface web

---

## ⚙️ Installation

1. Placez le dossier `affiliate_ai/` dans la racine de votre projet Flask :

```
mon_site/
├── app.py
├── affiliate_ai/
├── templates/
└── ...
```

2. Installez les dépendances :
```bash
pip install flask
```

---

## 🔌 Intégration des modules

Dans votre `app.py` :

```python
from flask import Flask
from affiliate_ai.ui.routes.dashboard import dashboard_bp
from affiliate_ai.ui.routes.preview import preview_bp
from affiliate_ai.ui.routes.stats import stats_bp
from affiliate_ai.ui.routes.backup import backup_bp
from affiliate_ai.ui.routes.docs_routes import docs_bp
from affiliate_ai.ui.routes.ia_control import ia_bp
from affiliate_ai.ui.routes.planification import planif_bp
from affiliate_ai.ui.routes.dashboard_jinja import dashboard_jinja_bp

app = Flask(__name__)

# Brancher les blueprints
for bp in [dashboard_bp, preview_bp, stats_bp, backup_bp, docs_bp, ia_bp, planif_bp, dashboard_jinja_bp]:
    app.register_blueprint(bp)

app.run(debug=True)
```

---

## 🌐 Interfaces Web

| URL | Description |
|-----|-------------|
| `/dashboard-integrated` | 💻 Tableau de bord complet avec menu |
| `/preview/produit` | 🔮 Voir le prochain post IA |
| `/stats` | 📊 Stats & revenu estimé |
| `/backup/run` | 💾 Sauvegarde immédiate |
| `/backup/list` | 📂 Voir les sauvegardes |
| `/planifier/liste` | 📅 Voir les dates planifiées |

---

## 🧠 Planification Automatique

Les dates sont stockées dans `affiliate_ai/db/planifications.json`.

Pour lancer automatiquement à la bonne date :
- Créez une tâche cron qui lit ce fichier chaque jour à 6h :
```bash
0 6 * * * /usr/bin/python3 /chemin/vers/publisher.py --auto-planification
```

Un module à venir lit ce fichier et publiera automatiquement les produits prévus.

---

## 🔐 Configuration

- Le fichier `server_config.py` permet d’adapter le port, debug, IA activée
- Les mots de passe peuvent être stockés de manière chiffrée
- L’IA peut être activée/désactivée via `/toggle/ia`

---

## 💡 Astuce : Intégration via iFrame

Dans une interface existante :
```html
<iframe src="http://localhost:5000/dashboard-integrated" width="100%" height="1000px"></iframe>
```

---

## 🧱 Installation Packagée (prochainement)

Nous préparons un installeur :
```
python -m phoenixproject install
```

📬 Pour être notifié : contact@phoenixproject.ai
