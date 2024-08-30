from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
import json
import os
from app.core.config import settings
from app.models.price_model import PriceChangeAlert
from app.services.api_service import trigger_price_change

# Define the router
price_router = APIRouter()

# Define a model for the request body
class WebSocketConfig(BaseModel):
    secret_key: str
    api_key: str
    switch_state: bool

# Utility function to load and save the JSON configuration
def load_config():
    with open("data/matrix_config.json", "r") as f:
        return json.load(f)

def save_config(config):
    with open("data/matrix_config.json", "w") as f:
        json.dump(config, f, indent=4)

def load_price_data(symbol: str):
    file_map = {
        "BTCUSDT": "data/btcusdt_price.json",
        "ETHUSDT": "data/ethusdt_price.json"
    }
    file_path = file_map.get(symbol.upper())
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Symbol not found or file does not exist")

    with open(file_path, "r") as f:
        return json.load(f)



@price_router.post("/get_websocket_switch/")
async def get_websocket_switch(api_key: str = Body(...)):
    # Security check using BULLMATRIX_API_KEY from environment variables
    if api_key != os.getenv("BULLMATRIX_API_KEY"):
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")
    
    # Load the current configuration
    current_config = load_config()

    # Get the websocket switch state
    websocket_switch = current_config['matrix_config'][0]['config_websocket_switch']

    return {"config_websocket_switch": websocket_switch}




# API endpoint to update the websocket switch state
@price_router.post("/update_websocket_switch/")
async def update_websocket_switch(config: WebSocketConfig):
    # Verify SECRET_KEY and BULLMATRIX_API_KEY
    if config.secret_key != settings.SECRET_KEY or config.api_key != os.getenv("BULLMATRIX_API_KEY"):
        raise HTTPException(status_code=403, detail="Forbidden: Invalid credentials")

    # Load the current configuration
    current_config = load_config()
    
    # Update the websocket switch state
    current_config['matrix_config'][0]['config_websocket_switch'] = config.switch_state
    
    # Save the updated configuration back to the file
    save_config(current_config)
    
    return {"message": "WebSocket switch state updated successfully", "new_state": config.switch_state}


# Utility function to load the price data from the JSON file
def load_price_data(symbol: str):
    file_map = {
        "BTCUSDT": "data/btcusdt_price.json",
        "ETHUSDT": "data/ethusdt_price.json"
    }
    file_path = file_map.get(symbol.upper())
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Symbol not found or file does not exist")

    with open(file_path, "r") as f:
        return json.load(f)

# API endpoint to retrieve the live JSON price for a given symbol
@price_router.post("/retrieve_websocket_live_json_price/")
async def retrieve_websocket_live_json_price(symbol: str = Body(...), api_key: str = Body(...)):
    # Security check using BULLMATRIX_API_KEY from environment variables
    if api_key != os.getenv("BULLMATRIX_API_KEY"):
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")
    
    # Load price data for the given symbol
    price_data = load_price_data(symbol)
    
    # Remove the BULLMATRIX_API_KEY from the data before returning
    if "BULLMATRIX_API_KEY" in price_data:
        del price_data["BULLMATRIX_API_KEY"]

    return price_data


@price_router.post("/price_change_alert/")
async def price_change_alert(alert: PriceChangeAlert):
    # Verify SECRET_KEY and BULLMATRIX_API_KEY
    if alert.BULLMATRIX_API_KEY != os.getenv("BULLMATRIX_API_KEY"):
        raise HTTPException(status_code=403, detail="Forbidden: Invalid credentials")
    
    success = await trigger_price_change(alert)
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=500, detail="Failed to trigger API")
