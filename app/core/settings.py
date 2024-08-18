import os

class EmailSettings:
    SEND_EMAIL = os.getenv('SEND_EMAIL')
    SEND_EMAIL_PASSWORD = os.getenv('SEND_EMAIL_PASSWORD')
    RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')

EMAIL_SETTINGS = EmailSettings()
