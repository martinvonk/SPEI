from typing import Optional

from pandas import Series
from scipy.stats import fisk, gamma, genextreme, norm

from ._typing import ContinuousDist
from .dist import compute_cdf_nsf, compute_si_ppf
from .utils import validate_index, validate_series


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

    series = validate_series(series)
    index = validate_index(series.index)
    si = Series(index=index, dtype=float)  # type: Series
    for month in range(1, 13):
        data = series[index.month == month].sort_values()
        cdf = compute_cdf_nsf(data=data.values.astype(float))
        si.loc[data.index] = norm.ppf(cdf)

    return si


def spi(
    series: Series,
    dist: ContinuousDist = gamma,
    prob_zero: bool = True,
    freq: Optional[str] = None,
    window: int = 0,
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

    return compute_si_ppf(
        series=series, dist=dist, prob_zero=prob_zero, freq=freq, window=window
    )


def spei(
    series: Series,
    dist: ContinuousDist = fisk,
    prob_zero: bool = True,
    freq: Optional[str] = None,
    window: int = 0,
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

    return compute_si_ppf(
        series=series, dist=dist, prob_zero=prob_zero, freq=freq, window=window
    )


def ssfi(
    series: Series,
    dist: Optional[ContinuousDist] = genextreme,
    prob_zero: bool = True,
    freq: Optional[str] = None,
    window: int = 0,
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

    return compute_si_ppf(
        series=series, dist=dist, prob_zero=prob_zero, freq=freq, window=window
    )
