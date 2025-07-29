"""
alert_manager.py – Notifications email avec config chiffrée
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from affiliate_ai.config.decryptor import load_email_config

creds = load_email_config()
EMAIL_ADDRESS = creds["email"]
EMAIL_PASSWORD = creds["password"]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(subject, body, to_email=EMAIL_ADDRESS):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"📨 Notification envoyée : {subject}")
    except Exception as e:
        print(f"❌ Erreur d’envoi de mail : {e}")
