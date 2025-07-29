"""
daily_backup.py – Sauvegarde quotidienne des logs Reddit
"""

from pathlib import Path
from datetime import datetime
import shutil

def backup_logs():
    src = Path("affiliate_ai/logs/reddit_publications.json")
    if not src.exists():
        print("Aucun log à sauvegarder.")
        return

    backup_dir = Path("affiliate_ai/backups/")
    backup_dir.mkdir(exist_ok=True, parents=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    dst = backup_dir / f"reddit_logs_backup_{stamp}.json"
    shutil.copy(src, dst)
    print(f"💾 Backup effectué : {dst}")

if __name__ == "__main__":
    backup_logs()
