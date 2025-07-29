# 🤖 README_REDDIT.md – Publication Automatisée IA sur Reddit

## 🎯 Objectif :
Poster automatiquement des avis IA contenant des liens affiliés Amazon dans des subreddits pertinents, de façon naturelle et non intrusive.

---

## 🔐 Authentification Reddit (API)

1. Crée un compte Reddit.
2. Va sur https://www.reddit.com/prefs/apps
3. Clique "Créer une application".
4. Type : **Script**
5. Redirect URI : `http://localhost:8080`
6. Récupère :
   - client_id
   - client_secret
   - username
   - password

---

## 🗂️ Fichier `reddit_config.json` :

```json
{
  "client_id": "VOTRE_CLIENT_ID",
  "client_secret": "VOTRE_CLIENT_SECRET",
  "username": "VotrePseudoReddit",
  "password": "VotreMotDePasseReddit",
  "user_agent": "IA_affiliate_bot by /u/VotrePseudoReddit"
}
```

---

## ⚙️ Modules inclus :

- `publisher.py` : publie l’avis IA sur Reddit
- `scheduler.py` : planifie les publications Reddit
- `log_manager.py` : log des publications (succès/échec)
- `reddit_config.json` : identifiants stockés localement

---

## ✅ À faire avant de lancer :

- Renseigner correctement `reddit_config.json`
- Réchauffer le compte Reddit avec des interactions normales
- Lancer le scheduler (`python scheduler.py`) ou programmer une tâche

---

## 🚫 À éviter :
- Titre trop agressif ou pub
- Trop de posts trop vite (risque de bannissement)
- Absence de texte accompagnant le lien

---

## Exemple de post :

**Titre** : "Ce petit accessoire m’a sauvé la nuque au bureau"  
**Texte** :
```
J’ai découvert ce support pour mon écran sur Amazon. Ultra simple mais efficace.

👉 Voici le lien : https://amazon.fr/dp/XXXX?tag=tonid-21

Et vous, vous utilisez quoi ?
```
