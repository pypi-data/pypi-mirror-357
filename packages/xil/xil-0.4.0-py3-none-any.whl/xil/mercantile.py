"""
Mercantile bank

https://www.mercantile.co.il/en/private/foregin-currency/exchange-rates/
Taken from:
https://www.mercantile.co.il/api/ExchangeRates/GetExchangeRates?bankCode=0017

The structure is identical Discount's, but the data is different.
"""

import pandas as pd

from xil.discount import get_discount_df as _get_discount_df

_MERCANTILE_URL = "\
https://www.mercantile.co.il/api/ExchangeRates/GetExchangeRates?bankCode=0017"


def get_mercantile_df(url: str = _MERCANTILE_URL) -> pd.DataFrame:
    """Get Mercantile Bank exchange rates"""
    # The structure is identical Discount's, but the data is different - use Discount's
    # function
    return _get_discount_df(url)
