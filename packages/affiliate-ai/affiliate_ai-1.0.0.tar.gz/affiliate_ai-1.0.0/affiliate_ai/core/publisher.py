"""
publisher.py – Publication avec adaptation automatique (titre, règles, variation)
"""

import requests
import json
from pathlib import Path
from subreddit_rules import get_subreddit_rules
from variation_generator import varier_contenu

CONFIG_PATH = Path("affiliate_ai/reddit/reddit_config.json")
LOG_PATH = Path("affiliate_ai/logs/reddit_publications.json")

def charger_config():
    return json.loads(CONFIG_PATH.read_text())

def publier_sur_reddit(titre, contenu, subreddit, token):
    rules_info = get_subreddit_rules(subreddit, token)
    if "error" in rules_info:
        print("⛔ Erreur de lecture des règles :", rules_info["error"])
        return False

    print(f"📚 Règles de r/{subreddit} :")
    for ligne in rules_info["summary"]:
        print("  -", ligne)

    # Variations du contenu AVANT application des règles
    contenu = varier_contenu(contenu)

    # Adaptation selon les règles
    if any("texte" in r.lower() for r in rules_info["summary"]):
        contenu = contenu.replace("http", "[lien supprimé] http")
    if any("titre" in r.lower() for r in rules_info["summary"]):
        titre = titre.title()

    print(f"📤 Publication de '{titre}' dans r/{subreddit}...")

    post_data = {
        "title": titre,
        "sr": subreddit,
        "kind": "self",
        "text": contenu
    }
    headers = {
        "Authorization": f"bearer {token}",
        "User-Agent": "IA-Affiliate-Agent/1.0"
    }
    response = requests.post("https://oauth.reddit.com/api/submit", headers=headers, data=post_data)

    if response.status_code != 200:
        print("❌ Erreur Reddit :", response.text)
        return False

    # Ajout au log
    if LOG_PATH.exists():
        logs = json.loads(LOG_PATH.read_text())
    else:
        logs = []
    logs.append({
        "timestamp": response.headers.get("Date"),
        "title": titre,
        "subreddit": subreddit,
        "url": "https://reddit.com" + response.json().get("json", {}).get("data", {}).get("url", "/post")
    })
    LOG_PATH.write_text(json.dumps(logs, indent=2))
    print("✅ Publication réussie.")
    return True
