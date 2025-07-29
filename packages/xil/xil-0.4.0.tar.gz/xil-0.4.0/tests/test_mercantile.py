# pylint: disable=missing-module-docstring, missing-function-docstring
import pandas as pd
import pytest

from xil._currencies import CurrencyCode
from xil.mercantile import get_mercantile_df

from .test_discount import test_df as _test_df_helper


@pytest.fixture(name="df")
def df_fixture() -> pd.DataFrame:
    return get_mercantile_df()


@pytest.fixture(name="currencies")
def currencies_fixture() -> set[CurrencyCode]:
    return {
        CurrencyCode.CAD,
        CurrencyCode.MXN,
        CurrencyCode.EGP,
        CurrencyCode.RUB,
        CurrencyCode.JPY,
        CurrencyCode.LBP,
        CurrencyCode.XAG,
        CurrencyCode.XAU,
        CurrencyCode.CNY,
        CurrencyCode.SEK,
        CurrencyCode.ZAR,
        CurrencyCode.SAL,
        CurrencyCode.USD,
        CurrencyCode.XPT,
        CurrencyCode.SGD,
        CurrencyCode.INR,
        CurrencyCode.AUD,
        CurrencyCode.BRL,
        CurrencyCode.CHF,
        CurrencyCode.JOD,
        CurrencyCode.NOK,
        CurrencyCode.PLN,
        CurrencyCode.DKK,
        CurrencyCode.GBP,
        CurrencyCode.XPD,
        CurrencyCode.NZD,
        CurrencyCode.HKD,
        CurrencyCode.HUF,
        CurrencyCode.TRY,
        CurrencyCode.EUR,
    }


@pytest.mark.parametrize("dropped_currencies", [[CurrencyCode.XAU]])
@pytest.mark.live
def test_df(
    df: pd.DataFrame,
    currencies: set[CurrencyCode],
    dropped_currencies: list[CurrencyCode],
) -> None:
    _test_df_helper(df, currencies, dropped_currencies=dropped_currencies)
