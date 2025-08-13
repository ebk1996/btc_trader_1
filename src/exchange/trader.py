from .kraken_client import KrakenClient
from loguru import logger

def execute_signal(kclient, symbol, price, base_order_usd, signal):
    if signal == 'BUY':
        # base_order_usd is a USD quote amount to spend
        resp = kclient.market_buy(symbol, float(base_order_usd))
        logger.info(f"Placed BUY: {resp}")
    elif signal == 'SELL':
        ...
    else:
        logger.info("HOLD (no action)")