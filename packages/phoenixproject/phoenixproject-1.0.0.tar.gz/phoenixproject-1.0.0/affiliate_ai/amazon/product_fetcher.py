"""
🛍️ product_fetcher.py
Scrape les résultats de recherche Amazon à partir d’un mot-clé et extrait les titres, liens, et ASINs.

⚠️ Amazon bloque rapidement les requêtes automatisées.
Utiliser des headers + temporisation + proxy si besoin.

🔧 Requiert : requests, BeautifulSoup4
"""

import requests
from bs4 import BeautifulSoup
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_products(keyword, max_results=10):
    base_url = "https://www.amazon.fr/s"
    params = {"k": keyword}
    response = requests.get(base_url, params=params, headers=HEADERS)

    if response.status_code != 200:
        print(f"Erreur {response.status_code} lors de la requête Amazon.")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find_all("div", {"data-component-type": "s-search-result"})
    products = []

    for result in results[:max_results]:
        title_elem = result.h2
        link_elem = title_elem.a if title_elem else None
        asin = result.get("data-asin")
        title = title_elem.text.strip() if title_elem else "Titre non trouvé"
        url = f"https://www.amazon.fr{link_elem.get('href')}" if link_elem else "Lien non trouvé"
        products.append({"asin": asin, "title": title, "url": url})
        time.sleep(random.uniform(1.5, 3.0))  # éviter les blocages

    return products

# Exemple d’usage
if __name__ == "__main__":
    keyword = "support ordinateur"
    fetched = fetch_products(keyword)
    for p in fetched:
        print(f"- {p['title']} ({p['url']})")
