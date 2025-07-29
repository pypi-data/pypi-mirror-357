"""
One Zero bank official webpage:
https://www.onezerobank.com/currencies/
It loads the data from:
https://dv16ymfyh91nr.cloudfront.net/MarketingRatesReport/MarketingSiteFCYRatesCurrentReport.json
"""

import pandas as pd

from xil._currencies import CurrencyCode
from xil._df_normalizer import BaseDataFrameNormalizer

_ONEZERO_URL = "\
https://dv16ymfyh91nr.cloudfront.net/MarketingRatesReport/MarketingSiteFCYRatesCurrentReport.json"
_IDX0 = pd.MultiIndex.from_product([["currency"], ["code", "official rate"]])
_IDX1 = pd.MultiIndex.from_product([["transfer"], ["buy", "sell"]])
_IDX = _IDX0.append(_IDX1)


def get_onezero_df(url: str = _ONEZERO_URL) -> pd.DataFrame:
    """Get One Zero bank exchange rates"""
    series = pd.read_json(url, typ="series")
    # series.generatingReportDateTime holds the date in YYYY-MM-DD format
    df = pd.json_normalize(series.marketingRecords)
    df = df[df.fromCurrency == CurrencyCode.ILS]  # remove data duplication
    df.drop(labels="fromCurrency", axis="columns", inplace=True)
    df.columns = _IDX
    df = BaseDataFrameNormalizer(df).norm()
    return df
