"""
routes/docs_routes.py – Route pour afficher la documentation Reddit
"""

from flask import Blueprint, render_template_string

docs_bp = Blueprint('docs', __name__)

with open("affiliate_ai/docs/README_REDDIT_AUTOMATION.html", "r", encoding="utf-8") as f:
    html_content = f.read()

@docs_bp.route("/docs/reddit")
def afficher_doc_reddit():
    return render_template_string(html_content)
