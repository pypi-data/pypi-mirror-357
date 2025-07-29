"""
Bank of Israel (BOI) official exchange rates data.

The data is available on the following pages (when viewing the source):
https://www.boi.org.il/roles/markets/%D7%A9%D7%A2%D7%A8%D7%99-%D7%97%D7%9C%D7%99%D7%A4%D7%99%D7%9F-%D7%99%D7%A6%D7%99%D7%92%D7%99%D7%9D/
https://www.boi.org.il/en/economic-roles/financial-markets/exchange-rates/

The public API, which is also more accurate, is available with the following URL:
https://boi.org.il/PublicApi/GetExchangeRates

A slightly different URL can also be used to get a single key, e.g.:
https://boi.org.il/PublicApi/GetExchangeRate?key=USD
For more information, see:
https://www.boi.org.il/%D7%A9%D7%90%D7%9C%D7%95%D7%AA-%D7%95%D7%AA%D7%A9%D7%95%D7%91%D7%95%D7%AA-%D7%A2%D7%9C-%D7%94%D7%A9%D7%99%D7%9E%D7%95%D7%A9-%D7%91%D7%90%D7%AA%D7%A8-%D7%94%D7%97%D7%93%D7%A9/
"""

from functools import partial

import pandas as pd

from xil._df_normalizer import _CURRENCY_KEY, BaseDataFrameNormalizer
from xil._headers import get_url_response

_BOI_URL = "https://boi.org.il/PublicApi/GetExchangeRates"
_IDX = pd.MultiIndex.from_product(
    [[_CURRENCY_KEY], ["code", "official rate", "change (%)", "amount", "time"]]
)

get_boi_url_response = partial(get_url_response, set_context=True)


def get_boi_df(url: str = _BOI_URL) -> pd.DataFrame:
    """Get Bank of Israel (BOI) exchange rates"""
    with get_boi_url_response(url) as response:
        series = pd.read_json(response, typ="series", convert_dates=True)
    assert "exchangeRates" in series
    df = pd.json_normalize(series.exchangeRates)
    df.columns = _IDX
    df = BaseDataFrameNormalizer(df).norm()
    return df


if __name__ == "__main__":
    print(get_boi_df())
