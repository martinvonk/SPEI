import logging

import pytest
from pandas import DataFrame, DatetimeIndex, Series, Timestamp, to_datetime

from spei.utils import validate_index, validate_series


def test_validate_index(caplog) -> None:
    caplog.set_level(logging.INFO)
    series = Series([1.0, 2.0, 3.0], index=["2018", "2019", "2020"])
    validate_index(series.index)
    msg = (
        f"Expected the index to be a DatetimeIndex. Automatically converted "
        f"{type(series.index)} using pd.to_datetime(Index)\n"
    )
    assert msg in caplog.text


def test_validate_index_duplicated(caplog) -> None:
    caplog.set_level(logging.ERROR)
    series = Series(
        [1.0, 1.0],
        index=DatetimeIndex([Timestamp("2000-01-01"), Timestamp("2000-01-01")]),
    )
    with pytest.raises(ValueError):
        validate_index(series.index)
        msg = (
            "Duplicated indices found. Please remove them. For instance by using"
            "`series = series.loc[~series.index.duplicated(keep='first/last')]`"
        )
        assert msg in caplog.text


def test_validate_series() -> None:
    with pytest.raises(TypeError):
        validate_series([1, 2, 3])


def test_validate_series_df_1d(caplog) -> None:
    df = DataFrame({"s": [1, 2, 3]}, index=to_datetime([1, 2, 3]))
    validate_series(df)
    msg = (
        "Please convert series of type pandas.DataFrame to a"
        "pandas.Series using DataFrame.squeeze(). Now done automatically.\n"
    )
    assert msg in caplog.text


def test_validate_series_df_2d() -> None:
    with pytest.raises(TypeError):
        df = DataFrame({"s1": [1, 2, 3], "s2": [1, 2, 3]}, index=to_datetime([1, 2, 3]))
        validate_series(df)
