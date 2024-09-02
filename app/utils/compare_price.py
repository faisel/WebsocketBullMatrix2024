import json
import os
from datetime import datetime, timedelta
from pytz import timezone
from app.services.api_service import trigger_price_change
from app.services.email_service import send_email_notification

async def compare_and_update_price(new_data):
    try:
        symbol = new_data['s']
        new_price = new_data['p']
        timestamp = new_data['E'] / 1000
        json_file = os.path.join('data', f"{symbol.lower()}_price.json")

        # Check if the file exists and load the old data
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                old_data = json.load(f)
                old_price = old_data.get('price')
                old_timestamp = old_data.get('timestamp')
        else:
            old_price = None
            old_timestamp = None

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


        # print("################## \n \n")

        # print("symbol", symbol)
        # print("old_price", old_price)
        # print("price_diff", price_diff)
        # print("new_price", new_price)


        # print("################## \n \n")


        if old_price is not None:
            if symbol == "BTCUSDT" and price_diff >= 1.0:
                trigger_data["is_big_diff"] = True
                await trigger_price_change(trigger_data)
                with open(json_file, 'w') as f:
                    json.dump(trigger_data, f)
            elif symbol == "ETHUSDT" and price_diff >= 0.5:
                trigger_data["is_big_diff"] = True
                await trigger_price_change(trigger_data)
                with open(json_file, 'w') as f:
                    json.dump(trigger_data, f)

            # Check if price hasn't changed for 30 seconds
            if datetime.utcnow() - timedelta(seconds=30) > datetime.utcfromtimestamp(old_timestamp):
                send_email_notification("Price Unchanged Alert", f"Price for {symbol} has not changed for 30 seconds.")

        # Save the updated data to the JSON file
        with open(json_file, 'w') as f:
            json.dump(trigger_data, f)

    except Exception as e:
        print(f"Error in compare_and_update_price: {e}")

    return True
