"""
Currencies DataFrame (df) normalization.
"""

import pandas as pd

from xil._currencies import currency_from_heb_name

_CURRENCY_KEY = "currency"
_IDX0 = pd.MultiIndex.from_product(
    [[_CURRENCY_KEY], ["name", "official rate", "change (%)"]]
)
_IDX1 = pd.MultiIndex.from_product([["transfer", "cash"], ["buy", "sell"]])
_IDX = _IDX0.append(_IDX1)
_CURRENCY_CODE_KEY = (_CURRENCY_KEY, "code")
_CURRENCY_NAME_KEY = _IDX0[0]


class BaseDataFrameNormalizer:
    """
    Base class that can be used when the df has a ("currency", "code") column.
    """

    def __init__(self, df: pd.DataFrame):
        """Initialize a DataFrame (df) normalizer with a raw currencies df"""
        self.df = df

    def norm(self) -> pd.DataFrame:
        """
        Normalize the df inplace and return it - set the currency code as the index.
        """
        self.set_code_index()
        return self.df

    def set_code_index(self) -> None:
        """Set the ("currency", "code") as the df index"""
        self.df.set_index(_CURRENCY_CODE_KEY, inplace=True)


class DataFrameNormalizer(BaseDataFrameNormalizer):
    """
    This class is used to normalize currencies data frames of with a
    ("currency", "name") column.
    """

    def norm(self) -> pd.DataFrame:
        """Normalize the df inplace according to the given parameters and return it"""
        self.add_code_from_name()
        self.drop_currency_name()
        return super().norm()

    def add_code_from_name(self) -> None:
        """Add a ("currency", "code") column from the ("currency", "name") column"""
        self.df[_CURRENCY_CODE_KEY] = self.preprocess_names(
            self.df[_CURRENCY_NAME_KEY]
        ).apply(currency_from_heb_name)

    @classmethod
    def preprocess_names(cls, names: pd.Series) -> pd.Series:
        """
        A preprocessing hook to manipulate the names before passing them to the
        currency_from_heb_name function.
        """
        return names

    def drop_currency_name(self) -> None:
        """Drop the ("currency", "name") column from the df"""
        self.df.drop(labels=_CURRENCY_NAME_KEY, axis="columns", inplace=True)


class JPYNormalizer(DataFrameNormalizer):
    """
    Normalizer subclass for fixing JPY amount in the name.
    Used in Poalim and Leumi banks.
    """

    _JPY_AMOUNT = "100"

    @classmethod
    def _remove_100(cls, raw_name: str) -> str:
        """
        remove '100' from '100 ין יפני', prefix or suffix.
        Note: this method does not check the currency name.
        """
        return (
            raw_name.removeprefix(cls._JPY_AMOUNT).removesuffix(cls._JPY_AMOUNT).strip()
        )

    @classmethod
    def preprocess_names(cls, names: pd.Series) -> pd.Series:
        names = super().preprocess_names(names)
        return names.apply(cls._remove_100)
