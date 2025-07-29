"""
runner.py – Orchestration complète de la boucle IA-affiliée
"""

from affiliate_ai.core import quota_tracker
from affiliate_ai.amazon import product_fetcher, review_generator, link_builder
from affiliate_ai.core import publisher, log_manager
from affiliate_ai.config.decryptor import load_credentials
import json
from pathlib import Path

# Load configuration
CONFIG = json.loads(Path("affiliate_ai/config/global.json").read_text())
KEYWORDS = CONFIG.get("default_keywords", [])
TAG = CONFIG.get("affiliate_tag", "")
PLATFORMS = CONFIG.get("default_platforms", [])

def run_cycle():
    user_id = CONFIG.get("user_id", "default")
    quota_tracker.init_user(user_id)
    reddit_creds = load_credentials()
    for keyword in KEYWORDS:
        print(f"🔍 Recherche de produits pour : {keyword}")
        products = product_fetcher.fetch_products(keyword)
        for product in products[:1]:  # 1er produit par mot-clé
            title = product.get("title", "Produit")
            url = product.get("url", "")
            print(f"📝 Génération d’un avis pour : {title}")
            review = review_generator.generate_review(title)
            affiliate_url = link_builder.build_affiliate_link(url, TAG)
            full_content = f"{review}

👉 Voici le lien : {affiliate_url}

Et vous, vous utilisez quoi ?"
            if not quota_tracker.use_quota(user_id):
                print("🚫 Quota IA atteint pour cet utilisateur.")
                continue
            for platform in PLATFORMS:
                try:
                    print(f"📤 Publication sur {platform}")
                    publisher.publish(platform, title, full_content, creds=reddit_creds)
                    log_manager.log_event(platform, title, status="OK")
                except Exception as e:
                    print(f"❌ Erreur de publication sur {platform} : {e}")
                    log_manager.log_event(platform, title, status=f"ERREUR: {e}")

if __name__ == "__main__":
    run_cycle()