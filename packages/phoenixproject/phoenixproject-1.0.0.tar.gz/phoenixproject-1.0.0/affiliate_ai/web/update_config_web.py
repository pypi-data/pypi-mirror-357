from flask import Flask, request, render_template, redirect
import json
from pathlib import Path

app = Flask(__name__)
CONFIG_PATH = Path("affiliate_ai/config/global.json")

@app.route("/update-config", methods=["GET", "POST"])
def update_config():
    if request.method == "POST":
        data = {
            "user_id": request.form["user_id"],
            "keywords": [k.strip() for k in request.form["keywords"].split(",")],
            "platforms": [p.strip() for p in request.form["platforms"].split(",")],
            "preferred_language": request.form["preferred_language"],
            "stripe_invoice_url": request.form["stripe_invoice_url"]
        }
        CONFIG_PATH.write_text(json.dumps(data, indent=2))
        return redirect("/update-config")

    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text())
    else:
        config = {}
    return render_template("config_form.html", config=config)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
