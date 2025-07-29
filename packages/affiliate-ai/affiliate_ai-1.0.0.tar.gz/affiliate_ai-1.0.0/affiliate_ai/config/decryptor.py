"""
decryptor.py – Déchiffre les identifiants Reddit pour les modules internes
"""

import json
from cryptography.fernet import Fernet
from pathlib import Path

KEY_PATH = Path("config/crypto.key")
CONFIG_PATH = Path("config/secure_reddit.json")

def load_credentials():
    if not KEY_PATH.exists() or not CONFIG_PATH.exists():
        raise FileNotFoundError("🔐 Clé de chiffrement ou config chiffrée manquante")

    key = KEY_PATH.read_bytes()
    cipher = Fernet(key)

    encrypted_data = CONFIG_PATH.read_bytes()
    decrypted_data = cipher.decrypt(encrypted_data).decode()

    creds = json.loads(decrypted_data)
    return creds

# Exemple d'utilisation
if __name__ == "__main__":
    creds = load_credentials()
    print("✅ Identifiants déchiffrés :")
    print(json.dumps(creds, indent=2))



def load_email_config():
    key = KEY_PATH.read_bytes()
    cipher = Fernet(key)
    encrypted = Path("config/secure_mail.json").read_bytes()
    decrypted = cipher.decrypt(encrypted).decode()
    return json.loads(decrypted)
