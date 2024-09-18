import logging
from calendar import isleap
from typing import Union

from numpy import array, nan
from pandas import (
    DataFrame,
    DatetimeIndex,
    Grouper,
    Index,
    Series,
    Timedelta,
    concat,
    infer_freq,
    to_datetime,
)
from pandas import __version__ as pd_version


def validate_series(series: Series) -> Series:
    series = series.copy()

    if not isinstance(series, Series):
        if isinstance(series, DataFrame):
            if len(series.columns) == 1:
                logging.warning(
                    "Please convert series of type pandas.DataFrame to a"
                    "pandas.Series using DataFrame.squeeze(). Now done automatically."
                )
                series = series.squeeze()
            else:
                raise TypeError(
                    "Please provide a pandas.Series instead of a pandas.DataFrame"
                )
        else:
            raise TypeError(f"Please provide a Pandas Series instead of {type(series)}")

    index = validate_index(series.index)

    return series.reindex(index, copy=True)


def validate_index(index: Index) -> DatetimeIndex:
    index = index.copy()

    if not isinstance(index, DatetimeIndex):
        logging.info(
            f"Expected the index to be a DatetimeIndex. Automatically converted "
            f"{type(index)} using pd.to_datetime(Index)"
        )
        index = DatetimeIndex(to_datetime(index))

    if index.has_duplicates:
        msg = (
            "Duplicated indices found. Please remove them. For instance by"
            " using `series = "
            "series.loc[~series.index.duplicated(keep='first/last')]`"
        )
        logging.error(msg)
        raise ValueError(msg)

    return index


def infer_frequency(index: Union[Index, DatetimeIndex]) -> str:
    """Infer frequency"""

    index = validate_index(index)

    inf_freq = infer_freq(index)

    if inf_freq is None:
        logging.info(
            "Could not infer frequency from index, using monthly frequency instead"
        )
        inf_freq = "ME" if pd_version >= "2.2.0" else "M"
    else:
        logging.info(f"Inferred frequency '{inf_freq}' from index")

    if "W-" in inf_freq:
        logging.info(f"Converted frequncy weekly '{inf_freq}' to 'W'")
        inf_freq = "W"

    return inf_freq


def group_yearly_df(series: Series) -> DataFrame:
    """Group series in a DataFrame with date (in the year 2000) as index and
    year as columns.
    """
    strfstr: str = "%m-%d %H:%M:%S"
    grs = {}
    freq = "YE" if pd_version >= "2.2.0" else "Y"
    for year_timestamp, gry in series.groupby(Grouper(freq=freq)):
        index = validate_index(gry.index)
        gry.index = to_datetime(
            "2000-" + index.strftime(strfstr), format="%Y-" + strfstr
        )
        year = getattr(year_timestamp, "year")  # type: str
        grs[year] = gry
    return concat(grs, axis=1)


def get_data_series(group_df: DataFrame) -> Series:
    """Transform grouped dataframe by yearly values back to time series."""
    strfstr: str = "%m-%d %H:%M:%S"
    index = validate_index(group_df.index)
    idx = array(
        [(f"{col}-" + index.strftime(strfstr)).tolist() for col in group_df.columns]
    ).flatten()
    # remove illegal 29 febraury for non leap years created by group_yearly_df
    boolidx = ~array(
        [
            (x.split(" ")[0].split("-", 1)[1] == "02-29")
            and not isleap(int(x.split(" ")[0].split("-")[0]))
            for x in idx
        ]
    )

    dt_idx = to_datetime(idx[boolidx], format="%Y-" + strfstr)
    values = group_df.transpose().values.flatten()[boolidx]
    return Series(values, index=dt_idx, dtype=float).dropna()


def daily_window_group_yearly_df(dfval: DataFrame, period: int) -> DataFrame:
    """Fill a period of daily values in grouped by yearly DataFrame to get
    cyclic rolling window.
    """
    dfval_window_index_start = [
        dfval.index[0] + Timedelta(value=-i, unit="D")
        for i in reversed(range(1, period + 1))
    ]
    dfval_window_index_end = [
        dfval.index[-1] + Timedelta(value=i, unit="D") for i in range(1, period + 1)
    ]
    dfval_window_index = DatetimeIndex(
        dfval_window_index_start + dfval.index.to_list() + dfval_window_index_end
    )

    dfval_window = DataFrame(
        nan, index=dfval_window_index, columns=dfval.columns, dtype=float
    )
    dfval_window.loc[dfval.index, dfval.columns] = dfval.values
    dfval_window.iloc[:period] = dfval.iloc[-period:].values
    dfval_window.iloc[-period:] = dfval.iloc[:period].values
    return dfval_window
