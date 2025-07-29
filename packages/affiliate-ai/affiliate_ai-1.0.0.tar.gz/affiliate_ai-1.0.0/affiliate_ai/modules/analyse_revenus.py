import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt

def analyser_revenus_vs_publications(revenus_path="data/revenus.json", logs_path="data/publications.json"):
    revenus_data = json.loads(Path(revenus_path).read_text())
    if Path(logs_path).exists():
        pubs_data = json.loads(Path(logs_path).read_text())
    else:
        print("⚠️ Aucun fichier de publications trouvé. Analyse limitée aux revenus.")
        pubs_data = []

    # Regroupement des revenus par date
    journaux = defaultdict(lambda: {"revenu": 0.0, "publications": 0})
    for r in revenus_data:
        journaux[r["date"]]["revenu"] += r["revenu"]

    for p in pubs_data:
        journaux[p["date"]]["publications"] += 1

    dates = sorted(journaux)
    revenus = [journaux[d]["revenu"] for d in dates]
    pubs = [journaux[d]["publications"] for d in dates]

    # Affichage
    for d in dates:
        print(f"{d} → 📰 {journaux[d]['publications']} pubs / 💰 {journaux[d]['revenu']} €")

    # Courbe de tendance
    plt.figure()
    plt.title("Revenus vs Publications")
    plt.plot(dates, revenus, label="Revenus (€)")
    plt.plot(dates, pubs, label="Publications")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig("data/analyse_revenus.png")
    print("📈 Graphe généré : data/analyse_revenus.png")

if __name__ == "__main__":
    analyser_revenus_vs_publications()
