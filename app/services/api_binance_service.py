# app/services/api_binance_service.py

from binance.client import Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class BinanceService:
    def __init__(self):
        # Initialize the Binance client with API keys from settings
        self.client = Client(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET)

    def get_current_price(self, symbol):
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
            return None
