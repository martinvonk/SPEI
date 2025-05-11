import numpy as np
import pandas as pd

from .utils import group_yearly_df


def get_yearly_temp_date(temp: pd.Series, threshold: float) -> pd.Timestamp:
    """Get the first date of the temperature data."""
    temp_group_df = group_yearly_df(series=temp).cumsum(axis=0)
    first_date_above_threshold = temp_group_df.gt(threshold).idxmax()
    return first_date_above_threshold


def get_cumulative_deficit(
    deficit: pd.Series,
    startdate: pd.Timestamp | pd.Series,
    enddate: pd.Timestamp | pd.Series,
) -> pd.DataFrame:
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
        cumdf.loc[start:end, col] = group_df.loc[start:end, col].cumsum().values

    return cumdf


def deficit_oct1(deficit: pd.Series) -> pd.Series:
    """Get the deficit on October 1st."""
    startdate = pd.Timestamp("2000-04-01")
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit, startdate=startdate, enddate=enddate
    )
    return cumdf.loc[enddate].rename("Doct1")


def deficit_max(deficit: pd.Series) -> pd.Series:
    """Get the maximum deficit from april first onward."""
    startdate = pd.Timestamp("2000-04-01")
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit, startdate=startdate, enddate=enddate
    )
    return cumdf.max().rename("Dmax")


def deficit_apr1(deficit: pd.Series) -> pd.Series:
    """Get the max deficit change."""
    startdate = pd.Timestamp("2000-04-01")
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit, startdate=startdate, enddate=enddate
    )
    return (cumdf.max() - cumdf.min()).rename("DIapr1")


def deficit_gdd(
    deficit: pd.Series, temp: pd.Series, threshold: float = 440.0
) -> pd.Series:
    """Get the deficit from the first day above 440 growing degree days."""
    startdate = get_yearly_temp_date(temp=temp, threshold=threshold)
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit, startdate=startdate, enddate=enddate
    )
    return cumdf.max().rename("DIgdd")


def deficit_wet(deficit: pd.Series) -> pd.Series:
    """Get the max from januari first onward deficit."""
    startdate = pd.Timestamp("2000-01-01")
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit, startdate=startdate, enddate=enddate
    )
    return cumdf.max().rename("DIwet")
