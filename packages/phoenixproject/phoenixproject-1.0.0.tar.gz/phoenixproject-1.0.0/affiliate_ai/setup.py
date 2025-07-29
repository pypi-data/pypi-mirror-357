"""
setup.py – Initialisation de l'environnement IA-Affiliée
"""

import os
import json
import getpass
from pathlib import Path
from cryptography.fernet import Fernet

# Générer une clé de cryptage unique (sauvegardée localement)
KEY_PATH = Path("config/crypto.key")
CONFIG_PATH = Path("config/secure_reddit.json")

def generate_key():
    KEY_PATH.parent.mkdir(exist_ok=True, parents=True)
    key = Fernet.generate_key()
    KEY_PATH.write_bytes(key)
    return key

def encrypt_config(client_id, client_secret, username, password):
    key = KEY_PATH.read_bytes()
    cipher = Fernet(key)
    creds = {
        "client_id": client_id,
        "client_secret": client_secret,
        "username": username,
        "password": password
    }
    enc = cipher.encrypt(json.dumps(creds).encode())
    CONFIG_PATH.write_bytes(enc)
    print("🔐 Identifiants cryptés et sauvegardés dans config/secure_reddit.json")

def install_reqs():
    os.system("pip install praw cryptography beautifulsoup4 matplotlib")

def main():
    print("🚀 Setup IA-Affiliée – Initialisation")
    install_reqs()

    if not KEY_PATH.exists():
        generate_key()
        print("🗝️  Clé de chiffrement générée.")

    print("👉 Configuration Reddit")
    client_id = input("client_id : ")
    client_secret = input("client_secret : ")
    username = input("Reddit username : ")
    password = getpass.getpass("Reddit password : ")
    encrypt_config(client_id, client_secret, username, password)


    print("👉 Configuration Email pour alertes")
    email = input("Adresse email d’envoi : ")
    email_pw = getpass.getpass("Mot de passe email (ou mot de passe app Gmail) : ")

    mail_creds = {
        "email": email,
        "password": email_pw
    }
    encrypted_mail = cipher.encrypt(json.dumps(mail_creds).encode())
    Path("config/secure_mail.json").write_bytes(encrypted_mail)
    print("📧 Email chiffré et stocké dans config/secure_mail.json")

if __name__ == "__main__":
    main()