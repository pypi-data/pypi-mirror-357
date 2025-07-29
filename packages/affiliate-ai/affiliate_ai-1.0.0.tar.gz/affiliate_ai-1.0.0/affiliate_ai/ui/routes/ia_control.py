"""
routes/ia_control.py – Route de contrôle IA automatique (pause/reprise)
"""

from flask import Blueprint, redirect
import os

ia_bp = Blueprint('ia', __name__)
FLAG_PATH = "affiliate_ai/state/ia_status.flag"

@ia_bp.route("/toggle/ia", methods=["POST"])
def toggle_ia():
    if not os.path.exists(FLAG_PATH):
        Path(FLAG_PATH).write_text("off")
        return redirect("/dashboard")

    current = Path(FLAG_PATH).read_text().strip()
    new_state = "on" if current == "off" else "off"
    Path(FLAG_PATH).write_text(new_state)
    return redirect("/dashboard")

def is_ia_active():
    if not os.path.exists(FLAG_PATH):
        return True
    return Path(FLAG_PATH).read_text().strip() == "on"
