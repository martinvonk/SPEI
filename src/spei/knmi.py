import numpy as np
import pandas as pd

from .utils import group_yearly_df


def get_yearly_temp_date(temp: pd.Series, threshold: float) -> pd.Series:
    """Get the first date of the temperature data."""
    temp_group_df = group_yearly_df(series=temp).cumsum(axis=0)
    first_date_above_threshold = temp_group_df.gt(threshold).idxmax()
    return first_date_above_threshold


def cumsum(deficit: pd.Series, allow_below_zero: bool = True) -> pd.Series:
    """Get the cumulative sum of the deficit."""
    if allow_below_zero:
        return deficit.cumsum()
    else:
        sumlm = np.frompyfunc(lambda a, b: 0.0 if a + b < 0.0 else a + b, nin=2, nout=1)
        return pd.Series(sumlm.accumulate(deficit.values), deficit.index, dtype=float)


def get_cumulative_deficit(
    deficit: pd.Series,
    startdate: pd.Timestamp | pd.Series,
    enddate: pd.Timestamp | pd.Series,
    allow_below_zero: bool = True,
) -> pd.DataFrame:
    """Get the cumulative deficit from startdate to enddate."""
    group_df = group_yearly_df(series=deficit)
    if isinstance(startdate, pd.Timestamp):
        if startdate.year != 2000:
            startdate = startdate.replace(year=2000)
        startdate = pd.Series(startdate, index=group_df.columns)
    if isinstance(enddate, pd.Timestamp):
        if enddate.year != 2000:
            enddate = enddate.replace(year=2000)
        enddate = pd.Series(enddate, index=group_df.columns)

    index = pd.date_range(start=startdate.min(), end=enddate.max(), freq="D")
    cumdf = pd.DataFrame(np.nan, index=index, columns=group_df.columns)
    for col in group_df.columns:
        start = startdate[col]
        end = enddate[col]
        cumdf.loc[start:end, col] = cumsum(
            group_df.loc[start:end, col],
            allow_below_zero=allow_below_zero,
        ).values

    return cumdf


def deficit_oct1(deficit: pd.Series) -> pd.Series:
    """Get the deficit on October 1st."""
    startdate = pd.Timestamp("2000-04-01")
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit,
        startdate=startdate,
        enddate=enddate,
        allow_below_zero=False,
    )
    doct1 = pd.Series(
        data=cumdf.loc[enddate].values,
        index=cumdf.columns,
        dtype=float,
        name="Doct1",
    )
    return doct1


def deficit_max(deficit: pd.Series) -> pd.Series:
    """Get the maximum deficit from april first onward."""
    startdate = pd.Timestamp("2000-04-01")
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit,
        startdate=startdate,
        enddate=enddate,
        allow_below_zero=False,
    )
    return cumdf.max().rename("Dmax")


def deficit_apr1(deficit: pd.Series) -> pd.Series:
    """Get the max deficit change."""
    startdate = pd.Timestamp("2000-04-01")
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit,
        startdate=startdate,
        enddate=enddate,
        allow_below_zero=True,
    )
    return (cumdf.max() - cumdf.min()).rename("DIapr1")


def deficit_gdd(
    deficit: pd.Series, temp: pd.Series, threshold: float = 440.0
) -> pd.Series:
    """Get the deficit from the first day above 440 growing degree days."""
    startdate = get_yearly_temp_date(temp=temp, threshold=threshold)
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit,
        startdate=startdate,
        enddate=enddate,
        allow_below_zero=True,
    )
    return cumdf.max().rename("DIgdd")


def deficit_wet(deficit: pd.Series) -> pd.Series:
    """Get the max from januari first onward deficit."""
    startdate = pd.Timestamp("2000-01-01")
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit,
        startdate=startdate,
        enddate=enddate,
        allow_below_zero=True,
    )
    return cumdf.max().rename("DIwet")
