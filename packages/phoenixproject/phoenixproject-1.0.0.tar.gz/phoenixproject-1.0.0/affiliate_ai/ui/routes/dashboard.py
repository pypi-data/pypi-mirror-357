"""
routes/dashboard.py – Tableau de bord enrichi avec stats et contrôle IA
"""

from flask import Blueprint, render_template_string
import json
from pathlib import Path

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
def tableau_de_bord():
    # Chargement estimation revenus
    logs_path = Path("affiliate_ai/logs/reddit_publications.json")
    revenu_estime = 0.0
    if logs_path.exists():
        try:
            logs = json.loads(logs_path.read_text())
            revenu_estime = round(len(logs) * 0.15, 2)  # Estimation à 0.15€/clic
        except:
            pass

    html = f"""
    <!DOCTYPE html>
    <html lang='fr'>
    <head>
        <meta charset='UTF-8'>
        <title>📊 Tableau de Bord – PhoenixProject</title>
        <style>
            body {{ font-family: sans-serif; background-color: #f9f9f9; margin: 40px; }}
            h1 {{ color: #c0392b; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ margin: 1em 0; }}
            a {{ text-decoration: none; font-size: 1.2em; color: #2980b9; }}
            a:hover {{ text-decoration: underline; }}
            .bloc {{ background: #fff; padding: 1em; margin-top: 2em; border-radius: 6px; box-shadow: 0 0 6px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body>
        <h1>🔥 PhoenixProject – Tableau de bord IA</h1>
        <ul>
            <li>📖 <a href="/docs/reddit" target="_blank">Documentation Reddit Automation</a></li>
            <li>📜 <a href="/reddit-logs" target="_blank">Historique des publications Reddit</a></li>
            <li>🚀 <a href="/run/reddit/publish">Lancer une publication IA maintenant</a></li>
            <li>⏱️ <a href="/run/reddit/scheduler">Démarrer le scheduler automatique</a></li>
        </ul>

        <div class="bloc">
            <h2>💸 Revenus estimés</h2>
            <p>Nombre de publications : {len(logs) if logs_path.exists() else 0}</p>
            <p>💰 Estimation actuelle : <strong>{revenu_estime} €</strong></p>
        </div>

        <div class="bloc">
            <h2>🔮 Prochain produit</h2>
            <p>Chargé depuis <code>produits.json</code></p>
            <p><a href="/preview/produit" target="_blank">🔍 Voir le prochain produit</a></p>
        </div>

        <div class="bloc">
            <h2>⛔ Contrôle IA</h2>
            <form method="post" action="/toggle/ia">
                <button type="submit">⏸️ Pause / Reprise IA automatique</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)
