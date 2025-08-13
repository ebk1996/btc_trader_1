from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
    KRAKEN_API_KEY = os.getenv("KRAKEN_API_KEY", "")
    KRAKEN_API_SECRET = os.getenv("KRAKEN_API_SECRET", "")
    SYMBOL = os.getenv("SYMBOL", "XBT/USD")
    YF_TICKER = os.getenv("YF_TICKER", "BTC-USD")
    BASE_ORDER_USD = float(os.getenv("BASE_ORDER_USD", "25"))
    FAST_MA = int(os.getenv("FAST_MA", "20"))
    SLOW_MA = int(os.getenv("SLOW_MA", "50"))
    INTERVAL = os.getenv("INTERVAL", "15m")

settings = Settings()
