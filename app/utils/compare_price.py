import json
import os
from datetime import datetime, timedelta
from pytz import timezone
from app.services.api_service import trigger_price_change
from app.services.email_service import send_email_notification

DATA_PATH = 'data'

# Set the Zurich timezone
zurich_tz = timezone('Europe/Zurich')

async def compare_and_update_price(new_data):

    #print("new_data", new_data)

    symbol = new_data['symbol']
    new_price = new_data['mark_price']
    timestamp = new_data['event_time']
    index_price = new_data['index_price']
    estimated_settle_price = new_data['estimated_settle_price']
    json_file = os.path.join(DATA_PATH, f"{symbol.lower()}_price.json")

    # Get the current time in Zurich timezone
    zurich_time = datetime.now(zurich_tz)
    apptime = zurich_time.strftime("%b %d %H:%M:%S")  # e.g., "May 03 07:52:16"
    servertime = datetime.now().strftime("%b %d %H:%M:%S")  # Server time in UTC

    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            old_data = json.load(f)
            old_price = old_data['price']
            old_timestamp = old_data['timestamp']
            price_diff = abs(float(new_price) - float(old_price))  # Always positive

            if price_diff != 0:
                trigger_data = {
                    "BULLMATRIX_API_KEY": os.getenv('BULLMATRIX_API_KEY'),
                    "apptime": apptime,
                    "servertime": servertime,
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "price": new_price,
                    "price_big_p": estimated_settle_price,
                    "price_i": index_price,
                    "price_diff": str(price_diff),
                    "is_big_diff": abs(price_diff) > 1  # Example threshold
                }

                await trigger_price_change(trigger_data)
                with open(json_file, 'w') as f:
                    json.dump(trigger_data, f)

            if datetime.now() - timedelta(seconds=30) > datetime.fromtimestamp(old_timestamp):
                send_email_notification("Price Unchanged Alert", f"Price for {symbol} has not changed for 30 seconds.")

    else:
        with open(json_file, 'w') as f:
            json.dump({
                    "BULLMATRIX_API_KEY": os.getenv('BULLMATRIX_API_KEY'),
                    "apptime": apptime,
                    "servertime": servertime,
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "price": new_price,
                    "price_big_p": estimated_settle_price,
                    "price_i": index_price,
                    "price_diff": str(price_diff),
                    "is_big_diff": abs(price_diff) > 1  # Example threshold
                }, f)
