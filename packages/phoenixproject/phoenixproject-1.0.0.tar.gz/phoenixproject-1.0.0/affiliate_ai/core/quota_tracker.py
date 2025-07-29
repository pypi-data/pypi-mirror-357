"""
quota_tracker.py – Gestion de quota pour utilisateurs IA
"""

import json
from pathlib import Path
from datetime import datetime

QUOTA_FILE = Path("affiliate_ai/config/user_quotas.json")

def init_user(user_id):
    if not QUOTA_FILE.exists():
        QUOTA_FILE.write_text("{}")

    data = json.loads(QUOTA_FILE.read_text())
    if user_id not in data:
        data[user_id] = {"used": 0, "limit": 10, "last_reset": datetime.now().isoformat()}
    QUOTA_FILE.write_text(json.dumps(data, indent=2))

def use_quota(user_id):
    data = json.loads(QUOTA_FILE.read_text())
    if data[user_id]["used"] >= data[user_id]["limit"]:
        return False
    data[user_id]["used"] += 1
    QUOTA_FILE.write_text(json.dumps(data, indent=2))
    return True

def reset_quota(user_id, new_limit=10):
    data = json.loads(QUOTA_FILE.read_text())
    data[user_id]["used"] = 0
    data[user_id]["limit"] = new_limit
    data[user_id]["last_reset"] = datetime.now().isoformat()
    QUOTA_FILE.write_text(json.dumps(data, indent=2))
