"""
Leumi's official exchange web page:
https://www.leumi.co.il/Lobby/currency_rates/40806/
embeds the table from:
https://www.bankleumi.co.il/vgnprod/currency/new_shaar_muskamim.html
https://www.bankleumi.co.il/Rates/Forex/Scripts/drawTable.js
which in turn consumes its data from:
https://www.bankleumi.co.il/Rates/Api3.5/ForeignExchange/LatestSelectedRates.aspx

Historical data by currency ID:
https://www.bankleumi.co.il/vgnprod/currency/ExchangeRateByCurrency.aspx?in_matbea=1

For business data:
https://biz.leumi.co.il/portal/site/Business/home_03/currency_rates/12283/
the table is embedded from the static page:
https://www.bankleumi.co.il/vgnprod/ltrade_new_shaar_muskamim_multilang_vgn_HE.html

Looks like the business data is identical to the private data.
"""

import pandas as pd

from xil._df_normalizer import JPYNormalizer
from xil._headers import UA_HEADER

_LEUMI_URL = "\
https://www.bankleumi.co.il/Rates/Api3.5/ForeignExchange/LatestSelectedRates.aspx"
_IDX0 = pd.MultiIndex.from_product(
    [["currency"], ["name", "official rate", "change (%)"]]
)
_IDX1 = pd.MultiIndex.from_product([["transfer", "cash"], ["buy", "sell"]])
_IDX = _IDX0.append(_IDX1)


class LeumiNormalizer(JPYNormalizer):
    """Leumi bank data normalizer"""

    _QUOT = "&quot;"

    @classmethod
    def _fix_quot(cls, raw_name: str) -> str:
        """fix " in 'דולר ארה&quot;ב'"""
        return raw_name.replace(cls._QUOT, '"')

    @classmethod
    def preprocess_names(cls, names: pd.Series) -> pd.Series:
        names = super().preprocess_names(names)
        return names.apply(cls._fix_quot)


def get_leumi_df(url: str = _LEUMI_URL) -> pd.DataFrame:
    """Get Leumi Bank exchange rates"""
    series = pd.read_json(url, typ="series", storage_options=UA_HEADER)
    # date = s.yatzigDate  # Hour in `s.topHeaderText`
    df = pd.json_normalize(series.data)
    df = df[
        [
            "currencyName",
            "yatzig",
            "percent",
            "hamchaot.knia",
            "hamchaot.mechira",
            "mezuman.knia",
            "mezuman.mechira",
        ]
    ]
    df.columns = _IDX
    df = df.loc[df[("currency", "name")] != "סל המטבעות", :]
    df = LeumiNormalizer(df).norm()
    return df
