from typing import Any
from pandas import Series
from numpy import linspace
from scipy.stats import norm, gamma, fisk, genextreme
from .utils import check_series


def get_si_ppf(
    series: Series,
    dist: Any,
    sgi: bool = False,
    prob_zero: bool = False,
) -> Series:

    check_series(series)

    si = Series(index=series.index, dtype="float")
    for month in range(1, 13):
        data = series[series.index.month == month].sort_values()
        if sgi:
            pmin = 1 / (2 * data.size)
            pmax = 1 - pmin
            cdf = linspace(pmin, pmax, data.size)
        else:
            if prob_zero:
                p0 = (data == 0.0).sum() / len(data)
                pars, loc, scale = dist.fit(data[data != 0.0], scale=data.std())
                cdf_sub = dist.cdf(data, pars, loc=loc, scale=scale)
                cdf = p0 + (1 - p0) * cdf_sub
                cdf[data == 0.0] = p0
            else:
                *pars, loc, scale = dist.fit(data, scale=data.std())
                cdf = dist.cdf(data, pars, loc=loc, scale=scale)
        ppf = norm.ppf(cdf)
        si.loc[data.index] = ppf

    return si


def sgi(series: Series) -> Series:
    """Method to compute the Standardized Groundwater Index [sgi_2013]_.
    Same method as in Pastas.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the groundwater levels. Time series index
        should be a pandas DatetimeIndex.

    Returns
    -------
    pandas.Series

    References
    ----------
    .. [sgi_2013] Bloomfield, J. P. and Marchant, B. P.: Analysis of
       groundwater drought building on the standardised precipitation index
       approach. Hydrol. Earth Syst. Sci., 17, 4769–4787, 2013.
    """

    return get_si_ppf(series, None, sgi=True)


def spi(series: Series, dist: Any = None, prob_zero: bool = False) -> Series:
    """Method to compute the Standardized Precipitation Index [spi_2002]_.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the precipitation. Time series index
        should be a pandas DatetimeIndex.
    dist: scipy.stats._continuous_distns
        Can be any continuous distribution from the scipy.stats library.
        However, for the SPI generally the Gamma probability density
        function is recommended. Other appropriate choices could be the
        lognormal, log-logistic (fisk) or PearsonIII distribution.
    prob_zero: bool
        Option to correct the distribution if x=0 is not in probability
        density function. E.g. the case with the Gamma distriubtion.

    Returns
    -------
    pandas.Series

    References
    ----------
    .. [spi_2002] LLoyd-Hughes, B. and Saunders, M.A.: A drought
       climatology for Europe. International Journal of Climatology,
       22, 1571-1592, 2002.
    """

    if dist == None:
        dist = gamma

    return get_si_ppf(series, dist, prob_zero)


def spei(series: Series, dist: Any = None) -> Series:
    """Method to compute the Standardized Precipitation Evaporation Index [spei_2010]_.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the precipitation. Time series index
        should be a pandas DatetimeIndex.
    dist: scipy.stats._continuous_distns
        Can be any continuous distribution from the scipy.stats library.
        However, for the SPEI generally the log-logistic (fisk) probability
        density function is recommended. Other appropriate choices could be
        the lognormal or PearsonIII distribution.

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

    if dist == None:
        dist = fisk  # log-logistic

    return get_si_ppf(series, dist)


def ssfi(series: Series, dist: Any = None) -> Series:
    """Method to compute the Standardized StreamFlow Index [ssfi_2020]_.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the precipitation. Time series index
        should be a pandas DatetimeIndex.
    dist: scipy.stats._continuous_distns
        Can be any continuous distribution from the scipy.stats library.
        However, for the SSFI generally the gamma probability density
        function is recommended. Other appropriate choices could be the
        normal, lognormal, pearsonIII, GEV or  Gen-Logistic distribution.

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

    if dist == None:
        dist = genextreme

    return get_si_ppf(series, dist)
