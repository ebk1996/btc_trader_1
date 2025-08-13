import os, time
import schedule
from loguru import logger
from config import settings
from strategies.ma_crossover import fetch_history, signal_ma_cross
from exchange.kraken_client import KrakenClient
from exchange.trader import execute_signal

def interval_to_minutes(s: str) -> int:
    s = s.strip().lower()
    if s.endswith("m"): return int(s[:-1])
    if s.endswith("h"): return int(s[:-1]) * 60
    return 15

def job():
    k = KrakenClient(settings.KRAKEN_API_KEY, settings.KRAKEN_API_SECRET, settings.DRY_RUN)
    df = fetch_history(settings.YF_TICKER, period="1d", interval="1m")
    sig = signal_ma_cross(df, settings.FAST_MA, settings.SLOW_MA)
    price = k.get_price(settings.SYMBOL)
    logger.info(f"Signal={sig} | Price={price}")
    execute_signal(k, settings.SYMBOL, price, settings.BASE_ORDER_USD, sig)

if __name__ == "__main__":
    logger.info(f"Starting bot | DRY_RUN={settings.DRY_RUN}")
    mins = interval_to_minutes(settings.INTERVAL)
    schedule.every(mins).minutes.do(job)
    job()  # run once at start
    while True:
        schedule.run_pending()
        time.sleep(1)
