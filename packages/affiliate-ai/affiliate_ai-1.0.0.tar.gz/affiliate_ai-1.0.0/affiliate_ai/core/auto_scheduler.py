"""
auto_scheduler.py – Publication autonome avec filtre intelligent IA
- Lit les règles du subreddit
- Ne publie que si conditions favorables
- Sinon, attend et réessaie plus tard
"""

import time
from datetime import datetime
from auto_publish import auto_publish
from config_loader import charger_token
from subreddit_rules import get_subreddit_rules
from config_loader import charger_config

def boucle_publication_secure():
    config = charger_config()
    subreddit = config.get("default_subreddit", "AItools")
    token = charger_token()

    while True:
        print(f"🕒 {datetime.now().isoformat()} – Vérification des règles pour r/{subreddit}")
        rules = get_subreddit_rules(subreddit, token)

        if "error" in rules:
            print("❌ Erreur de récupération des règles. Attente 15 min.")
            time.sleep(900)
            continue

        print("📜 Règles synthétisées :", rules["summary"])

        # Critères de blocage
        blocages = ["🧱", "🤖", "⚠️", "🔗"]
        if any(b in ligne for ligne in rules["summary"] for b in blocages):
            print("⛔ Subreddit trop restrictif. Nouvelle tentative dans 60 min.")
            time.sleep(3600)
            continue

        print("✅ Conditions OK. Lancement de la publication.")
        auto_publish()
        print("🛌 Attente avant prochaine publication (2h)...")
        time.sleep(7200)  # toutes les 2 heures

if __name__ == "__main__":
    boucle_publication_secure()
