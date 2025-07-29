"""
Discount bank

https://www.discountbank.co.il/private/general-information/foreign-currency-transfers/exchange-rates/
Takes the data from:
https://www.discountbank.co.il/api/ExchangeRates/GetExchangeRates?bankCode=0011
"""

import pandas as pd

from xil._df_normalizer import BaseDataFrameNormalizer

_DISCOUNT_URL = "\
https://www.discountbank.co.il/api/ExchangeRates/GetExchangeRates?bankCode=0011"
_IDX0 = pd.MultiIndex.from_product([["currency"], ["code", "amount", "official rate"]])
_IDX1 = pd.MultiIndex.from_product([["cash", "transfer"], ["buy", "sell"]])
_DISCOUNT_IDX = _IDX0.append(_IDX1)


def get_discount_df(url: str = _DISCOUNT_URL) -> pd.DataFrame:
    """Get Discount Bank exchange rates"""
    s = pd.read_json(url, typ="series")
    df = pd.json_normalize(s.data["exchangeRates"]["CurrenciesList"])
    df.columns = _DISCOUNT_IDX
    df = BaseDataFrameNormalizer(df).norm()
    return df
