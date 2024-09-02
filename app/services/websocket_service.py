import asyncio
import os
import json
from datetime import datetime, timedelta
from unicorn_binance_websocket_api import BinanceWebSocketApiManager
from app.utils.compare_price import compare_and_update_price  # Import your price comparison function

class WebSocketService:
    def __init__(self, print_new_data=False):
        self.example_database = []
        self.print_new_data = print_new_data

        # Define the markets and channels
        self.markets = ['btcusdt', 'ethusdt']
        self.channels = ['trade']

        self.ubwa = BinanceWebSocketApiManager(exchange='binance.com-futures',
                                               auto_data_cleanup_stopped_streams=True,
                                               enable_stream_signal_buffer=True,
                                               output_default='dict')

    async def start_service(self):
        # Create a stream for the defined markets and channels
        self.ubwa.create_stream(self.channels, self.markets,
                                process_asyncio_queue=self.processing_of_new_data,
                                stream_label="trade_stream")

        while not self.ubwa.is_manager_stopping():
            await asyncio.sleep(1)
            stream_info = self.ubwa.get_stream_info(stream_id=self.ubwa.get_stream_id_by_label('trade_stream'))
            status_text = (f"Stream 'trade_stream' is {stream_info['status']} "
                           f"(last_stream_signal={stream_info['last_stream_signal']})\r\n")
            # print(f"Status:\r\n\tStored {len(self.example_database)} data records in `self.example_database`\r\n"
            #       f"{status_text}")


    async def processing_of_new_data(self, stream_id=None):
        print(f"Processing data from stream {self.ubwa.get_stream_label(stream_id=stream_id)} ...")
        while not self.ubwa.is_stop_request(stream_id=stream_id):
            data = await self.ubwa.get_stream_data_from_asyncio_queue(stream_id)
            # self.example_database.append(data)
            # if self.print_new_data:
            #     print(f"Received data by stream `{self.ubwa.get_stream_label(stream_id=stream_id)}`: {data}")
            
            # Ensure the 'data' key exists before trying to access it
            if 'data' in data:
                try:
                    await compare_and_update_price(data['data'])  # Pass the 'data' part of the message
                except Exception as e:
                    print(f"Error processing data: {e}")
            else:
                print(f"Unexpected data format received: {data}")
            
            self.ubwa.asyncio_queue_task_done(stream_id)







    def stop_service(self):
        self.ubwa.stop_manager()

async def start_websocket():
    ws_service = WebSocketService(print_new_data=True)
    try:
        await ws_service.start_service()
    except KeyboardInterrupt:
        print("\r\nGracefully stopping ...")
    except Exception as e:
        print(f"\r\nERROR: {e}")
        print("Gracefully stopping ...")
    finally:
        ws_service.stop_service()
