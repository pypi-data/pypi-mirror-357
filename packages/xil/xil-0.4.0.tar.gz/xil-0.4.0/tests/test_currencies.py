"""
Test the _currencies module.
This test module checks only a small subset of the currencies.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring
import pytest

from xil._currencies import (
    CurrencyCode,
    CurrencyNotSupportedError,
    currency_code_from_heb_name,
    currency_from_heb_name,
    optional_currency_from_heb_name,
)


def test_currency_code_from_heb_name() -> None:
    assert currency_code_from_heb_name('דולר ארה"ב') == CurrencyCode.USD


def test_currency_from_heb_name() -> None:
    assert currency_from_heb_name("פרנק שויצרי") == "CHF"


@pytest.mark.parametrize("currency_name", ["מטבע לא קיים", "NOT A CURRENCY"])
class TestNonExistingCurrencies:
    @staticmethod
    def test_not_supported_currency(currency_name: str) -> None:
        with pytest.raises(
            CurrencyNotSupportedError, match=f"Unknown currency name: '{currency_name}'"
        ):
            currency_code_from_heb_name(currency_name)

    @staticmethod
    def test_optional_currency_returns_none(currency_name: str) -> None:
        assert optional_currency_from_heb_name(currency_name) is None
