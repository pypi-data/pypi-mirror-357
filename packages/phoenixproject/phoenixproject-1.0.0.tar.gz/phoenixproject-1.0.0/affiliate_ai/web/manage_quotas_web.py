from flask import Flask, request, render_template, redirect
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
QUOTA_PATH = Path("affiliate_ai/config/user_quotas.json")

@app.route("/quotas", methods=["GET"])
def show_quotas():
    if not QUOTA_PATH.exists():
        return "Aucun quota enregistré."
    quotas = json.loads(QUOTA_PATH.read_text())
    return render_template("quotas.html", quotas=quotas)

@app.route("/reset-quota", methods=["POST"])
def reset_quota():
    user = request.form["user"]
    new_limit = int(request.form["new_limit"])
    quotas = json.loads(QUOTA_PATH.read_text())
    if user in quotas:
        quotas[user]["used"] = 0
        quotas[user]["limit"] = new_limit
        quotas[user]["last_reset"] = datetime.now().isoformat()
        QUOTA_PATH.write_text(json.dumps(quotas, indent=2))
    return redirect("/quotas")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
