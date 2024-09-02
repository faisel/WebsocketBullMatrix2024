import json
import os
import asyncio
from datetime import datetime, timedelta
from pytz import timezone
from app.services.api_service import trigger_price_change
from app.services.email_service import send_email_notification


# Lock to ensure only one request is processed at a time
processing_lock = asyncio.Lock()

# State to track if processing is active
is_processing = False


async def compare_and_update_price(new_data):
    global is_processing

    async with processing_lock:  # Only one process can enter this block at a time
        if is_processing:
            print(f"compare_and_update_price - SKIPPED - {new_data}")
            return False

        # Mark as processing
        is_processing = True

        try:
            symbol = new_data['s']
            new_price = new_data['p']
            timestamp = new_data['E'] / 1000
            json_file = os.path.join('data', f"{symbol.lower()}_price.json")

            # Initialize variables
            old_price = None
            old_timestamp = None

            # Check if the file exists and load the old data
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r') as f:
                        old_data = json.load(f)
                        old_price = old_data.get('price')
                        old_timestamp = old_data.get('timestamp')
                except (json.JSONDecodeError, OSError) as e:
                    print(f"Error reading JSON file: {e}")

            price_diff = abs(float(new_price) - float(old_price)) if old_price else 0

            # Create the data structure to store and possibly send
            trigger_data = {
                "BULLMATRIX_API_KEY": '0cce3DB04ed7-e645-4b16-8786-b260a34f5Z47433ab32',
                "apptime": datetime.now(timezone('Europe/Zurich')).strftime("%b %d %H:%M:%S"),
                "servertime": datetime.utcnow().strftime("%b %d %H:%M:%S"),
                "timestamp": timestamp,
                "symbol": symbol,
                "price": new_price,
                "price_big_p": new_price,
                "price_i": new_price,
                "price_diff": str(price_diff),
                "is_big_diff": False
            }

            # Check for price differences
            if old_price is not None:
                if symbol == "BTCUSDT" and price_diff >= 1.0:
                    trigger_data["is_big_diff"] = True
                    await trigger_price_change(trigger_data)
                    # Save the updated data to the JSON file
                    try:
                        with open(json_file, 'w') as f:
                            json.dump(trigger_data, f)
                    except OSError as e:
                        print(f"Error writing to JSON file: {e}")

                elif symbol == "ETHUSDT" and price_diff >= 0.5:
                    trigger_data["is_big_diff"] = True
                    await trigger_price_change(trigger_data)

                    # Save the updated data to the JSON file
                    try:
                        with open(json_file, 'w') as f:
                            json.dump(trigger_data, f)
                    except OSError as e:
                        print(f"Error writing to JSON file: {e}")

                # Check if price hasn't changed for 30 seconds
                if old_timestamp and datetime.utcnow() - timedelta(seconds=30) > datetime.utcfromtimestamp(old_timestamp):
                    send_email_notification("Price Unchanged Alert", f"Price for {symbol} has not changed for 30 seconds.")


        except KeyError as e:
            print(f"Missing key in new data: {e}")
        except Exception as e:
            print(f"Error in compare_and_update_price: {e}")
        finally:
            # Mark as not processing
            is_processing = False

    return True