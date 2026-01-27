import numpy as np
import pandas as pd

from .utils import group_yearly_df, validate_series


def get_yearly_temp_date(temp: pd.Series, threshold: float) -> pd.Series:
    """
    Get the first date in each year where the cumulative temperature exceeds a given threshold.

    Parameters
    ----------
    temp : pd.Series
        A pandas Series representing the temperature time series, indexed by date.
    threshold : float
        The temperature threshold to identify the first date above it.

    Returns
    -------
    pd.Series
        A pandas Series containing the first date in each year where the cumulative
        temperature exceeds the threshold. The index corresponds to the years.
    """
    temp_group_df = group_yearly_df(series=temp).cumsum(axis=0)
    first_date_above_threshold = temp_group_df.gt(threshold).idxmax()
    return first_date_above_threshold


def cumsum(deficit: pd.Series, allow_below_zero: bool = True) -> pd.Series:
    """
    Calculate the cumulative sum of a deficit series.

    Parameters:
    -----------
    deficit : pd.Series
        A pandas Series representing the deficit values.
    allow_below_zero : bool, optional
        If True, the cumulative sum is calculated as-is, allowing negative values.
        If False, the cumulative sum is constrained to be non-negative, resetting
        to zero whenever the sum would drop below zero. Default is True.

    Returns:
    --------
    pd.Series
        A pandas Series containing the cumulative sum of the deficit values,
        optionally constrained to be non-negative.
    """
    if allow_below_zero:
        return deficit.cumsum()
    else:
        if deficit.to_numpy(float)[0] < 0.0:
            deficit.iat[0] = 0.0
        sumlm = np.frompyfunc(lambda a, b: 0.0 if a + b < 0.0 else a + b, nin=2, nout=1)
        return pd.Series(sumlm.accumulate(deficit.values), deficit.index, dtype=float)


def get_cumulative_deficit(
    deficit: pd.Series,
    startdate: pd.Timestamp | pd.Series,
    enddate: pd.Timestamp | pd.Series,
    allow_below_zero: bool = True,
) -> pd.DataFrame:
    """
    Calculate the cumulative deficit for a given time period.

    This function computes the cumulative deficit for each column in a
    grouped yearly DataFrame, starting from `startdate` to `enddate`.
    The cumulative sum can optionally allow values below zero.

    Parameters:
    -----------
    deficit : pd.Series
        A pandas Series representing the deficit time series.
    startdate : pd.Timestamp | pd.Series
        The start date(s) for the cumulative deficit calculation. If a
        single timestamp is provided, it is applied to all columns. If
        a Series is provided, it should align with the columns of the
        grouped DataFrame.
    enddate : pd.Timestamp | pd.Series
        The end date(s) for the cumulative deficit calculation. Similar
        to `startdate`, it can be a single timestamp or a Series aligned
        with the columns.
    allow_below_zero : bool, optional
        If True, allows the cumulative sum to include values below zero.
        Defaults to True.

    Returns:
    --------
    pd.DataFrame
        A DataFrame containing the cumulative deficit for each column
        over the specified time period. The index represents the date
        range, and the columns correspond to the year.
    """
    deficit = validate_series(deficit)
    group_df = group_yearly_df(series=deficit)
    if isinstance(startdate, pd.Timestamp):
        if startdate.year != 2000:
            # year is replaced since group_yearly_df returns a df with 2000 as a base year
            startdate = startdate.replace(year=2000)
        startdate = pd.Series(startdate, index=group_df.columns)
    if isinstance(enddate, pd.Timestamp):
        if enddate.year != 2000:
            # year is replaced since group_yearly_df returns a df with 2000 as a base year
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
    """
    Calculate the cumulative deficit on October 1st.

    This function computes the cumulative deficit for a given time series
    of deficits, considering only the period between April 1st and
    September 30th. The cumulative deficit is reset to zero if it goes
    below zero during this period.

    Parameters:
    -----------
    deficit : pd.Series
        A pandas Series representing the deficit time series. The index
        should be datetime-like, and the values should represent the
        deficit amounts.

    Returns:
    --------
    pd.Series
        A pandas Series containing the cumulative deficit values on
        October 1st. The index of the returned Series corresponds to
        the columns of the cumulative deficit DataFrame, and the name
        of the Series is "Doct1".
    """
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
    """
    Calculate the maximum cumulative deficit within a specified period.

    This function computes the maximum cumulative deficit for a given
    deficit time series, starting from April 1st to September 30th.
    The cumulative deficit is calculated using the `get_cumulative_deficit`
    function, ensuring that values below zero are not allowed.

    Parameters:
    -----------
    deficit : pd.Series
        A pandas Series representing the deficit values over time.

    Returns:
    --------
    pd.Series
        A pandas Series containing the maximum cumulative deficit
        within the specified period, labeled as "Dmax".
    """
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
    """
    Calculate the maximum change in cumulative deficit within a specified date range.

    This function computes the cumulative deficit for the given deficit series
    between April 1st and September 30th of the year 2000. It then calculates
    the maximum change in the cumulative deficit over this period.

    Parameters
    ----------
    deficit : pd.Series
        A pandas Series representing the deficit values. The index is expected
        to be datetime-like.

    Returns
    -------
    pd.Series
        A pandas Series containing the maximum change in cumulative deficit
        over the specified period, labeled as "DIapr1".
    """
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
    """
    Calculate the maximum change in cumulative deficit starting from the
    first day when the temperature sum (growing degree days; GDD)
    exceeds a specified threshold.

    Parameters:
    -----------
    deficit : pd.Series
        A pandas Series representing the daily deficit values.
    temp : pd.Series
        A pandas Series representing the daily temperature values.
    threshold : float, optional
        The temperature sum GDD threshold to determine the starting date for the calculation.
        Defaults to 440.0.

    Returns:
    --------
    pd.Series
        A pandas Series containing the maximum change in cumulative deficit,
        labeled as "DIgdd".
    """
    temp = validate_series(temp)
    startdate = get_yearly_temp_date(temp=temp, threshold=threshold)
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit,
        startdate=startdate,
        enddate=enddate,
        allow_below_zero=True,
    )
    return (cumdf.max() - cumdf.min()).rename("DIapr1").rename("DIgdd")


def deficit_wet(deficit: pd.Series) -> pd.Series:
    """
    Calculate the maximum change in cumulative deficit for a specified period.

    This function computes the maximum change in  cumulative deficit from
    January 1st to September 30th of a given year. The cumulative deficit
    is calculated using the `get_cumulative_deficit` function, allowing
    values below zero.

    Parameters:
    -----------
    deficit : pd.Series
        A pandas Series representing the deficit values over time.

    Returns:
    --------
    pd.Series
        A pandas Series containing the maximum change in cumulative deficit
        for the specified period, labeled as "DIwet".
    """
    startdate = pd.Timestamp("2000-01-01")
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit,
        startdate=startdate,
        enddate=enddate,
        allow_below_zero=True,
    )
    return (cumdf.max() - cumdf.min()).rename("DIapr1").rename("DIwet")
