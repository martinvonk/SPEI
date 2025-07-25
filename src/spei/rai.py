import numpy as np
import pandas as pd

from .utils import get_data_series, group_yearly_df, validate_series


def rai(series: pd.Series) -> pd.Series:
    """
    Calculate the Rainfall Anomaly Index (RAI) for a given time
    series of precipitation data.

    Parameters
    ----------
    series : pd.Series
        A pandas Series containing precipitation data.

    Returns
    -------
    pd.Series
        A pandas Series containing the RAI values.

    References
    ----------
    van Rooy, M.P. A Rainfall Anomaly Index Independent of Time and Space. Notos. 1965.
    """
    series = validate_series(series)
    pm = series.mean()
    pi_above = series > pm
    rai = pd.Series(np.nan, index=series.index, dtype=float)
    rai[pi_above] = 3.0 * (series[pi_above] - pm) / (series.nlargest(10).mean() - pm)
    rai[~pi_above] = (
        -3.0 * (series[~pi_above] - pm) / (series.nsmallest(10).mean() - pm)
    )
    return rai


def mrai(series: pd.Series, sf: float = 1.7) -> pd.Series:
    """Calculate the Modified Rainfall Anomaly Index (MRAI)
    for a given time series of precipitation data.

    Parameters
    ----------
    series : pd.Series
        A pandas Series containing precipitation data.
    sf : float
        Scaling factor for the MRAI calculation. Default is 1.7.

    Returns
    -------
    pd.Series
        A pandas Series containing the MRAI values.

    References
    ----------
    Hänsel, S., Schucknecht, A. and Matschullat J. The Modified Rainfall
    Anomaly Index (mRAI) — is this an alternative to the Standardised
    Precipitation Index (SPI) in evaluating future extreme precipitation
    characteristics? Theoretical and Applied Climatology. 2015.
    """
    series = validate_series(series)
    mrai = pd.Series(np.nan, index=series.index, dtype=float)
    group_df = group_yearly_df(series=series)
    for _, gr in group_df.groupby(pd.Grouper(freq="MS")):
        gr_series = get_data_series(gr)
        pm = gr_series.mean()
        pi_above = gr_series > pm
        e_above = gr_series[gr_series > gr_series.quantile(0.9)].mean()
        e_below = gr_series[gr_series < gr_series.quantile(0.1)].mean()
        mrai_gr = pd.Series(np.nan, index=gr_series.index, dtype=float)
        mrai_gr[pi_above] = sf * (gr_series[pi_above] - pm) / (e_above - pm)
        mrai_gr[~pi_above] = -sf * (gr_series[~pi_above] - pm) / (e_below - pm)
        mrai.loc[mrai_gr.index] = mrai_gr.values

    return mrai
