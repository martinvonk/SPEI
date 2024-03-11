import logging
from typing import Optional, Tuple, Union

from numpy import ceil, isnan, linspace, nan, std
from pandas import DataFrame, DatetimeIndex, Grouper, Series, Timedelta
from scipy.stats import kstest, norm

from ._typing import ContinuousDist, NDArrayFloat
from .utils import (
    daily_window_groupby_yearly_df,
    get_data_series,
    group_yearly_df,
    infer_frequency,
    validate_index,
    validate_series,
)


def compute_si_ppf(
    series: Series,
    dist: ContinuousDist,
    prob_zero: bool,
    freq: Optional[str] = None,
    window: int = 0,
) -> Series:
    """Internal helper function to calculate drought index

    Parameters
    ----------
    series : Series
        Series with observations
    dist : ContinuousDist
        Continuous distribution from the SciPy library
    index : DatetimeIndex, optional
        DatetimeIndex with the date of the observations
    prob_zero : bool, optional
        Apply logic to observations that have value zero and calculate their
        probability seperately, by default False

    Returns
    -------
    Series
        Series with probability point function, ppf
    """

    series = validate_series(series)
    index = validate_index(series.index)
    series = series.reindex(index, copy=True)

    if freq is None:
        freq = infer_frequency(index)

    dfval = group_yearly_df(series=series)

    if window > 0:
        si = compute_ppf_rolling_window(
            dfval=dfval,
            index=index,
            dist=dist,
            prob_zero=prob_zero,
            freq=freq,
            window=window,
        )
    else:
        si = compute_ppf_groupby_freq(
            dfval=dfval, index=index, dist=dist, prob_zero=prob_zero, freq=freq
        )
    return si


def compute_ppf_groupby_freq(
    dfval: DataFrame,
    index: DatetimeIndex,
    dist: ContinuousDist,
    prob_zero: bool,
    freq: str,
) -> Series:
    logging.info("Using rolling groupby frequency method")
    si = Series(nan, index=index, dtype=float)  # type: Series
    for _, grval in dfval.groupby(Grouper(freq=freq)):
        data = get_data_series(grval)
        if prob_zero:
            p0 = (data == 0.0).sum() / len(data)
            pars, loc, scale = fit_dist(data=data[data != 0.0], dist=dist)
            cdf_sub = compute_cdf(data=data, dist=dist, loc=loc, scale=scale, pars=pars)
            cdf = p0 + (1 - p0) * cdf_sub
            cdf[data == 0.0] = p0
        else:
            pars, loc, scale = fit_dist(data=data, dist=dist)
            cdf = compute_cdf(data=data, dist=dist, loc=loc, scale=scale, pars=pars)
        ppf = norm.ppf(cdf)
        si.loc[data.index] = ppf
    return si


def compute_ppf_rolling_window(
    dfval: DataFrame,
    index: DatetimeIndex,
    dist: ContinuousDist,
    prob_zero: bool,
    freq: str,
    window: int,
) -> Series:

    if freq not in ("d", "w", "D", "W"):  # TODO: 14D etc. should also work.
        raise ValueError(
            f"Frequency freq must be 'D' or 'W', not '{freq}', if a window is provided."
        )
    logging.info("Using rolling window method")

    if window < 3:
        logging.error("Window should be larger than 2. Setting the window value to 3.")
        window = 3  # make sure window is at least three (value itself plus one to the left and right)
    elif window % 2 == 0:
        logging.error(f"Window should be odd. Setting the window value to {window + 1}")
        window += 1  # make sure window is odd

    period = int(ceil(window / 2))
    if freq in ("W", "w"):
        period = Timedelta(value=period, unit="W").days
        window = period * 2 + 1

    si = Series(nan, index=index, dtype=float)  # type: Series
    dfval_window = daily_window_groupby_yearly_df(dfval=dfval, period=period)
    for dfval_rwindow in dfval_window.rolling(
        window=window, min_periods=window, closed="right"
    ):
        if len(dfval_rwindow) < window:
            continue  # min_periods ignored by Rolling.__iter__
        data_window = dfval_rwindow.values.ravel()
        data_window = data_window[~isnan(data_window)]
        if prob_zero:
            p0 = (data_window == 0.0).sum() / len(data_window)
            pars, loc, scale = fit_dist(data=data_window[data_window != 0.0], dist=dist)
            data = get_data_series(dfval_rwindow.iloc[[period]])
            cdf_sub = compute_cdf(
                data=data.values.astype(float),
                dist=dist,
                loc=loc,
                scale=scale,
                pars=pars,
            )
            cdf = p0 + (1 - p0) * cdf_sub
            cdf[data == 0.0] = p0
        else:
            pars, loc, scale = si.si.fit_dist(data=data_window, dist=dist)
            data = get_data_series(dfval_rwindow.iloc[[period]])
            cdf = si.si.compute_cdf(
                data=data.values.astype(float),
                dist=dist,
                loc=loc,
                scale=scale,
                pars=pars,
            )
        ppf = norm.ppf(cdf)
        si.loc[data.index] = ppf
    return si


def fit_dist(data: Union[Series, NDArrayFloat], dist: ContinuousDist) -> Tuple:
    """Fit a Scipy Continuous Distribution"""
    fit_tuple = dist.fit(data, scale=std(data))
    if len(fit_tuple) == 2:
        loc, scale = fit_tuple
        pars = None
    else:
        *pars, loc, scale = fit_tuple
    return pars, loc, scale


def compute_cdf(
    data: Union[Series, NDArrayFloat],
    dist: ContinuousDist,
    loc: float,
    scale: float,
    pars: Optional[Tuple[float]] = None,
) -> NDArrayFloat:
    """Compute cumulative density function of a Scipy Continuous Distribution"""
    if pars is not None:
        cdf = dist.cdf(data, pars, loc=loc, scale=scale)
    else:
        cdf = dist.cdf(data, loc=loc, scale=scale)
    return cdf


def compute_cdf_nsf(data: Union[Series, NDArrayFloat]) -> NDArrayFloat:
    """Compute cumulative density function using the Normal Scores Transform"""
    n = data.size
    cdf = linspace(1 / (2 * n), 1 - 1 / (2 * n), n)
    return cdf


def fit_test(
    series: Union[Series, NDArrayFloat],
    dist: ContinuousDist,
    alpha: float = 0.05,
) -> Tuple[str, float, bool, tuple]:
    """Fit a distribution and perform the two-sided
    Kolmogorov-Smirnov test for goodness of fit. The
    null hypothesis is that the data and distributions
    are identical, the alternative is that they are
    not identical. [scipy_2021]_

    Parameters
    ----------
    data : Union[Series, NDArray[float]]
        pandas Series or numpy array of floats of observations of random
        variables
    dist: scipy.stats.rv_continuous
        Can be any continuous distribution from the
        scipy.stats library.
    alpha : float, optional
        Significance level for testing, default is 0.05
        which is equal to a a confidence level of 95%;
        that is, the null hypothesis will be rejected in
        favor of the alternative if the p-value is
        less than 0.05.

    Returns
    -------
    string, float, bool, tuple
        distribution name, p-value and fitted parameters

    References
    -------
    .. [scipy_2021] Onnen, H.: Intro to Probability
     Distributions and Distribution Fitting with Pythons
    SciPy, 2021.
    """
    fitted = dist.fit(series, scale=std(series))
    dist_name = getattr(dist, "name")
    ks = kstest(rvs=series, cdf=dist_name, args=fitted)[1]
    rej_h0 = ks < alpha
    return dist_name, ks, rej_h0, fitted
