"""
routes/planification.py – Gère la planification d'une publication à une date donnée
"""

from flask import Blueprint, request, redirect, render_template_string
from pathlib import Path
import json
from datetime import datetime

planif_bp = Blueprint('planification', __name__)
PLAN_FILE = Path("affiliate_ai/db/planifications.json")

@planif_bp.route("/planifier", methods=["POST"])
def planifier():
    date_str = request.form.get("date")
    if not date_str:
        return "Date manquante.", 400

    plan = json.loads(PLAN_FILE.read_text()) if PLAN_FILE.exists() else []
    plan.append({"date": date_str, "status": "à venir"})
    PLAN_FILE.write_text(json.dumps(plan, indent=2))
    return redirect("/dashboard-integrated")

@planif_bp.route("/planifier/liste")
def voir_planifications():
    plan = json.loads(PLAN_FILE.read_text()) if PLAN_FILE.exists() else []
    html = "<h2>📆 Planifications enregistrées :</h2><ul>"
    for p in plan:
        html += f"<li>{p['date']} — {p['status']}</li>"
    html += "</ul><p><a href='/dashboard-integrated'>⬅️ Retour tableau de bord</a></p>"
    return render_template_string(html)
