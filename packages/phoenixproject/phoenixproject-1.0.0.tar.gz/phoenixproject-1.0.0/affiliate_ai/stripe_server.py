"""
stripe_server.py – Serveur Flask pour gérer la facturation à l’usage avec Stripe
"""

import os
import stripe
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration Stripe (à chiffrer dans le futur)
STRIPE_SECRET_KEY = "sk_test_..."  # à remplacer par ta clé réelle
stripe.api_key = STRIPE_SECRET_KEY

PRICE_PER_ACTION = 100  # en centimes (1.00 € par action IA)

@app.route("/invoice", methods=["POST"])
def create_invoice_item():
    data = request.json
    customer_id = data.get("customer_id")
    description = data.get("description", "Action IA facturée")

    if not customer_id:
        return jsonify({"error": "customer_id requis"}), 400

    try:
        invoice_item = stripe.InvoiceItem.create(
            customer=customer_id,
            amount=PRICE_PER_ACTION,
            currency="eur",
            description=description
        )
        return jsonify({"success": True, "item_id": invoice_item.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5005)
