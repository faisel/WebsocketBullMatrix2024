import httpx
import json
import asyncio
from app.core.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Global variables to track processing for each symbol
symbol_processing = {"BTCUSDT": False, "ETHUSDT": False}
symbol_locks = {"BTCUSDT": asyncio.Lock(), "ETHUSDT": asyncio.Lock()}
latest_alerts = {"BTCUSDT": None, "ETHUSDT": None}

async def trigger_price_change(alert):
    symbol = alert['symbol']

    # Load the current configuration to check the websocket switch
    with open("data/matrix_config.json", "r") as f:
        current_config = json.load(f)

    websocket_switch = current_config['matrix_config'][0]['config_websocket_switch']

    # Check if the websocket switch is OFF
    if not websocket_switch:
        logger.info(f"Websocket switch is OFF, not triggering the price change alert for {symbol}.")
        return  # Exit the function

    # Store the latest alert for the symbol
    latest_alerts[symbol] = alert

    # Wait for the lock to be available for this symbol
    async with symbol_locks[symbol]:
        # Set the processing flag to True
        symbol_processing[symbol] = True

        # Wait for API response with a 5-second timeout
        timeout = 5  # seconds
        url = settings.PRICE_CHANGE_API_URL
        headers = {"Content-Type": "application/json"}

        print(f"Processing price alert for {symbol}: {alert}")

        try:
            # Wait for the API request with a timeout
            async with httpx.AsyncClient() as client:
                api_task = client.post(url, json=alert, headers=headers)
                response = await asyncio.wait_for(api_task, timeout=timeout)

                # Check if the response is successful
                if response.status_code == 200:
                    result = response.json()
                    print(f"Received API response for {symbol}: {result}")
                    if result.get("success"):
                        logger.info("\n \n \n \n")
                        logger.info(f"STARTED API response for {symbol}")
                        logger.info(f"API success: {result.get('success')}")
                        logger.info(f"API message: {result.get('message')}")
                        logger.info(f"API position_id: {result.get('position_id')}")
                        logger.info(f"API price: {result.get('price')}")
                        logger.info(f"API type: {result.get('type')}")
                        logger.info(f"API isHedgeOpen: {result.get('isHedgeOpen')}")
                        logger.info(f"API trigger: {result.get('trigger')}")
                        logger.info(f"API trigger_success: {result.get('trigger_success')}")
                        logger.info(f"API trigger_message: {result.get('trigger_message')}")
                        logger.info(f"END API response for {symbol}")

                else:
                    logger.error(f"Failed to trigger API price change for {symbol}. Status code: {response.status_code}")
        except asyncio.TimeoutError:
            logger.warning(f"Timeout occurred while waiting for API response for {symbol}, processing the latest alert instead.")

        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {url} for {symbol}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        finally:
            # After processing, check if a new alert came in during the wait time
            latest_alert = latest_alerts[symbol]
            if latest_alert != alert:
                logger.info(f"Skipping intermediate alert for {symbol} while processing the previous one.")
            else:
                print(f"Finished processing the alert for {symbol}.")

            # Mark the processing as finished
            symbol_processing[symbol] = False
