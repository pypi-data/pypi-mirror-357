"""
server_config.py – Configuration centralisée du serveur Flask
Permet de changer dynamiquement le port, le host, et les modules actifs
"""

import os

def get_server_config():
    return {
        "host": os.environ.get("FLASK_HOST", "0.0.0.0"),
        "port": int(os.environ.get("FLASK_PORT", 5000)),
        "debug": os.environ.get("FLASK_DEBUG", "false").lower() == "true",
        "auto_ia_enabled": os.environ.get("AUTO_IA", "true").lower() == "true"
    }
