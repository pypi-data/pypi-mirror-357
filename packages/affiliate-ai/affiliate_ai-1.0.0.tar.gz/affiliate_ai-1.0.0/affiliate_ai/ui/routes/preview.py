"""
routes/preview.py – Affiche le prochain post IA avant publication
"""

from flask import Blueprint, render_template_string
from review_generator import generer_avis_depuis_produit
import json
from pathlib import Path

preview_bp = Blueprint('preview', __name__)

@preview_bp.route("/preview/produit")
def preview_produit():
    produits_path = Path("affiliate_ai/db/produits.json")
    produits = json.loads(produits_path.read_text())
    if not produits:
        return "Aucun produit disponible."

    produit = produits[0]  # Prend le prochain produit
    avis = generer_avis_depuis_produit(produit)

    html = f"""
    <h2>🔮 Prochain Produit : {produit['titre']}</h2>
    <p><strong>🔗 Lien :</strong> <a href="{produit['url']}" target="_blank">{produit['url']}</a></p>
    <h3>📝 Avis IA généré :</h3>
    <div style='white-space: pre-wrap; background: #eee; padding: 1em;'>{avis}</div>
    """
    return render_template_string(html)
