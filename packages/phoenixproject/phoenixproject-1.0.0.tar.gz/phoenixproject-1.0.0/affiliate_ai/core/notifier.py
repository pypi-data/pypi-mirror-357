"""
notifier.py – Envoi d'un email après chaque post Reddit réussi
"""

import smtplib
from email.message import EmailMessage
from datetime import datetime

def notifier_email(titre, url, destinataire="tonadresse@mail.com"):
    msg = EmailMessage()
    msg['Subject'] = f"[PhoenixProject] Nouveau post Reddit publié"
    msg['From'] = "notifier@phoenix.ai"
    msg['To'] = destinataire

    corps = f"""Bonjour 👋,

Un nouveau post Reddit vient d’être publié avec succès :

📝 Titre : {titre}
🔗 Lien : {url}
📅 Date : {datetime.now().strftime('%Y-%m-%d %H:%M')}

– PhoenixProject
"""
    msg.set_content(corps)

    try:
        with smtplib.SMTP('localhost') as smtp:
            smtp.send_message(msg)
        print("📧 Notification envoyée")
    except Exception as e:
        print("❌ Erreur envoi mail :", e)
