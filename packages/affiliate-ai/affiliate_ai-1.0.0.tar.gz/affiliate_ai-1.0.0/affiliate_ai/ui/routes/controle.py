from flask import Blueprint, request, redirect, render_template, flash, session
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

controle_bp = Blueprint('controle_cli', __name__)
HISTO_PATH = Path("affiliate_ai/logs/historique_cli.json")

@controle_bp.route("/controle", methods=["GET"])
def formulaire_controle():
    historique = []
    if HISTO_PATH.exists():
        historique = json.loads(HISTO_PATH.read_text())
    return render_template("controle_cli.html", historique=historique)

@controle_bp.route("/controle/cli", methods=["POST"])
def executer_action():
    action = request.form.get("action")
    date = request.form.get("date")
    statut = "succès"
    horodatage = datetime.now().strftime("%Y-%m-%d %H:%M")

    try:
        if action == "serve":
            subprocess.Popen([sys.executable, "app.py"])
        elif action == "run":
            subprocess.Popen([sys.executable, "affiliate_ai/core/publisher.py"])
        elif action == "plan" and date:
            subprocess.Popen([sys.executable, "affiliate_ai/cli.py", "--plan", date])
        else:
            statut = "échec : action inconnue"
    except Exception as e:
        statut = f"échec : {str(e)}"

    # Historique
    historique = json.loads(HISTO_PATH.read_text()) if HISTO_PATH.exists() else []
    historique.insert(0, {"action": action, "date": date or "-", "statut": statut, "timestamp": horodatage})
    HISTO_PATH.write_text(json.dumps(historique[:20], indent=2))  # on garde les 20 dernières

    return redirect("/dashboard-integrated")

from flask import send_file

@controle_bp.route("/controle/logs")
def voir_logs():
    return send_file("affiliate_ai/logs/historique_cli.json", mimetype="application/json")


@controle_bp.route("/controle/logs/reset", methods=["POST"])
def reset_logs():
    HISTO_PATH.write_text("[]")
    return redirect("/dashboard-integrated")


@controle_bp.route("/update-project", methods=["POST"])
def update_project():
    import subprocess
    subprocess.Popen(["python3", "update_phoenixproject.py"])
    return redirect("/dashboard-integrated")


@controle_bp.route("/dashboard-integrated")
def dashboard_integrated():
    from flask import render_template
    histo = []
    status_path = Path("affiliate_ai/logs/update_status.txt")
    status = status_path.read_text() if status_path.exists() else None
    if Path("affiliate_ai/logs/historique_cli.json").exists():
        histo = json.loads(Path("affiliate_ai/logs/historique_cli.json").read_text())
    return render_template("affiliate_ia_dashboard.html", historique=histo, update_status=status)
