# 📦 Amazon Affiliates – IA Automation Bundle

Ce package permet de générer automatiquement des contenus affiliés Amazon (avis + lien) et de les publier sur des plateformes externes.

---

## 🚀 Modules inclus

```
amazon_affiliate/
├── product_fetcher.py      → Scrape les produits Amazon à partir d’un mot-clé
├── review_generator.py     → Génère un avis IA à partir du nom du produit
├── link_builder.py         → Ajoute automatiquement le tag affilié
├── generate_bundle.py      → Pipeline complet : recherche + avis + lien
├── publisher.py            → Publication automatique sur Medium et Reddit
├── README.md               → Ce mode d’emploi
```

---

## 🧪 1. Générer des contenus affiliés

```bash
python generate_bundle.py
```

Tu peux modifier le mot-clé dans le `main()` pour cibler ta niche. Le script génère pour chaque produit :
- le titre
- le lien Amazon (non affilié)
- un avis généré par IA

---

## 🔗 2. Ajouter ton tag affilié Amazon

Utilise `link_builder.py` pour transformer les liens en liens affiliés :

```python
from link_builder import build_affiliate_link
url = "https://www.amazon.fr/dp/B00XYZ1234"
print(build_affiliate_link(url, "tonid-21"))
```

---

## 📣 3. Publier automatiquement

Configure d'abord tes identifiants dans `publisher.py` :

### Medium :
- Va sur https://medium.com/me/settings
- Génére un *Integration Token*
- Ajoute-le dans `CONFIG["medium"]["token"]`
- Récupère ton `user_id` via l'API :  
  ```bash
  curl -H "Authorization: Bearer <token>" https://api.medium.com/v1/me
  ```

### Reddit :
- Crée une app sur https://www.reddit.com/prefs/apps
- Renseigne `client_id`, `client_secret`, etc.

Ensuite tu peux lancer :

```bash
python publisher.py
```

---

## 🛡️ Bonnes pratiques

- ❌ Ne publie jamais les avis générés sur Amazon.fr
- ✅ Publie-les uniquement sur Medium, Reddit, blog Notion, PDF, réseaux
- ✅ Utilise un pseudo pour signer les articles

---

## 📌 À venir

- Module `signature_selector.py` (signatures IA aléatoires)
- Publication sur Notion / Carrd
- Génération automatique de PDF / ebooks
- Tracker SQLite des clics affiliés

---

