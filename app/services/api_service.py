import requests
import httpx
from app.core.config import settings

async def trigger_price_change(alert):
    url = settings.PRICE_CHANGE_API_URL


    # headers = {"Content-Type": "application/json"}
    # response = requests.post(url, json=alert.dict(), headers=headers)




    #return response.status_code == 200


    print("Triggers API Price change alert", alert)
    return 200


# async def trigger_price_change(alert):
#     url = settings.PRICE_CHANGE_API_URL
#     headers = {"Content-Type": "application/json"}

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(url, json=alert, headers=headers)

#         # Check if the request was successful
#         if response.status_code == 200:
#             print("Successfully triggered API price change alert:", alert)
#             return True
#         else:
#             print(f"Failed to trigger API price change. Status code: {response.status_code}, Response: {response.text}")
#             return False

#     except httpx.RequestError as e:
#         # Handle any errors that occurred during the request
#         print(f"An error occurred while requesting {url}: {e}")
#         return False