"""
routes/stats.py – Statistiques d’activité IA
"""

from flask import Blueprint, render_template_string
import json
from pathlib import Path

stats_bp = Blueprint('stats', __name__)

@stats_bp.route("/stats")
def afficher_stats():
    logs_path = Path("affiliate_ai/logs/reddit_publications.json")
    logs = json.loads(logs_path.read_text()) if logs_path.exists() else []
    nb_posts = len(logs)
    estim_gain = round(nb_posts * 0.15, 2)

    html = f"""
    <h2>📊 Statistiques de publication</h2>
    <p>Nombre total de publications : <strong>{nb_posts}</strong></p>
    <p>Revenu estimé (0,15€/post) : <strong>{estim_gain} €</strong></p>
    <p>Dernier post : {logs[-1]['title'] if logs else 'Aucun'}</p>
    <p>Dernier lien : <a href="{logs[-1]['url']}" target="_blank">{logs[-1]['url']}</a></p>
    """
    return render_template_string(html)
