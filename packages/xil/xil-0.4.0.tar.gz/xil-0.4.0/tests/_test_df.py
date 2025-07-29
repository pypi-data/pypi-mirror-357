# pylint: disable=missing-module-docstring
import pandas as pd

from xil._currencies import CurrencyCode


def _test_df_sanity(df: pd.DataFrame, expected_currencies: list[CurrencyCode]) -> None:
    """Test the actual vs. expected currencies and rates"""
    assert (df.index == expected_currencies).all(), "The currencies are not as expected"
    assert (df[("transfer", "sell")] > df[("transfer", "buy")]).all()
    assert (df[("cash", "sell")] > df[("cash", "buy")]).all()
    assert (df[("cash", "sell")] > df[("transfer", "sell")]).all()
    assert (df[("transfer", "buy")] > df[("cash", "buy")]).all()
