import pytest
from pandas import DataFrame, Series, to_datetime

from spei.utils import validate_index, validate_series


def test_validate_index(capfd) -> None:
    series = Series([1, 2, 3], index=[1, 2, 3])
    validate_index(series.index)
    index = series.index
    msg = (
        f"Expected the index to be a DatetimeIndex. Automatically converted"
        f"{type(index)} using pd.to_datetime(Index)\n"
    )
    out, _ = capfd.readouterr()
    assert out == msg


def test_validate_series() -> None:
    with pytest.raises(TypeError):
        validate_series([1, 2, 3])


def test_validate_series_df_1d(capfd) -> None:
    df = DataFrame({"s": [1, 2, 3]}, index=to_datetime([1, 2, 3]))
    validate_series(df)
    msg = (
        "Please convert series of type pandas.DataFrame to a"
        "pandas.Series using DataFrame.squeeze(). Now done automatically.\n"
    )
    out, _ = capfd.readouterr()
    assert out == msg


def test_validate_series_df_2d() -> None:
    with pytest.raises(TypeError):
        df = DataFrame({"s1": [1, 2, 3], "s2": [1, 2, 3]}, index=to_datetime([1, 2, 3]))
        validate_series(df)
