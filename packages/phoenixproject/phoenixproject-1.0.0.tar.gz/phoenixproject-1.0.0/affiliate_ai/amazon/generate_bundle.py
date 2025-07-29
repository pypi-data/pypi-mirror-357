"""
📦 generate_bundle.py
Combine la récupération de produits Amazon avec la génération automatique d'avis pour chaque produit.
"""

from product_fetcher import fetch_products
from review_generator import generate_review
import time

def generate_product_bundles(keyword, max_results=5):
    products = fetch_products(keyword, max_results=max_results)
    bundles = []

    for product in products:
        title = product['title']
        link = product['link']
        review = generate_review(title)
        bundle = {
            "title": title,
            "link": link,
            "review": review
        }
        bundles.append(bundle)

    return bundles

# Exemple d’utilisation
if __name__ == "__main__":
    keyword = "support ordinateur portable"
    bundles = generate_product_bundles(keyword)

    for idx, b in enumerate(bundles, start=1):
        print(f"
🛒 Produit {idx}")
        print(f"🔗 Titre : {b['title']}")
        print(f"📎 Lien : {b['link']}")
        print(f"📝 Avis généré :
{b['review']}")
        time.sleep(1)
