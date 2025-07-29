"""
config_editor_cli.py – Modifier global.json en terminal
"""

import json
from pathlib import Path

CONFIG_PATH = Path("affiliate_ai/config/global.json")

def charger_config():
    if not CONFIG_PATH.exists():
        print("❌ Fichier global.json introuvable.")
        return {}
    return json.loads(CONFIG_PATH.read_text())

def sauvegarder_config(config):
    CONFIG_PATH.write_text(json.dumps(config, indent=2))
    print("✅ Configuration mise à jour.")

def modifier_config():
    config = charger_config()
    if not config:
        return

    while True:
        print("\n🛠️ Configuration actuelle :")
        for key, value in config.items():
            print(f"- {key} : {value}")

        choix = input("\n📝 Clé à modifier (ou 'exit' pour quitter) : ").strip()
        if choix.lower() == "exit":
            break
        if choix not in config:
            print("⛔ Clé invalide.")
            continue

        new_val = input(f"🆕 Nouvelle valeur pour {choix} : ").strip()
        try:
            if config[choix] and isinstance(config[choix], list):
                config[choix] = [x.strip() for x in new_val.split(",")]
            elif config[choix] and isinstance(config[choix], int):
                config[choix] = int(new_val)
            else:
                config[choix] = new_val
        except Exception as e:
            print(f"❌ Erreur de mise à jour : {e}")
        else:
            sauvegarder_config(config)

if __name__ == "__main__":
    modifier_config()
