import json
from pathlib import Path
from affiliate_ai.modules.amazon import post_amazon_review
from affiliate_ai.modules.reddit import post_reddit_comment
from affiliate_ai.gestion_secrets import verifier_secrets

def execute_from_json(path="affiliate_ai/hooks/task.json"):
    verifier_secrets()
    file = Path(path)
    if not file.exists():
        print(f"❌ Fichier {path} introuvable.")
        return

    task = json.loads(file.read_text())
    action = task.get("action")
    params = task.get("params", {})

    if action == "post_amazon_review":
        post_amazon_review(**params)
    elif action == "post_reddit_comment":
        post_reddit_comment(**params)
    else:
        print(f"❓ Action inconnue : {action}")

if __name__ == "__main__":
    execute_from_json()
