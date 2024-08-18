import requests
from app.core.config import settings

async def trigger_price_change(alert):
    url = settings.PRICE_CHANGE_API_URL


    # headers = {"Content-Type": "application/json"}
    # response = requests.post(url, json=alert.dict(), headers=headers)




    #return response.status_code == 200


    print("Triggers API Price change alert", alert)
    return 200
