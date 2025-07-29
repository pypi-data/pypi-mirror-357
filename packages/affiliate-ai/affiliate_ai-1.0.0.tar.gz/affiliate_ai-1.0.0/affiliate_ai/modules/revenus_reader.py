import os
import json
from datetime import datetime
from pathlib import Path

def lire_revenus(depuis="mock", sauvegarde_path="data/revenus.json"):
    if depuis == "mock":
        revenus = {
            "source": "Amazon",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "clics": 17,
            "achats": 4,
            "revenu": 9.42
        }
    else:
        print("⚠️ Seul le mode 'mock' est actif par défaut. Configurez les API dans `.env` pour activer d'autres sources.")
        return

    sauvegarder_revenus(revenus, sauvegarde_path)

def sauvegarder_revenus(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if Path(path).exists():
        historique = json.loads(Path(path).read_text())
        historique.append(data)
    else:
        historique = [data]
    Path(path).write_text(json.dumps(historique, indent=2))
    print(f"✅ Revenus enregistrés dans {path}")

if __name__ == "__main__":
    print("""
⚠️ Cette fonctionnalité lit vos revenus depuis les sources affiliées configurées.
   Par défaut, seul le mode mock (faux revenu) est actif.

🔐 Activez les sources réelles uniquement si :
 - Vous avez bien stocké vos clés API dans .env
 - Vous comprenez que le script lit vos revenus mais ne gère aucun paiement.

💡 Pour l’instant, seul le mode Amazon mock est actif.
    """)
    lire_revenus()
