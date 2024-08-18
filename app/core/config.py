import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PRICE_CHANGE_API_URL = "http://bullmatrixapi2024-env.eba-gpycmjis.ap-northeast-1.elasticbeanstalk.com/pricechange/price_change_alert/"
    SECRET_KEY = os.getenv("SECRET_KEY")

settings = Settings()
