"""
🔗 link_builder.py
Ajoute un tag affilié Amazon à une URL produit propre.
"""

from urllib.parse import urlparse, urlunparse

def build_affiliate_link(url, affiliate_tag):
    """
    Ajoute le paramètre ?tag= à une URL produit Amazon propre
    """
    parsed_url = urlparse(url)
    base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    return f"{base_url}?tag={affiliate_tag}"

# Exemple d’utilisation
if __name__ == "__main__":
    url = "https://www.amazon.fr/dp/B08KH53NKR"
    tag = "tonid-21"
    print(build_affiliate_link(url, tag))
