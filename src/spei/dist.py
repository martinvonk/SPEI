import logging
from dataclasses import dataclass, field
from typing import Any, List, Literal, Optional, Tuple

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
    prob_zero: bool = False,
    freq: Optional[str] = None,
    window: int = 0,
    nsf: bool = False,
) -> Series:
    """Internal helper function to calculate propability point function of normal
    distribution based on a cumulative density function of a fitted
    distribution

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
    window : int, optional
        If a window is supplied, all data within the window is fitted for the
        cumulative density function so a bitter fit can be ensured. Frequency
        of the data must constant like 'D' or 'W'.
    nsf : bool, optional
        Use the normal scores transform to calculat the cumulative density
        function

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

    if window > 0:
        cdf = compute_cdf_rolling_window(
            series=series,
            dist=dist,
            prob_zero=prob_zero,
            freq=freq,
            window=window,
        )
    elif nsf:
        cdf = compute_cdf_nsf(series=series, freq=freq)
    else:
        cdf = compute_cdf_groupby_freq(
            series=series,
            dist=dist,
            prob_zero=prob_zero,
            freq=freq,
        )
    return Series(norm.ppf(cdf.values, loc=0, scale=1), index=index, dtype=float)


def compute_cdf_groupby_freq(
    series: Series,
    dist: ContinuousDist,
    prob_zero: bool,
    freq: str,
) -> Series:
    logging.info("Using rolling groupby frequency method")
    dfval = group_yearly_df(series=series)
    cdf_series = Series(nan, index=series.index, dtype=float)
    for _, grval in dfval.groupby(Grouper(freq=freq)):
        data = get_data_series(grval)
        fd = FittedDist(data=data, dist=dist, prob_zero=prob_zero)
        cdf = fd.cdf()
        cdf_series.loc[cdf.index] = cdf.values
    return cdf_series


def compute_cdf_rolling_window(
    series: Series,
    dist: ContinuousDist,
    prob_zero: bool,
    freq: str,
    window: int,
) -> Series:

    if freq not in ("d", "w", "D", "W"):  # TODO: ideally 14D should also work.
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

    dfval = group_yearly_df(series=series)
    cdf_series = Series(nan, index=series.index, dtype=float)
    dfval_window = daily_window_groupby_yearly_df(dfval=dfval, period=period)
    for dfval_rwindow in dfval_window.rolling(
        window=window, min_periods=window, closed="right"
    ):
        if len(dfval_rwindow) < window:
            continue  # min_periods ignored by Rolling.__iter__
        data = get_data_series(dfval_rwindow.iloc[[period]])
        data_window = get_data_series(dfval_rwindow)
        fd = FittedDist(
            data=data, dist=dist, prob_zero=prob_zero, data_window=data_window
        )
        cdf = fd.cdf()
        cdf_series.loc[cdf.index] = cdf.values
    return cdf_series


def compute_cdf_nsf(
    series: Series,
    freq: str,
):
    """Compute cumulative density function using the Normal Scores Transform"""
    logging.info("Using the normal scores transform")
    dfval = group_yearly_df(series=series)
    cdf_series = Series(nan, index=series.index, dtype=float)
    for _, grval in dfval.groupby(Grouper(freq=freq)):
        data = get_data_series(grval).sort_values()
        n = len(data)
        cdf_series.loc[data.index] = linspace(1 / (2 * n), 1 - 1 / (2 * n), n)
    return cdf_series


@dataclass
class FittedDist:
    data: Series = field(init=True, repr=False)
    dist: ContinuousDist
    loc: float = field(init=False, repr=True)
    scale: float = field(init=False, repr=True)
    pars: Optional[List[float]] = field(init=False, repr=False)
    prob_zero: bool = field(default=False, init=True, repr=False)
    p0: float = field(default=0.0, init=False, repr=False)
    data_window: Optional[Series] = field(default=None, init=True, repr=False)

    def __post_init__(self):
        data_fit = self.data_window if self.data_window is not None else self.data
        pars, loc, scale = self.fit_dist(data=data_fit, dist=self.dist)
        self.loc = loc
        self.scale = scale
        self.pars = pars

        if self.prob_zero:
            self.p0 = (data_fit == 0.0).sum() / len(data_fit)

    @staticmethod
    def fit_dist(data: Series, dist: ContinuousDist) -> Tuple:
        """Fit a Scipy Continuous Distribution"""
        fit_tuple = dist.fit(data, scale=std(data))
        if len(fit_tuple) == 2:
            loc, scale = fit_tuple
            pars = None
        else:
            *pars, loc, scale = fit_tuple
        return pars, loc, scale

    def cdf(self) -> Series:
        """Compute cumulative density function of a Scipy Continuous Distribution"""
        if self.pars is not None:
            cdf = self.dist.cdf(
                self.data.values, self.pars, loc=self.loc, scale=self.scale
            )
        else:
            cdf = self.dist.cdf(self.data.values, loc=self.loc, scale=self.scale)

        if self.prob_zero:
            cdf = self.p0 + (1 - self.p0) * cdf
            cdf[self.data == 0.0] = self.p0

        return Series(cdf, index=self.data.index, dtype=float)

    def ks_test(
        self,
        alternative: Literal["two-sided", "less", "greater"] = "two-sided",
    ) -> float:
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
        alternative: Literal["two-sided", "less", "greater"], optional
            Defines the null and alternative hypotheses. Default is 'two-sided'.

        Returns
        -------
        float
            p-value

        References
        -------
        .. [scipy_2021] Onnen, H.: Intro to Probability
        Distributions and Distribution Fitting with Pythons
        SciPy, 2021.
        """
        args = (
            (self.pars, self.loc, self.scale)
            if self.pars is not None
            else (self.loc, self.scale)
        )  # type: Any
        kstest_result = kstest(
            rvs=self.data, cdf=self.dist.name, args=args, alternative=alternative
        )
        # rej_h0 = kstest_result.pvalue < alpha
        return kstest_result.pvalue
