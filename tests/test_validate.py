import pytest
import logging
from pandas import DataFrame, Series, to_datetime

from spei.utils import validate_index, validate_series


def test_validate_index(caplog) -> None:
    caplog.set_level(logging.INFO)
    series = Series([1, 2, 3], index=["2018", "2019", "2020"])
    validate_index(series.index)
    msg = (
        f"Expected the index to be a DatetimeIndex. Automatically converted "
        f"{type(series.index)} using pd.to_datetime(Index)\n"
    )
    print(f"{caplog.text=}")
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
