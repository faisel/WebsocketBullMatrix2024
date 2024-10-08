import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PRICE_CHANGE_API_URL = "http://bullmatrixapi2024fastapi-env.ap-northeast-1.elasticbeanstalk.com/pricechange/price_change_alert/"
    #PRICE_CHANGE_API_URL = "http://127.0.0.1:8000/pricechange/price_change_alert/"
    SECRET_KEY = os.getenv("SECRET_KEY")
    BULLMATRIX_API_KEY = os.getenv("BULLMATRIX_API_KEY")
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

settings = Settings()
