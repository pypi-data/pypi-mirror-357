"""
revenus.py – Analyse des gains affiliés + alerte automatique
"""

import matplotlib.pyplot as plt
from collections import defaultdict
import datetime
from affiliate_ai.core.alert_manager import send_email

LOG_FILE = "affiliate_ai/logs/publish_log.txt"

def lire_logs():
    revenus = defaultdict(float)
    plateformes = defaultdict(float)
    with open(LOG_FILE, "r") as f:
        for ligne in f:
            if "GAIN:" in ligne:
                parts = ligne.strip().split("GAIN:")[-1].split("€")
                montant = float(parts[0].strip())
                date = ligne.split(" - ")[0]
                plateforme = ligne.split("plateforme:")[-1].split()[0]
                revenus[date] += montant
                plateformes[plateforme] += montant
    return revenus, plateformes

def afficher_stats(revenus, plateformes):
    total = sum(revenus.values())
    print(f"💰 Total des revenus : {total:.2f} €")
    for jour, val in revenus.items():
        print(f"📆 {jour} : {val:.2f} €")
    for plat, val in plateformes.items():
        print(f"🛰️ {plat} : {val:.2f} €")

    # Envoi automatique de l’alerte par mail
    if total > 0:
        today = datetime.datetime.now().strftime("%d/%m/%Y")
        send_email(f"🎯 Bilan IA du {today}", f"Tu as généré {total:.2f} € aujourd’hui avec ton IA !")

    # Affichage graphique
    jours = list(revenus.keys())
    montants = list(revenus.values())
    plt.bar(jours, montants)
    plt.title("Revenus par jour")
    plt.ylabel("€ gagnés")
    plt.xlabel("Date")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    rev, plat = lire_logs()
    afficher_stats(rev, plat)
