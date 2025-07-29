"""
subreddit_rules.py – Analyse automatique des règles d’un subreddit
"""

import requests

USER_AGENT = "IA-Affiliate-Agent/1.0 by u/YourBot"
BASE_URL = "https://oauth.reddit.com"

def get_subreddit_rules(subreddit, token):
    headers = {
        "Authorization": f"bearer {token}",
        "User-Agent": USER_AGENT
    }

    url = f"{BASE_URL}/r/{subreddit}/about/rules"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return {"error": f"Échec ({response.status_code}) : {response.text}"}

    data = response.json()
    rules = [r["short_name"] + ": " + r["description"] for r in data.get("rules", [])]

    # Génère une synthèse simple des contraintes à respecter
    synthese = []
    for rule in rules:
        lower = rule.lower()
        if "no spam" in lower or "self-promotion" in lower:
            synthese.append("⚠️ Ce subreddit limite la promo ou les liens externes.")
        if "title" in lower:
            synthese.append("📌 Titre structuré exigé.")
        if "new accounts" in lower:
            synthese.append("🧱 Compte récent interdit.")
        if "ai content" in lower:
            synthese.append("🤖 Ce sub limite les contenus IA.")
        if "link" in lower and "post" in lower:
            synthese.append("🔗 Préfère du texte plutôt que des liens.")

    return {
        "subreddit": subreddit,
        "rules": rules,
        "summary": list(set(synthese)) or ["✅ Aucune restriction bloquante détectée"]
    }
