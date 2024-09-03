import requests
import httpx
import json
from app.core.config import settings


async def trigger_price_change(alert):

    #print("alert", alert)
    # Load the current configuration to check the websocket switch
    with open("data/matrix_config.json", "r") as f:
        current_config = json.load(f)

    websocket_switch = current_config['matrix_config'][0]['config_websocket_switch']

    # Check if the websocket switch is OFF
    # if not websocket_switch:
    #     print("config_websocket_switch is OFF, not triggering the price change alert.", alert)
    #     return  # Simply exit the function without doing anything

    # If the switch is ON, proceed with the API request
    url = settings.PRICE_CHANGE_API_URL
    headers = {"Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=alert, headers=headers)

        # Check if the request was successful
        # if response.status_code == 200:
        #     print("config_websocket_switch is ON, Successfully triggered API price change alert:", alert)
        # else:
        #     print(f"Failed to trigger API price change. Status code: {response.status_code}, Response: {response.text}")

    except httpx.RequestError as e:
        # Handle any errors that occurred during the request
        #print(f"An error occurred while requesting {url}: {e}")
        pass