from fastapi import FastAPI, Request, HTTPException
from app.api.v1.price import price_router
from app.core.config import settings
import asyncio
from fastapi.templating import Jinja2Templates
from app.api.v1.price import load_price_data, load_config
import json
from pathlib import Path

app = FastAPI()

# Setup templates directory
templates = Jinja2Templates(directory="templates")

# Include API routers
app.include_router(price_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    #from app.services.websocket_service import start_websocket
    # Run the WebSocket service concurrently with FastAPI
    print("Just Started")
    #asyncio.create_task(start_websocket())
    

@app.get("/")
def read_root():
    return {"message": "Welcome to Bullmatrix WebSocket"}

@app.get("/price")
async def read_root(request: Request):
    btc_price = load_price_data("BTCUSDT")
    eth_price = load_price_data("ETHUSDT")
    current_config = load_config()  # Load the config to get the websocket switch state
    websocket_switch = current_config['matrix_config'][0]['config_websocket_switch']
    return templates.TemplateResponse("index.html", {
        "request": request,
        "btc_price": btc_price,
        "eth_price": eth_price,
        "websocket_switch": websocket_switch
    })


@app.get("/price_btcusdt")
async def get_matrix_price_btcusdt():
    return serve_json_file("btcusdt_price.json")

@app.get("/price_ethusdt")
async def get_matrix_price_ethusdt():
    return serve_json_file("ethusdt_price.json")

@app.get("/config")
async def get_matrix_price_ethusdt():
    return serve_json_file("matrix_config.json")


# Helper function to serve JSON files
def serve_json_file(filename: str):
    file_path = Path(f"data/{filename}")
    if file_path.exists():
        with open(file_path, "r") as file:
            return json.load(file)
    else:
        raise HTTPException(status_code=404, detail=f"{filename} file not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=80,
        reload=True,
        workers=1,
        debug=True,
    )
