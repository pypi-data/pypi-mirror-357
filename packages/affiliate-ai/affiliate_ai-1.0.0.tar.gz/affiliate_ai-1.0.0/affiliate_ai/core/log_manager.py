"""
📓 log_manager.py
Gère la journalisation des publications automatiques.
Crée un fichier `logs/publish_log.txt` contenant date, titre, plateforme, et résultat.
"""

import os
from datetime import datetime

LOG_FILE = "logs/publish_log.txt"

def log_event(platform, title, status, extra=""):
    """Enregistre un événement de publication dans le journal"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        log_line = f"[{datetime.now()}] [{platform.upper()}] {title} --> {status}"
        if extra:
            log_line += f" | {extra}"
        f.write(log_line + "\n")
    print("📝 Log enregistré.")

# Exemple
if __name__ == "__main__":
    log_event("medium", "Test publication IA", "SUCCESS", "Lien : https://medium.com/...")


def log_revenue(platform, amount, source=""):
    """Enregistre un revenu affilié (manuel ou via API)"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        log_line = f"[{datetime.now()}] [REVENUE] {platform.upper()} → +{amount:.2f}€ | {source}"
        f.write(log_line + "\n")
    print("💰 Revenu enregistré.")
