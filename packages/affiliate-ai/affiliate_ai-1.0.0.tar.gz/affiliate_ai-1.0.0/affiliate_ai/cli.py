"""
affiliate_ai/cli.py – Interface en ligne de commande du projet
"""

import argparse
import subprocess
from pathlib import Path
import sys
import json
from datetime import datetime

def lancer_serveur():
    print("🚀 Démarrage du serveur Flask sur http://localhost:5000")
    subprocess.run([sys.executable, "app.py"])

def ajouter_planification(date_str):
    path = Path("affiliate_ai/db/planifications.json")
    plans = json.loads(path.read_text()) if path.exists() else []
    plans.append({"date": date_str, "status": "à venir"})
    path.write_text(json.dumps(plans, indent=2))
    print(f"📆 Planification ajoutée pour le {date_str}")

def publication_immediate():
    print("📤 Lancement de la publication immédiate…")
    subprocess.run([sys.executable, "affiliate_ai/core/publisher.py"])

def main():
    parser = argparse.ArgumentParser(description="PhoenixProject CLI")
    parser.add_argument('--serve', action='store_true', help="Lancer le serveur Flask")
    parser.add_argument('--plan', type=str, help="Planifier une publication (format YYYY-MM-DD)")
    parser.add_argument('--run', action='store_true', help="Lancer une publication immédiate")

    args = parser.parse_args()

    if args.serve:
        lancer_serveur()
    elif args.plan:
        try:
            datetime.strptime(args.plan, "%Y-%m-%d")
            ajouter_planification(args.plan)
        except ValueError:
            print("❌ Format de date invalide. Utiliser YYYY-MM-DD.")
    elif args.run:
        publication_immediate()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
