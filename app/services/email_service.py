import smtplib
from email.mime.text import MIMEText
from app.core.settings import EMAIL_SETTINGS

def send_email_notification(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SETTINGS.SEND_EMAIL
    msg['To'] = EMAIL_SETTINGS.RECEIVER_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_SETTINGS.SEND_EMAIL, EMAIL_SETTINGS.SEND_EMAIL_PASSWORD)
        server.sendmail(EMAIL_SETTINGS.SEND_EMAIL, EMAIL_SETTINGS.RECEIVER_EMAIL, msg.as_string())
