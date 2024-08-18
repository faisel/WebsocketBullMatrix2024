from fastapi import APIRouter, HTTPException
from app.models.price_model import PriceChangeAlert
from app.services.api_service import trigger_price_change

price_router = APIRouter()

@price_router.post("/price_change_alert/")
async def price_change_alert(alert: PriceChangeAlert):
    success = await trigger_price_change(alert)
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=500, detail="Failed to trigger API")
