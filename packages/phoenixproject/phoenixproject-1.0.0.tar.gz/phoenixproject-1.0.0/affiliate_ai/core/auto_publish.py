"""
auto_publish.py – Publication automatique IA 100% autonome
Étapes :
1. Lit un produit aléatoire
2. Génère un avis IA
3. Lit les règles Reddit du subreddit cible
4. Adapte le contenu
5. Poste
6. Logue l'action
"""

import json
from pathlib import Path
from publisher import publier_sur_reddit
from review_generator import generer_avis
from config_loader import charger_token
from random import choice

# Fichiers
PRODUCTS_PATH = Path("affiliate_ai/data/produits.json")
CONFIG_PATH = Path("affiliate_ai/reddit/reddit_config.json")

def charger_produit():
    produits = json.loads(PRODUCTS_PATH.read_text())
    return choice(produits)

def charger_subreddit():
    config = json.loads(CONFIG_PATH.read_text())
    return config.get("default_subreddit", "AItools")

def auto_publish():
    produit = charger_produit()
    titre = f"Avis sur : {produit['nom']}"
    contenu = generer_avis(produit)
    subreddit = charger_subreddit()
    token = charger_token()

    success = publier_sur_reddit(titre, contenu, subreddit, token)
    if success:
        print("✅ Publication Reddit réussie !")
    else:
        print("❌ Publication échouée.")

if __name__ == "__main__":
    auto_publish()
