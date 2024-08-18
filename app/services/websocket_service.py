import asyncio
from unicorn_binance_websocket_api import BinanceWebSocketApiManager
import logging
import os
from app.utils.compare_price import compare_and_update_price  # Import your price comparison function

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    filename=os.path.join(os.path.dirname(__file__), 'websocket_service.log'),
                    format="{asctime} [{levelname:8}] {process} {thread} {module}: {message}",
                    style="{")

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
                #print("responsedata", data)
                # Directly check if 'data' key exists in the dictionary
                if "data" in data:
                    # Work with the received data
                    for item in data["data"]:
                        #print(f"Processing item: {item}")  # Debugging line
                        try:
                            await compare_and_update_price(item)  # Await the async function
                        except Exception as e:
                            pass
                            #print(f"Error processing item {item}: {e}")
                #else:
                    #print("Received data without 'data' key:", data)
            else:
                await asyncio.sleep(0.01)  # Use asyncio.sleep instead of time.sleep
    except KeyboardInterrupt:
        # Stop the UBWA instance if CTRL+C is pressed
        print("Gracefully stopping ...")
        ubwa.stop_manager()
    except Exception as error_msg:
        # Stop the UBWA instance and print out the error that has occurred
        print(f"\r\nERROR: {error_msg}")
        print("Gracefully stopping ...")
        ubwa.stop_manager()
