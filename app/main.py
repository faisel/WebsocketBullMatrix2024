from fastapi import FastAPI
from app.api.v1.price import price_router
from app.core.config import settings
import asyncio

app = FastAPI()

# Include API routers
app.include_router(price_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    from app.services.websocket_service import start_websocket
    # Run the WebSocket service concurrently with FastAPI
    asyncio.create_task(start_websocket())

@app.get("/")
def read_root():
    return {"message": "Welcome to Bullmatrix Websocket"}

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
