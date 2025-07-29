# Guide de développement PhoenixProject

## 🚀 Publication sur PyPI

### Prérequis
- Compte PyPI : https://pypi.org/account/register/
- Token API PyPI : https://pypi.org/manage/account/token/

### Configuration sécurisée

#### Option 1 : Variables d'environnement (recommandé)
```bash
# Linux/Mac
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-VOTRE_TOKEN_ICI

# Windows PowerShell
$env:TWINE_USERNAME = '__token__'
$env:TWINE_PASSWORD = 'pypi-VOTRE_TOKEN_ICI'
```

#### Option 2 : Fichier .pypirc (local uniquement)
Le script `scripts/upload_to_pypi.py` créera automatiquement un template `.pypirc`.
Remplacez `pypi-VOTRE_TOKEN_ICI` par votre token personnel.

### Processus de publication

1. **Construire le package** :
   ```bash
   python -m build
   ```

2. **Vérifier le package** :
   ```bash
   python -m twine check dist/*
   ```

3. **Publier** :
   ```bash
   python scripts/upload_to_pypi.py
   ```

### Sécurité

- ✅ **Jamais** commiter de tokens dans le code
- ✅ **Toujours** utiliser `.pypirc` ou variables d'environnement
- ✅ Le fichier `.pypirc` est dans `.gitignore`
- ✅ Chaque développeur utilise son propre token

### Structure du projet

```
unified_affiliate_bundle/
├── affiliate_ai/          # Code source principal
├── docs/                  # Documentation
├── scripts/               # Scripts utilitaires
│   └── upload_to_pypi.py  # Script d'upload sécurisé
├── tests/                 # Tests automatiques
├── setup.py              # Configuration du package
├── MANIFEST.in           # Fichiers à inclure
├── .gitignore            # Fichiers à ignorer
└── README.md             # Documentation principale
```

### Tests

```bash
# Tests avec couverture
python test_all.py

# Tests unitaires
python -m pytest tests/
```

### Développement local

```bash
# Installation en mode développement
pip install -e .

# Lancement du CLI
phoenixproject
```

---

**⚠️ Important** : Chaque développeur doit utiliser son propre token PyPI personnel ! 