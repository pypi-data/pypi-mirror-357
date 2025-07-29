"""
Test the _df_normalizer module.
"""

# pylint: disable=missing-function-docstring,missing-class-docstring
from contextlib import AbstractContextManager
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from xil._df_normalizer import (
    _CURRENCY_CODE_KEY,
    _CURRENCY_KEY,
    _CURRENCY_NAME_KEY,
    BaseDataFrameNormalizer,
    DataFrameNormalizer,
    JPYNormalizer,
)


@pytest.fixture(name="currencies_df")
def fixture_currencies_df() -> pd.DataFrame:
    return pd.DataFrame(
        [['דולר ארה"ב', 1, 3.41], ["ין יפני", 100, 2.65]],
        columns=[_CURRENCY_NAME_KEY, (_CURRENCY_KEY, "amount"), ("transfer", "sell")],
    )


@pytest.fixture(name="currencies_df_with_code")
def fixture_currencies_df_with_code(currencies_df: pd.DataFrame) -> pd.DataFrame:
    DataFrameNormalizer(currencies_df).add_code_from_name()
    return currencies_df


class TestBaseNormalizer:
    @staticmethod
    def test_set_index(currencies_df_with_code: pd.DataFrame) -> None:
        BaseDataFrameNormalizer(currencies_df_with_code).set_code_index()
        assert currencies_df_with_code.index.name == _CURRENCY_CODE_KEY

    @staticmethod
    def test_norm(currencies_df: pd.DataFrame) -> None:
        df_normalizer = BaseDataFrameNormalizer(currencies_df)
        with patch.object(
            BaseDataFrameNormalizer, "set_code_index", autospec=True
        ) as mock:
            df_normalizer.norm()
            mock.assert_called_once_with(df_normalizer)


class TestNormalizer:
    @staticmethod
    def _patch_normalizer_attr(attr: str) -> AbstractContextManager[Mock]:
        return patch.object(DataFrameNormalizer, attr, autospec=True)

    @staticmethod
    def test_drop_name(currencies_df: pd.DataFrame) -> None:
        assert _CURRENCY_NAME_KEY in currencies_df.columns
        DataFrameNormalizer(currencies_df).drop_currency_name()
        assert _CURRENCY_NAME_KEY not in currencies_df.columns

    @staticmethod
    def test_add_code(currencies_df: pd.DataFrame) -> None:
        assert _CURRENCY_CODE_KEY not in currencies_df.columns
        DataFrameNormalizer(currencies_df).add_code_from_name()
        assert _CURRENCY_CODE_KEY in currencies_df.columns

    @staticmethod
    def test_preprocess_names(currencies_df: pd.DataFrame) -> None:
        names = currencies_df[_CURRENCY_NAME_KEY]
        with patch.object(
            DataFrameNormalizer, "preprocess_names", autospec=True
        ) as mock:
            DataFrameNormalizer(currencies_df).add_code_from_name()
            mock.assert_called_once_with(names)

    @classmethod
    def test_norm(cls, currencies_df: pd.DataFrame) -> None:
        df_normalizer = DataFrameNormalizer(currencies_df)
        with (
            cls._patch_normalizer_attr("add_code_from_name") as mock_add_code,
            cls._patch_normalizer_attr("set_code_index") as mock_set_index,
            cls._patch_normalizer_attr("drop_currency_name") as mock_drop_name,
        ):
            df_normalizer.norm()
            for mock in [mock_add_code, mock_set_index, mock_drop_name]:
                mock.assert_called_once_with(df_normalizer)


class TestJPYNormalizer:
    @staticmethod
    @pytest.fixture(name="jpy_df")
    def fixture_jpy_df() -> pd.DataFrame:
        return pd.DataFrame(
            [['דולר ארה"ב', 3.41], ["100 ין יפני", 2.65]],
            columns=[_CURRENCY_NAME_KEY, ("transfer", "sell")],
        )

    @staticmethod
    @pytest.fixture(name="normed_jpy_df")
    def fixture_normed_jpy_df() -> pd.DataFrame:
        return pd.DataFrame(
            [[3.41], [2.65]],
            columns=[("transfer", "sell")],
            index=pd.Index(["USD", "JPY"], name=_CURRENCY_CODE_KEY),
        )

    @staticmethod
    @pytest.mark.parametrize(
        ("raw_name", "normed_name"),
        [
            ("100 ין יפני", "ין יפני"),
            ("ין יפני 100", "ין יפני"),
            (" ין יפני 100 ", "ין יפני 100"),
            ("דולר", "דולר"),
            ("1 דולר", "1 דולר"),
            (" 100 דולר", "100 דולר"),
            ("100 דולר", "דולר"),
        ],
    )
    def test_remove_100(raw_name: str, normed_name: str) -> None:
        # pylint: disable=protected-access
        assert JPYNormalizer._remove_100(raw_name) == normed_name

    @staticmethod
    def test_norm(jpy_df: pd.DataFrame, normed_jpy_df: pd.DataFrame) -> None:
        assert JPYNormalizer(jpy_df).norm().equals(normed_jpy_df), (
            "The normalized `jpy_df` is different than expected"
        )
