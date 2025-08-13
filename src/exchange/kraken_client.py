import ccxt
from . import kraken_client

class KrakenClient:
    def __init__(self, api_key: str, api_secret: str, dry_run: bool = True):
        self.dry_run = dry_run
        self.exchange = ccxt.kraken({
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
        })

    def get_price(self, symbol: str) -> float:
        ticker = self.exchange.fetch_ticker(symbol)
        return float(ticker["last"])

    def market_buy(self, symbol: str, usd_cost: float):
        self.exchange.load_markets()
        market = self.exchange.market(symbol)

        # Ensure your spend meets Kraken's minimums
        # Try cost min first; fall back to amount*price if cost min absent
        price = float(self.exchange.price_to_precision(symbol, self.exchange.fetch_ticker(symbol)['last']))
        min_amount = (market.get('limits', {}).get('amount', {}) or {}).get('min')
        min_cost = (market.get('limits', {}).get('cost', {}) or {}).get('min')

        if min_cost is None and min_amount is not None and price:
            min_cost = float(min_amount) * float(price)

        if min_cost is not None and float(usd_cost) < float(min_cost):
            raise ValueError(f"Order too small for {symbol}: ${usd_cost} < min cost ${min_cost}")

        # Use 'cost' param for Kraken market buy (spend this much quote currency)
        params = {'cost': self.exchange.cost_to_precision(symbol, usd_cost)}
        # When using 'cost', amount should be None for Kraken via CCXT
        return self.exchange.create_order(symbol, 'market', 'buy', None, None, params)

    def market_sell(self, symbol: str, amount: float):
        if self.dry_run:
            return {"status": "DRY_RUN_SELL", "symbol": symbol, "amount": amount}
        return self.exchange.create_market_sell_order(symbol, amount)
