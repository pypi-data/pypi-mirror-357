"""
Jerusalem bank exchange data

https://www.bankjerusalem.co.il/capital-market/rates
"""

import pandas as pd

from xil._df_normalizer import DataFrameNormalizer

_JERUSALEM_URL = "https://www.bankjerusalem.co.il/capital-market/rates"
_HEADER: None = None  # the table's header is not recognized
_AMOUNT_NAME_SPLITTER = "\xa0"
_IDX0 = pd.MultiIndex.from_product(
    [["currency"], ["name", "official rate", "change (%)"]]
)
_IDX1 = pd.MultiIndex.from_product([["cash", "transfer"], ["sell", "buy"]])
_IDX = _IDX0.append(_IDX1)


class JerusalemNormalizer(DataFrameNormalizer):
    """DataFrame normalizer for Jerusalem bank data"""

    @staticmethod
    def _fix_amount(raw_amount: str) -> str:
        return raw_amount.split(_AMOUNT_NAME_SPLITTER)[1]

    @classmethod
    def preprocess_names(cls, names: pd.Series) -> pd.Series:
        return names.apply(cls._fix_amount)


def get_jerusalem_df(url: str = _JERUSALEM_URL) -> pd.DataFrame:
    """Get Jerusalem Bank exchange rates"""
    df = pd.read_html(url, header=_HEADER)[0]
    df.columns = _IDX
    df = JerusalemNormalizer(df).norm()
    return df


if __name__ == "__main__":
    print(get_jerusalem_df())
