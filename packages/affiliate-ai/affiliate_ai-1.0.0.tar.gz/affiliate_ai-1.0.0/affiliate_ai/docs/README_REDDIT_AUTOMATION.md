# 🤖 Affiliate AI – Fonctionnement & Automatisation

---

## 🎯 Objectif
Une IA autonome capable de générer, publier et monétiser automatiquement des **avis de produits affiliés** sur Reddit et d'autres plateformes, de manière **naturelle**, **discrète**, et **rentable**.

---

## 📦 Structure des modules

| Module | Rôle |
|--------|------|
| `review_generator.py` | Génère un avis IA à partir d’un produit |
| `publisher.py` | Publie l’avis sur Reddit, en respectant les règles |
| `subreddit_rules.py` | Analyse les règles du subreddit en temps réel |
| `variation_generator.py` | Génère des variantes du contenu pour éviter le spam |
| `auto_publish.py` | Pipeline automatique (produit → avis → publication) |
| `auto_scheduler.py` | Boucle autonome avec contrôle des règles et temporisation |
| `reddit_logs_web.py` | Interface Web pour voir / republier les posts |
| `config_loader.py` | Charge les tokens et configurations sensibles |

---

## ⚙️ Fonctionnement du pipeline

1. Sélection aléatoire d’un produit dans `produits.json`
2. Génération d’un avis IA (formulé naturellement)
3. Variation automatique du contenu (anti-spam)
4. Vérification des règles Reddit (`about/rules`)
5. Adaptation du contenu (lien supprimé, titre formaté)
6. Publication sur Reddit (si règles compatibles)
7. Enregistrement dans les logs JSON
8. Possibilité de republier ailleurs automatiquement

---

## 🔁 Republier un post Reddit

- Interface : `/reddit-logs`
- Boutons :
  - 📤 Republier avec subreddit / titre modifié
  - 🗑 Supprimer l’entrée du log
- Le contenu est **légèrement modifié** automatiquement

---

## 🔐 Sécurité & Respect des règles

✅ Grâce à `subreddit_rules.py` :
- L’IA évite les subreddits hostiles à l’IA, aux nouveaux comptes ou à la promotion
- Elle adapte chaque publication avant de l’envoyer
- Elle attend 2h entre deux publications (scheduler)

---

## 💻 Lancer l'automatisation

```bash
# Pour publier une fois (test)
python affiliate_ai/core/auto_publish.py

# Pour une boucle permanente sécurisée
python affiliate_ai/core/auto_scheduler.py

# Pour accéder à l’interface Web des logs
http://localhost:5000/reddit-logs
```

---

## 🧠 À venir
- Plugin Medium / X / LinkedIn
- Choix dynamique de subreddit selon les tendances
- Filtrage des produits par saison / événement
- Tracking complet des revenus et clics (via shorteners)

---

© PhoenixProject 2025 – All rights protected 🕊️
