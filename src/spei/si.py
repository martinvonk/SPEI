import logging
from dataclasses import dataclass, field
from typing import Dict, Optional

from numpy import ceil, linspace, nan
from pandas import DataFrame, Grouper, Series, Timedelta, Timestamp
from scipy.stats import fisk, gamma, genextreme, norm

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
    fit_freq: Optional[str] = None,
) -> Series:
    """Method to compute the Standardized Groundwater Index [sgi_2013]_. Same
    method as in Pastas. Uses the normal scores transform to calculate the
    cumulative density function.

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
    .. [sgi_2013] Bloomfield, J. P. and Marchant, B. P.: Analysis of
       groundwater drought building on the standardised precipitation index
       approach. Hydrol. Earth Syst. Sci., 17, 4769–4787, 2013.
    """

    mock_dist = norm
    sgi = SI(
        series=series,
        dist=mock_dist,
        timescale=0,
        fit_freq=fit_freq,
        fit_window=0,
        prob_zero=False,
        normal_scores_transform=True,
    )
    return sgi.norm_ppf()


def spi(
    series: Series,
    dist: ContinuousDist = gamma,
    timescale: int = 0,
    fit_freq: Optional[str] = None,
    fit_window: int = 0,
    prob_zero: bool = True,
) -> Series:
    """Method to compute the Standardized Precipitation Index [spi_2002]_.

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
    .. [spi_2002] LLoyd-Hughes, B. and Saunders, M.A.: A drought
       climatology for Europe. International Journal of Climatology,
       22, 1571-1592, 2002.
    """

    spi = SI(
        series=series,
        dist=dist,
        timescale=timescale,
        fit_freq=fit_freq,
        fit_window=fit_window,
        prob_zero=prob_zero,
        normal_scores_transform=False,
    )
    spi.fit_distribution()
    return spi.norm_ppf()


def spei(
    series: Series,
    dist: ContinuousDist = fisk,
    timescale: int = 0,
    fit_freq: Optional[str] = None,
    fit_window: int = 0,
    prob_zero: bool = False,
) -> Series:
    """Method to compute the Standardized Precipitation Evaporation Index
    [spei_2010]_.

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
    .. [spei_2010] Vicente-Serrano S.M., Beguería S., López-Moreno J.I.:
       A Multi-scalar drought index sensitive to global warming: The
       Standardized Precipitation Evapotranspiration Index.
       Journal of Climate, 23, 1696-1718, 2010.
    """

    spei = SI(
        series=series,
        dist=dist,
        timescale=timescale,
        fit_freq=fit_freq,
        fit_window=fit_window,
        prob_zero=prob_zero,
        normal_scores_transform=False,
    )
    spei.fit_distribution()
    return spei.norm_ppf()


def ssfi(
    series: Series,
    dist: ContinuousDist = genextreme,
    timescale: int = 0,
    fit_freq: Optional[str] = None,
    fit_window: int = 0,
    prob_zero: bool = True,
) -> Series:
    """Method to compute the Standardized StreamFlow Index [ssfi_2020]_.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the precipitation. Time series index
        should be a pandas DatetimeIndex.
    dist: scipy.stats.rv_continuous
        Can be any continuous distribution from the scipy.stats library.
        However, for the SSFI generally the gamma probability density
        function is recommended. Other appropriate choices could be the
        normal, lognormal, pearsonIII, GEV or  Gen-Logistic distribution.
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
    .. [ssfi_2020] Tijdeman, E., Stahl, K., & Tallaksen, L. M.:
       Drought characteristics derived based on the Standardized
       Streamflow Index: A large sample comparison for parametric
       and nonparametric methods. Water Resources Research, 56, 2020.
    """
    ssfi = SI(
        series=series,
        dist=dist,
        timescale=timescale,
        fit_freq=fit_freq,
        fit_window=fit_window,
        prob_zero=prob_zero,
        normal_scores_transform=False,
    )
    ssfi.fit_distribution()
    return ssfi.norm_ppf()


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
    prob_zero : bool, default=False
        Flag indicating whether the probability of zero values in the series is
        calculated by the occurence.
    normal_scores_transform : bool, default=False
        Flag to use the normal scores transformation for calculating the
        cumulative density function.

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
    fit_freq: Optional[str] = field(default=None)
    fit_window: int = field(default=0)
    prob_zero: bool = field(default=False)
    normal_scores_transform: bool = field(default=False)
    _grouped_year: DataFrame = field(init=False, repr=False, compare=False)
    _dist_dict: Dict[int, Dist] = field(
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
                .sum()
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

    def fit_distribution(self):
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
                )
                self._dist_dict[date] = fd

    def cdf(self):
        """Compute the cumulative density function"""
        if self.normal_scores_transform:
            cdf = self.cdf_nsf()
        else:
            cdf = Series(nan, index=self.series.index, dtype=float)
            for k in self._dist_dict:
                cdf_k = self._dist_dict[k].cdf()
                cdf.loc[cdf_k.index] = cdf_k.values

        return cdf

    def pdf(self):
        """Compute the probability density function"""
        if self.normal_scores_transform:
            pdf = self.cdf().diff()
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
