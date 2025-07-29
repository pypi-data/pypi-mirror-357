"""
⏰ scheduler.py
Automatise l’exécution quotidienne ou hebdomadaire du pipeline affilié :
- Recherche produits Amazon
- Génération d’avis IA
- Construction du lien affilié
- Publication automatique

Peut être utilisé avec cron ou un service de planification local.
"""

import time
from datetime import datetime
from product_fetcher import fetch_products
from review_generator import generate_review
from link_builder import build_affiliate_link
from publisher import publish_to_medium, publish_to_reddit
from log_manager import log_event

# CONFIGURATION
AFFILIATE_TAG = "tonid-21"
KEYWORDS = ["support ordinateur portable", "gadget IA", "organisation bureau"]
PLATFORM_TARGETS = ["medium", "reddit"]
MAX_PRODUCTS = 3

def publish_bundle(product):
    """Génère un avis et publie automatiquement"""
    title = product["title"]
    base_link = product["link"]
    review = generate_review(title)
    affiliate_link = build_affiliate_link(base_link, AFFILIATE_TAG)

    full_content = f"🛒 [Voir le produit]({affiliate_link})

📝 {review}"

    if "medium" in PLATFORM_TARGETS:
        try:
            status, resp = publish_to_medium(title, full_content)
            print(f"[{datetime.now()}] ✅ Medium publié : {status}")
        except Exception as e:
            log_event("medium", title, "ERROR", str(e))

    if "reddit" in PLATFORM_TARGETS:
        try:
            url = publish_to_reddit(title, full_content)
            print(f"[{datetime.now()}] ✅ Reddit publié : {url}")
        except Exception as e:
            log_event("reddit", title, "ERROR", str(e))

def run_scheduler():
    """Exécution principale"""
    print(f"🟢 Lancement de la session du {datetime.now().date()}...
")
    for kw in KEYWORDS:
        print(f"🔍 Recherche de produits pour : {kw}")
        try:
            products = fetch_products(kw, max_results=MAX_PRODUCTS)
            for p in products:
                publish_bundle(p)
                time.sleep(10)  # pause pour éviter les surcharges
        except Exception as err:
            print(f"❌ Erreur pour '{kw}' :", err)

if __name__ == "__main__":
    run_scheduler()
