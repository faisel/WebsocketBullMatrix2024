# app/services/websocket_service.py
import asyncio
from unicorn_binance_websocket_api import BinanceWebSocketApiManager
import os
from app.utils.compare_price import compare_and_update_price  # Import your price comparison function

# Create an UBWA (Unicorn Binance WebSocket API) instance
ubwa = BinanceWebSocketApiManager(exchange="binance.com-futures")

# Define the markets and channels
markets = ['btcusdt', 'ethusdt']
channels = ['markPrice@1s']

# Create a stream with better readable output by using `UnicornFy`
ubwa.create_stream(channels, markets, output="UnicornFy")

async def start_websocket():
    try:
        while not ubwa.is_manager_stopping():
            # Take the received data
            data = ubwa.pop_stream_data_from_stream_buffer()
            if data:
                if "data" in data:
                    for item in data["data"]:
                        try:
                            await compare_and_update_price(item)  # Await the async function
                        except Exception as e:
                            pass
            else:
                await asyncio.sleep(0.01)  # Use asyncio.sleep instead of time.sleep
    except KeyboardInterrupt:
        print("Gracefully stopping ...")
        ubwa.stop_manager()
    except Exception as error_msg:
        print(f"\r\nERROR: {error_msg}")
        print("Gracefully stopping ...")
        ubwa.stop_manager()
