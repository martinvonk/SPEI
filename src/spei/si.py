import logging
from dataclasses import dataclass, field
from typing import Literal

from numpy import ceil, interp, linspace, nan
from pandas import DataFrame, Grouper, Series, Timedelta, Timestamp
from scipy.stats import beta, fisk, gamma, genextreme, norm

from ._typing import ContinuousDist
from .dist import Dist
from .utils import (
    daily_window_group_yearly_df,
    get_data_series,
    group_yearly_df,
    infer_frequency,
    validate_series,
)


def sgi(
    series: Series,
    timescale: int = 0,
    fit_freq: str | None = None,
) -> Series:
    """Method to compute the Standardized Groundwater Index. Uses
    the normal scores transform to calculate the cumulative density function.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the groundwater levels. Time series index
        should be a pandas DatetimeIndex.
    fit_freq : str, optional, default=None
        Frequency for fitting the distribution. Default is None in which case
        the frequency of the series is inferred. If this fails a monthly
        frequency is used.

    Returns
    -------
    pandas.Series

    References
    ----------
    Bloomfield, J. P. and Marchant, B. P.: Analysis of
    groundwater drought building on the standardised precipitation index
    approach. Hydrol. Earth Syst. Sci., 17, 4769-4787, 2013.
    """

    mock_dist = norm
    sgi = SI(
        series=series,
        dist=mock_dist,
        timescale=timescale,
        fit_freq=fit_freq,
        fit_window=0,
        fit_method="MLE",
        prob_zero=False,
        normal_scores_transform=True,
        agg_func="mean",
    )
    return sgi.norm_ppf()


def spi(
    series: Series,
    dist: ContinuousDist = gamma,
    timescale: int = 0,
    fit_freq: str | None = None,
    fit_window: int = 0,
    prob_zero: bool = True,
) -> Series:
    """Method to compute the Standardized Precipitation Index.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the precipitation. Time series index
        should be a pandas DatetimeIndex.
    dist: scipy.stats.rv_continuous
        Can be any continuous distribution from the scipy.stats library.
        However, for the SPI generally the Gamma probability density
        function is recommended. Other appropriate choices could be the
        lognormal, log-logistic (fisk) or PearsonIII distribution.
    timescale : int, optional, default=0
        Size of the moving window over which the series is summed. If zero, no
        summation is performed over the time series. If the time series
        frequency is daily, then one would provide timescale=30 for SI1,
        timescale=90 for SI3, timescale=180 for SI6 etc.
    fit_freq : str, optional, default=None
        Frequency for fitting the distribution. Default is None in which case
        the frequency of the series is inferred. If this fails a monthly
        frequency is used.
    fit_window : int, optional, default=0
        Window size for fitting data in fit_freq frequency's unit. Default is
        zero in which case only data within the fit_freq is considered. If
        larger than zero data data within the window is used to fit the
        distribution for the series. fit_window must be a odd number larger
        than 3 when used.
    prob_zero : bool, default=True
        Option to correct the distribution if x=0 is not in probability density
        function. E.g. the case with the Gamma distriubtion. If True, the
        probability of zero values in the series is calculated by the
        occurence.

    Returns
    -------
    pandas.Series

    References
    ----------
    LLoyd-Hughes, B. and Saunders, M.A.: A drought climatology for Europe.
    International Journal of Climatology, 22, 1571-1592, 2002.
    """

    spi = SI(
        series=series,
        dist=dist,
        timescale=timescale,
        fit_freq=fit_freq,
        fit_window=fit_window,
        fit_method="MLE",
        prob_zero=prob_zero,
        normal_scores_transform=False,
        agg_func="sum",
    )
    spi.fit_distribution()
    return spi.norm_ppf()


def spei(
    series: Series,
    dist: ContinuousDist = fisk,
    timescale: int = 0,
    fit_freq: str | None = None,
    fit_window: int = 0,
    prob_zero: bool = False,
) -> Series:
    """Method to compute the Standardized Precipitation Evaporation Index.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the precipitation. Time series index
        should be a pandas DatetimeIndex.
    dist: scipy.stats.rv_continuous
        Can be any continuous distribution from the scipy.stats library.
        However, for the SPEI generally the log-logistic (fisk) probability
        density function is recommended. Other appropriate choices could be
        the lognormal or PearsonIII distribution.
    timescale : int, optional, default=0
        Size of the moving window over which the series is summed. If zero, no
        summation is performed over the time series. If the time series
        frequency is daily, then one would provide timescale=30 for SI1,
        timescale=90 for SI3, timescale=180 for SI6 etc.
    fit_freq : str, optional, default=None
        Frequency for fitting the distribution. Default is None in which case
        the frequency of the series is inferred. If this fails a monthly
        frequency is used.
    fit_window : int, optional, default=0
        Window size for fitting data in fit_freq frequency's unit. Default is
        zero in which case only data within the fit_freq is considered. If
        larger than zero data data within the window is used to fit the
        distribution for the series. fit_window must be a odd number larger
        than 3 when used.
    prob_zero : bool, default=False
        Flag indicating whether the probability of zero values in the series is
        calculated by the occurence.

    Returns
    -------
    pandas.Series

    References
    ----------
    Vicente-Serrano S.M., Beguería S., López-Moreno J.I.:
    A Multi-scalar drought index sensitive to global warming:
    The Standardized Precipitation Evapotranspiration Index.
    Journal of Climate, 23, 1696-1718, 2010.
    """

    spei = SI(
        series=series,
        dist=dist,
        timescale=timescale,
        fit_freq=fit_freq,
        fit_window=fit_window,
        fit_method="MLE",
        prob_zero=prob_zero,
        normal_scores_transform=False,
        agg_func="sum",
    )
    spei.fit_distribution()
    return spei.norm_ppf()


def ssfi(
    series: Series,
    dist: ContinuousDist = genextreme,
    timescale: int = 0,
    fit_freq: str | None = None,
    fit_window: int = 0,
    prob_zero: bool = True,
) -> Series:
    """Method to compute the Standardized StreamFlow Index.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the precipitation. Time series index
        should be a pandas DatetimeIndex.
    dist: scipy.stats.rv_continuous
        Can be any continuous distribution from the scipy.stats library.
        However, for the SSFI generally the gamma probability density function
        is recommended. Other choices could be the normal, lognormal,
        pearsonIII, GEV or Gen-Logistic distribution or any distribution deemed
        appropriate.
    timescale : int, optional, default=0
        Size of the moving window over which the series is summed. If zero, no
        summation is performed over the time series. If the time series
        frequency is daily, then one would provide timescale=30 for SI1,
        timescale=90 for SI3, timescale=180 for SI6 etc.
    fit_freq : str, optional, default=None
        Frequency for fitting the distribution. Default is None in which case
        the frequency of the series is inferred. If this fails a monthly
        frequency is used.
    fit_window : int, optional, default=0
        Window size for fitting data in fit_freq frequency's unit. Default is
        zero in which case only data within the fit_freq is considered. If
        larger than zero data data within the window is used to fit the
        distribution for the series. fit_window must be a odd number larger
        than 3 when used.
    prob_zero : bool, default=False
        Flag indicating whether the probability of zero values in the series is
        calculated by the occurence.

    Returns
    -------
    pandas.Series

    References
    ----------
    Vicente-Serrano, S. M., J. I. López-Moreno, S. Beguería, J. Lorenzo-Lacruz,
    C. Azorin-Molina, and E. Morán-Tejeda. Accurate Computation of a Streamflow
    Drought Index. Journal of Hydrologic Engineering 17 (2): 318-332. 2012.
    """
    ssfi = SI(
        series=series,
        dist=dist,
        timescale=timescale,
        fit_freq=fit_freq,
        fit_window=fit_window,
        fit_method="MLE",
        prob_zero=prob_zero,
        normal_scores_transform=False,
        agg_func="mean",
    )
    ssfi.fit_distribution()
    return ssfi.norm_ppf()


def ssmi(
    series: Series,
    dist: ContinuousDist = beta,
    timescale: int = 0,
    fit_freq: str | None = None,
    fit_window: int = 0,
    prob_zero: bool = True,
) -> Series:
    """Method to compute the Standardized Soil Moisture Index.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the precipitation. Time series index
        should be a pandas DatetimeIndex.
    dist: scipy.stats.rv_continuous
        Can be any continuous distribution from the scipy.stats library.
        However, for the SSMI generally the beta probability density function
        is recommended. Other choices could be the normal or ECDF distribution
        or any distribution deemed appropriate.
    timescale : int, optional, default=0
        Size of the moving window over which the series is summed. If zero, no
        summation is performed over the time series. If the time series
        frequency is daily, then one would provide timescale=30 for SI1,
        timescale=90 for SI3, timescale=180 for SI6 etc.
    fit_freq : str, optional, default=None
        Frequency for fitting the distribution. Default is None in which case
        the frequency of the series is inferred. If this fails a monthly
        frequency is used.
    fit_window : int, optional, default=0
        Window size for fitting data in fit_freq frequency's unit. Default is
        zero in which case only data within the fit_freq is considered. If
        larger than zero data data within the window is used to fit the
        distribution for the series. fit_window must be a odd number larger
        than 3 when used.
    prob_zero : bool, default=False
        Flag indicating whether the probability of zero values in the series is
        calculated by the occurence.

    Returns
    -------
    pandas.Series

    References
    ----------
    Carrão. H., Russo, S., Sepulcre-Canto, G., Barbosa, P.: An empirical standardized
    soil moisture index for agricultural drought assessment from remotely sensed data.
    International Journal of Applied Earth Observation and Geoinformation, 48, 2016.
    """

    ssmi = SI(
        series=series,
        dist=dist,
        timescale=timescale,
        fit_freq=fit_freq,
        fit_window=fit_window,
        fit_method="MLE",
        prob_zero=prob_zero,
        normal_scores_transform=False,
        agg_func="mean",
    )
    ssmi.fit_distribution()
    return ssmi.norm_ppf()


@dataclass
class SI:
    """
    Standardized Index Class.

    Parameters
    ----------
    series : Series
        The input time series data.
    dist : ContinuousDist
        The SciPy continuous distribution associated with the data.
    timescale : int, optional, default=0
        Size of the moving window over which the series is summed. If zero, no
        summation is performed over the time series. If the time series
        frequency is daily, then one would provide timescale=30 for SI1,
        timescale=90 for SI3, timescale=180 for SI6 etc.
    fit_freq : str, optional, default=None
        Frequency for fitting the distribution. Default is None in which case
        the frequency of the series is inferred. If this fails a monthly
        frequency is used.
    fit_window : int, optional, default=0
        Window size for fitting data in fit_freq frequency's unit. Default is
        zero in which case only data within the fit_freq is considered. If
        larger than zero data data within the window is used to fit the
        distribution for the series. fit_window must be a odd number larger
        than 3 when used.
    fit_method : Literal["MLE", "MM"], default="MLE"
        The method used for fitting the distribution. The default is "MLE"
        (Maximum Likelihood Estimate); "MM" (Method of Moments) is also available.
    prob_zero : bool, default=False
        Flag indicating whether the probability of zero values in the series is
        calculated by the occurence.
    normal_scores_transform : bool, default=False
        Flag to use the normal scores transformation for calculating the
        cumulative density function.
    agg_func: Literal['sum', 'mean'], default='sum'
        String of the function to use for aggregating the time series if the
        timescale is larger than 0. Can either be 'sum' or 'mean'.

    Attributes
    ----------
    _grouped_year : DataFrame
        Dataframe with all data grouped in a one-year (2000) DataFrame with the
        original years as columns
    _dist_dict : Dict[int, Dist]
        Dictionary of distributions used to fit the data.
    """

    series: Series = field(repr=False)
    dist: ContinuousDist
    timescale: int = 0
    fit_freq: str | None = field(default=None)
    fit_window: int = field(default=0)
    fit_method: Literal["MLE", "MM"] = field(default="MLE", repr=False)
    prob_zero: bool = field(default=False)
    normal_scores_transform: bool = field(default=False)
    agg_func: Literal["sum", "mean"] = "sum"
    _grouped_year: DataFrame = field(init=False, repr=False, compare=False)
    _dist_dict: dict[int, Dist] = field(
        default_factory=dict, init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        """
        Post initializes the SI class and performs necessary data
        preprocessing and validation.
        """
        self.series = validate_series(self.series)

        if self.timescale > 0:
            self.series = (
                self.series.rolling(self.timescale, min_periods=self.timescale)
                .agg(self.agg_func)
                .dropna()
                .copy()
            )

        if self.fit_freq is None:
            self.fit_freq = infer_frequency(self.series.index)

        self._grouped_year = group_yearly_df(series=self.series)

        if self.fit_window > 0:
            if self.fit_window < 3:
                logging.error(
                    "Window should be larger than 2. Setting the window value to 3."
                )
                self.fit_window = 3  # make sure window is at least three
            elif self.fit_window % 2 == 0:
                logging.error(
                    "Window should be odd. Setting the window value to"
                    f"{self.fit_window + 1}"
                )
                self.fit_window += 1  # make sure window is odd

    def fit_distribution(self) -> None:
        """
        Fit distribution on the time series per fit_frequency and/or fit_window
        """

        if self.normal_scores_transform:
            logging.info("Using normal-scores-transform. No distribution is fitted.")

        elif self.fit_window > 0:
            if self.fit_freq not in (
                "d",
                "w",
                "D",
                "W",
            ):  # TODO: ideally 14D should also work.
                raise ValueError(
                    "Frequency fit_freq must be 'D' or 'W', not "
                    f"'{self.fit_freq}', if a fit_window is provided."
                )

            logging.info("Using rolling window method")
            window = self.fit_window
            period = int(ceil(window / 2))
            if self.fit_freq in ("W", "w"):
                period = Timedelta(value=period, unit="W").days
                window = period * 2 + 1

            dfval_window = daily_window_group_yearly_df(
                dfval=self._grouped_year, period=period
            )
            for dfval_rwindow in dfval_window.rolling(
                window=window, min_periods=window, closed="right"
            ):
                if len(dfval_rwindow) < window:
                    continue  # min_periods ignored by Rolling.__iter__
                date = dfval_rwindow.index[period]
                data = get_data_series(dfval_rwindow.loc[[date]])
                data_window = get_data_series(dfval_rwindow)
                fd = Dist(
                    data=data,
                    dist=self.dist,
                    prob_zero=self.prob_zero,
                    data_window=data_window,
                    fit_method=self.fit_method,
                )
                self._dist_dict[date] = fd
        else:
            logging.info("Using groupby fit by frequency method")
            for date, grval in self._grouped_year.groupby(
                Grouper(freq=str(self.fit_freq))
            ):
                data = get_data_series(grval)
                fd = Dist(
                    data=data,
                    dist=self.dist,
                    prob_zero=self.prob_zero,
                    data_window=None,
                    fit_method=self.fit_method,
                )
                self._dist_dict[date] = fd  # type: ignore

    def cdf(self) -> Series:
        """Compute the cumulative density function"""
        if self.normal_scores_transform:
            cdf = self.cdf_nsf()
        else:
            cdf = Series(nan, index=self.series.index, dtype=float)
            for k in self._dist_dict:
                cdf_k = self._dist_dict[k].cdf()
                cdf.loc[cdf_k.index] = cdf_k.values

        return cdf

    def pdf(self) -> Series:
        """Compute the probability density function"""
        if self.normal_scores_transform:
            pdf = self.cdf().diff()
        else:
            pdf = Series(nan, index=self.series.index, dtype=float)
            for k in self._dist_dict:
                pdf_k = self._dist_dict[k].pdf()
                pdf.loc[pdf_k.index] = pdf_k.values
        return pdf

    def cdf_nsf(self) -> Series:
        """
        Compute the cumulative density function using the Normal Scores
        Transform

        Returns
        -------
        Series
        """
        logging.info("Using the normal scores transform")
        cdf = Series(nan, index=self.series.index, dtype=float)
        for _, grval in self._grouped_year.groupby(Grouper(freq=str(self.fit_freq))):
            data = get_data_series(grval).sort_values()
            n = len(data)
            cdf.loc[data.index] = linspace(1 / (2 * n), 1 - 1 / (2 * n), n)
        return cdf

    def ppf(self, q: float) -> Series:
        """
        Method to calculate the percentile point function
        (inverse of cdf — percentiles) of a fitted
        distribution.

        Parameters
        ----------
        q : float
            The quantile value (between 0 and 1) for which to calculate the
            percentile point function.

        Returns
        -------
        Series
        """
        ppf = Series(nan, index=self.series.index, dtype=float)
        if self.normal_scores_transform:
            cdf = self.cdf_nsf()
            for _, grval in self._grouped_year.groupby(
                Grouper(freq=str(self.fit_freq))
            ):
                data = get_data_series(grval).sort_values()
                cdf_i = cdf.loc[data.index]
                ppf.loc[data.index] = interp(
                    x=q,
                    xp=cdf_i.to_numpy(dtype=float),
                    fp=data.to_numpy(dtype=float),
                )
        else:
            for k in self._dist_dict:
                ppf_k = self._dist_dict[k].ppf(q=q)
                ppf.loc[ppf_k.index] = ppf_k.values
        return ppf

    def norm_ppf(self) -> Series:
        """
        Method to calculate propability point function of normal distribution
        based on a cumulative density function of a fitted distribution

        Returns
        -------
        Series
        """

        cdf = self.cdf()
        ppf = Series(
            norm.ppf(cdf.values, loc=0, scale=1), index=self.series.index, dtype=float
        )
        return ppf

    def get_dist(self, date: Timestamp) -> Dist:
        for k in self._dist_dict:
            dist = self._dist_dict[k]
            if date in dist.data.index:
                return dist

        raise KeyError("Date not found in distributions")
