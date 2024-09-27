import httpx
import json
import asyncio
from app.core.config import settings
from app.utils.logging_config import get_logger
import time

logger = get_logger(__name__)

# Global variables to track processing for each symbol
symbol_processing = {"BTCUSDT": False, "ETHUSDT": False}
symbol_locks = {"BTCUSDT": asyncio.Lock(), "ETHUSDT": asyncio.Lock()}
latest_alerts = {"BTCUSDT": None, "ETHUSDT": None}



async def trigger_price_change(alert):
    symbol = alert['symbol']
    alert['price'] = str(round(float(alert['price']), 2))
    alert_trigger = f"{int(time.time())}_{alert['symbol']}_{alert['price']}"

    # Load the current configuration to check the websocket switch
    with open("data/matrix_config.json", "r") as f:
        current_config = json.load(f)

    websocket_switch = current_config['matrix_config'][0]['config_websocket_switch']

    # Check if the websocket switch is OFF
    if not websocket_switch:
        logger.info(f"Websocket switch is OFF, not triggering the price change alert for {symbol}.")
        return  # Exit the function

    # Log that we are checking the lock for this symbol
    logger.info(f"Checking lock for {symbol}")

    # Store the latest alert for the symbol
    latest_alerts[symbol] = alert

    # Acquire the lock for this symbol to process only one alert at a time
    async with symbol_locks[symbol]:
        if symbol_processing[symbol]:
            logger.info(f"Already processing {symbol}, skipping this alert.")
            return  # Skip the alert if processing is still ongoing

        logger.info(f"Lock acquired for {symbol}, starting processing for {alert_trigger}")
        symbol_processing[symbol] = True  # Set the flag to indicate processing has started

        # Wait for API response with a 5-second timeout
        timeout = 5  # seconds
        url = settings.PRICE_CHANGE_API_URL
        headers = {"Content-Type": "application/json"}

        print(f"Processing price alert for {symbol}: {alert}")

        try:
            # Log that we are sending the API request
            logger.info(f"Sending API request for {symbol}: {alert}")

            # Make the API call with a timeout
            async with httpx.AsyncClient() as client:
                api_task = client.post(url, json=alert, headers=headers)
                response = await asyncio.wait_for(api_task, timeout=timeout)

                # Log the response details
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Received API response for {symbol}: {result}")

                    # Check the response format and log relevant details
                    if result.get("success") is not None:
                        logger.info("\n \n \n \n")
                        logger.info(f"ALERT Trigger {alert_trigger}")
                        logger.info(f"STARTED API response for {symbol}")
                        logger.info(f"API success: {result.get('success')}")
                        logger.info(f"API message: {result.get('message', 'No message provided')}")
                        logger.info(f"END API response for {symbol}")
                    else:
                        logger.warning(f"API response for {symbol} is missing 'success' key or is malformed.")
                else:
                    logger.error(f"Failed to trigger API for {symbol}, status code: {response.status_code}")

        except asyncio.TimeoutError:
            logger.warning(f"API call for {symbol} timed out after {timeout} seconds.")

        except httpx.RequestError as e:
            logger.error(f"HTTP request error for {symbol}: {e}")

        finally:
            # After processing, check if a new alert came in during the processing
            latest_alert = latest_alerts[symbol]
            if latest_alert != alert:
                logger.info(f"Skipping intermediate alert for {symbol} while processing.")
            else:
                logger.info(f"Completed processing for {symbol} with no newer alert.")

            # Release the processing flag
            symbol_processing[symbol] = False
            logger.info(f"PROCESSING completed for {symbol}, lock released.\n \n \n")



