from fastapi import FastAPI, Request, HTTPException
from app.api.v1.price import price_router
from app.core.config import settings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import asyncio
from fastapi.templating import Jinja2Templates
from app.api.v1.price import load_price_data, load_config
import json
from pathlib import Path
import os

app = FastAPI()

# Setup templates directory
templates = Jinja2Templates(directory="templates")

# Include API routers
app.include_router(price_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    from app.services.websocket_service import start_websocket
    # Run the WebSocket service concurrently with FastAPI
    #print("Just Started")
    asyncio.create_task(start_websocket())
    

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Bullmatrix WebSocket",
        "/price": "get the live price",
        "/logs": "get the logs",
        "/logs-empty": "empty logs, app.log",
        "/data": "get files from /data/ - data/btcusdt_price.json or data/ethusdt_price.json or data/matrix_config.json"
        }

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

LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "log", "app.log")
@app.get("/logs")
def stream_logs():
    """
    Stream logs from the app.log file.
    """

    def log_streamer():
        with open(LOG_FILE_PATH, "r") as log_file:
            while True:
                line = log_file.readline()
                if not line:
                    break
                yield line

    return StreamingResponse(log_streamer(), media_type="text/plain")


@app.get("/logs-empty")
def logs_empty():
    try:
        # Open the log file in write mode to clear its contents
        with open(LOG_FILE_PATH, 'w') as file:
            file.write("")  # Writing an empty string will clear the file

        return {"message": "Log file emptied successfully."}
    except Exception as e:
        return {"error": f"Failed to empty the log file: {str(e)}"}


# Serve static files (e.g., JSON files)
app.mount("/data", StaticFiles(directory="data"), name="data")



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
