# pylint: disable=missing-module-docstring, missing-function-docstring, redefined-outer-name
import pandas as pd
import pytest

from xil._currencies import CurrencyCode
from xil.leumi import get_leumi_df

from ._test_df import _test_df_sanity


@pytest.fixture
def df() -> pd.DataFrame:
    return get_leumi_df()


@pytest.fixture()
def expected_currencies() -> list[CurrencyCode]:
    return [
        CurrencyCode.USD,
        CurrencyCode.EUR,
        CurrencyCode.GBP,
        CurrencyCode.JPY,
        CurrencyCode.CHF,
        CurrencyCode.AUD,
        CurrencyCode.CAD,
        CurrencyCode.ZAR,
        CurrencyCode.AED,
        CurrencyCode.SEK,
        CurrencyCode.NOK,
        CurrencyCode.DKK,
    ]


@pytest.mark.live
def test_df(df: pd.DataFrame, expected_currencies: list[CurrencyCode]) -> None:
    _test_df_sanity(df, expected_currencies)
