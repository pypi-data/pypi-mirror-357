"""
quota_dashboard.py – CLI simple pour consulter les quotas IA par utilisateur
"""

import json
from pathlib import Path

QUOTA_FILE = Path("affiliate_ai/config/user_quotas.json")

def afficher_quotas():
    if not QUOTA_FILE.exists():
        print("Aucune donnée de quota.")
        return

    data = json.loads(QUOTA_FILE.read_text())
    print("📊 Quotas Utilisateurs IA :")
    for user, info in data.items():
        print(f"👤 {user} : {info['used']} / {info['limit']} (depuis {info['last_reset']})")

if __name__ == "__main__":
    afficher_quotas()
