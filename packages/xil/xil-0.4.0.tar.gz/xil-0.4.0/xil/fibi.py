"""
FIBI - First International Bank of Israel (HaBank HaBeinleumi)

The exchange rates page
https://www.fibi.co.il/wps/portal/FibiMenu/Marketing/Private/ForeignCurrency/Trade/Rates
includes static data from:
https://apps.fibi.co.il/Matach/matach.aspx
"""

import pandas as pd

from xil._df_normalizer import DataFrameNormalizer
from xil._headers import UA_HEADER

_FIBI_URL = "http://apps.fibi.co.il/Matach/matach.aspx"
_ENCODING = "iso-8859-8"
_MATCH = "העברות והמחאות"
_HEADER = [0, 1]
_ATTRS = {"class": "clsPart"}
_RELEVANT_COLS = [
    ("מטבע", "מטבע"),
    ("יחידה", "יחידה"),
    ("יציג", "יציג"),
    ("בנקנוטים", "מכירה"),
    ("בנקנוטים", "קניה"),
    ("העברות והמחאות", "מכירה"),
    ("העברות והמחאות", "קניה"),
]
_IDX0 = pd.MultiIndex.from_product([["currency"], ["name", "amount", "official rate"]])
_IDX1 = pd.MultiIndex.from_product([["cash", "transfer"], ["sell", "buy"]])
_IDX = _IDX0.append(_IDX1)


def get_fibi_df(url: str = _FIBI_URL) -> pd.DataFrame:
    """Get FIBI exchange rates"""
    dfs = pd.read_html(
        url,
        match=_MATCH,
        header=_HEADER,
        encoding=_ENCODING,
        attrs=_ATTRS,
        storage_options=UA_HEADER,
    )

    df = dfs[0]  # guaranteed to have at least one element at this point
    df = df[_RELEVANT_COLS]
    df.columns = _IDX
    df = DataFrameNormalizer(df).norm()
    return df


if __name__ == "__main__":
    print(get_fibi_df())
