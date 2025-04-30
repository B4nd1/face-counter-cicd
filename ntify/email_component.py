import os
import smtplib
from email.mime.text import MIMEText

# SMTP settings
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")

def send_test_email():
    print("TODO")

def send_email(to_email: str, subject: str, body: str):
    print(f"Send email to {to_email}")
    print(f"{subject}, {body}")
    # msg = MIMEText(body)
    # msg["Subject"] = subject
    # msg["From"] = EMAIL_FROM
    # msg["To"] = to_email
    # with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
    #     server.starttls()
    #     server.login(SMTP_USER, SMTP_PASSWORD)
    #     server.send_message(msg)