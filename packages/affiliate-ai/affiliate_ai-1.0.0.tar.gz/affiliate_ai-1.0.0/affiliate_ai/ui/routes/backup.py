"""
routes/backup.py – Gestion des sauvegardes des logs Reddit via interface web
"""

from flask import Blueprint, render_template_string, redirect
from datetime import datetime
from pathlib import Path
import shutil

backup_bp = Blueprint('backup', __name__)

@backup_bp.route("/backup/run")
def lancer_backup():
    logs_path = Path("affiliate_ai/logs/reddit_publications.json")
    if not logs_path.exists():
        return "❌ Aucun log à sauvegarder."

    backup_dir = Path("affiliate_ai/backups/")
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    dst = backup_dir / f"reddit_logs_backup_{stamp}.json"
    shutil.copy(logs_path, dst)

    return redirect("/backup/list")

@backup_bp.route("/backup/list")
def afficher_backups():
    backup_dir = Path("affiliate_ai/backups/")
    fichiers = sorted(backup_dir.glob("*.json"), reverse=True)
    if not fichiers:
        return "Aucune sauvegarde disponible."

    html = "<h2>💾 Sauvegardes disponibles :</h2><ul>"
    for f in fichiers:
        html += f"<li><a href='/download/{f.name}'>{f.name}</a></li>"
    html += "</ul><p><a href='/dashboard'>⬅️ Retour tableau de bord</a></p>"
    return render_template_string(html)
