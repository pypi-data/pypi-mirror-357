# 🚀 Déploiement de l'IA Autonome sur un Serveur Distant

Ce guide vous accompagne pas à pas pour déployer le bundle sur un serveur professionnel distant.

---

## ✅ Prérequis Serveur

| Élément         | Requis                              |
|------------------|--------------------------------------|
| OS              | Linux (Ubuntu/Debian/CentOS) ou macOS |
| Python          | 3.8 ou supérieur                    |
| Accès terminal  | SSH ou accès shell distant          |
| Droits          | Écriture dans le répertoire de projet |

---

## 🔧 Installation

```bash
# Cloner le projet
git clone https://... (votre dépôt ou bundle)
cd nom_du_projet

# Créer un environnement Python
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configuration des secrets
cp .env.example .env
nano .env  # Remplir les clés API si nécessaire
```

---

## ⚙️ Activer les modules

### 📄 1. Mode fichier JSON (local, recommandé)
- Créez une tâche dans `affiliate_ai/hooks/task.json`
- Exécutez :
```bash
python3 affiliate_ai/hooks/hook_handler.py
```

### 🔁 2. Planification automatique (cron)
Ajoutez à `crontab -e` :
```
0 2 * * 0 python3 /chemin/vers/affiliate_ai/modules/analyse_revenus.py >> /chemin/vers/data/logs/analyse_revenus.log 2>&1
```

### 🌐 3. Webhook (si besoin d’un accès distant)
Lancez Flask avec :
```bash
python3 api/server.py
```
⚠️ Assurez-vous que le port (ex : 5000) est ouvert via votre firewall.

---

## 🔒 Sécurité recommandée

- 🔐 Stockez les clés dans `.env` ou dans GitHub secrets
- 🛡️ Activez un pare-feu (UFW ou iptables)
- ❌ N’ouvrez pas de port inutile si vous n'utilisez pas le serveur API
- 📊 Vérifiez régulièrement les logs (`data/logs/`)

---

## 🔁 Mise à jour facile

Remplacez le dossier `/affiliate_ai` avec une nouvelle version,
puis relancez le processus (`launch.py`, `hook_handler.py`, etc.)

---

## 🧪 Tests

```bash
python3 analyse_revenus_manuel.py
python3 affiliate_ai/modules/revenus_reader.py
```

---
