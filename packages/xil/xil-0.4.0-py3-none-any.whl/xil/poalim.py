"""
Scrape Bank Hapoalim exchange data publicly visible on
https://www.bankhapoalim.co.il/he/foreign-currency/exchange-rates
"""

from datetime import date

import pandas as pd

from xil._currencies import USD_HEB_NAME
from xil._df_normalizer import JPYNormalizer

_POALIM_GET_URL = "https://www.bankhapoalim.co.il/he/coin-rates"
_DATE_QUERY = "?date="
_POALIM_QUERY = _POALIM_GET_URL + _DATE_QUERY
_DATE_FORMAT = "%Y-%m-%d"  # YYYY-MM-DD
_RELEVANT_COLS = [
    "DT_ERECH",
    "NAME_HEB",
    "SHAAR_YATZIG",
    "AHUZ_SHINUI",
    "SHAAR_CHK_KNIA",
    "SHAAR_CHK_MECHIRA",
    "SHAAR_CASH_KNIA",
    "SHAAR_CASH_MECHIRA",
]
_IDX0 = pd.Index(["date"])
_IDX1 = pd.MultiIndex.from_product(
    [["currency"], ["name", "official rate", "change (%)"]]
)
_IDX2 = pd.MultiIndex.from_product([["transfer", "cash"], ["buy", "sell"]])
_IDX = _IDX0.append(_IDX1.append(_IDX2))


def _get_url(t: date | None) -> str:
    if t is None:
        return _POALIM_GET_URL
    return _POALIM_QUERY + t.strftime(_DATE_FORMAT)


class PoalimNormalizer(JPYNormalizer):
    """Bank HaPoalim data normalizer"""

    _USD_ALIAS = 'דולר ארה"ב - Cloned'

    @classmethod
    def _fix_usd(cls, raw_name: str) -> str:
        """Fix USD currency name"""
        if raw_name == cls._USD_ALIAS:
            return USD_HEB_NAME
        return raw_name

    @classmethod
    def preprocess_names(cls, names: pd.Series) -> pd.Series:
        names = super().preprocess_names(names)
        return names.apply(cls._fix_usd)


def get_df(t: date | None = None, keep_last_date_only: bool = True) -> pd.DataFrame:
    """
    Get poalim exchange data from the latest available day or a specified
    date t as a pandas DataFrame. If keep_last_date_only is true, and there
    is no specified date t, only the last available date's data is returned.
    """
    df = pd.read_json(_get_url(t))
    if df.empty:
        return df

    df = df[_RELEVANT_COLS]
    df.columns = _IDX

    df.date = pd.to_datetime(df.date, format=_DATE_FORMAT).dt.date

    if keep_last_date_only and t is None:
        df = df[df.date == df.date.max()]

    df = PoalimNormalizer(df).norm()
    return df
