import logging

import pytest
from pandas import DataFrame, DatetimeIndex, Index, Series, Timestamp, to_datetime
from spei.utils import infer_frequency, validate_index, validate_series


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


def test_infer_frequency_monthly():
    index = DatetimeIndex(["2020-01-01", "2020-02-01", "2020-03-01"])
    assert infer_frequency(index) == "M"


def test_infer_frequency_weekly():
    index = DatetimeIndex(["2020-01-01", "2020-01-08", "2020-01-15"])
    assert infer_frequency(index) == "W"


def test_infer_frequency_daily():
    index = DatetimeIndex(["2020-01-01", "2020-01-02", "2020-01-03"])
    assert infer_frequency(index) == "D"


def test_infer_frequency_no_infer():
    index = DatetimeIndex(["2020-01-01", "2020-01-03", "2020-01-07"])
    assert infer_frequency(index) == "ME"  # Assuming pandas version >= 2.2.0


def test_infer_frequency_non_datetime_index():
    index = Index(["2020-01-01", "2020-02-01", "2020-03-01"])
    assert infer_frequency(index) == "M"


def test_infer_frequency_invalid_index():
    index = Index(["a", "b", "c"])
    with pytest.raises(ValueError):
        infer_frequency(index)
