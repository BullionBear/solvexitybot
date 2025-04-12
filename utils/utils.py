from decimal import Decimal, ROUND_DOWN
from binance.client import Client as BinanceClient
from functools import lru_cache

@lru_cache(maxsize=128)  # Set the cache size to 128 entries (or adjust as needed)
def _get_symbol_info(symbol):
    client = BinanceClient()
    symbol_info = client.get_symbol_info(symbol)
    return symbol_info

def symbol_filter(symbol: str, size: Decimal, price: Decimal) -> tuple[Decimal, Decimal]:
    symbol_info = _get_symbol_info(symbol)
    for _filter in symbol_info['filters']:
        if _filter['filterType'] == 'PRICE_FILTER':
            tick_size = Decimal(_filter['tickSize']).normalize()
            price = price.quantize(tick_size, rounding=ROUND_DOWN)
        elif _filter['filterType'] == 'LOT_SIZE':
            lot_size = Decimal(_filter['stepSize']).normalize()
            size = size.quantize(lot_size, rounding=ROUND_DOWN)
    return size, price
