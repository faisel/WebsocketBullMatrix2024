from pydantic import BaseModel
from datetime import datetime

class PriceChangeAlert(BaseModel):
    BULLMATRIX_API_KEY: str
    apptime: str
    servertime: str
    timestamp: int
    symbol: str
    price: str
    price_big_p: str
    price_i: str
    price_diff: str
    is_big_diff: bool
