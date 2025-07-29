#!/bin/bash
# revenus_auto.sh – Exécution automatique du bilan des revenus IA

SCRIPT_PATH="$(dirname "$(realpath "$0")")/affiliate_ai/core/revenus.py"

echo "📊 Génération automatique du rapport de revenus IA ($(date))"
python3 "$SCRIPT_PATH"
