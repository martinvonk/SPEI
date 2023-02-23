from typing import Optional, Union

from numpy import linspace, std
from pandas import DatetimeIndex, Series
from scipy.stats import fisk, gamma, genextreme, norm

from ._typing import ContinuousDist, NDArrayFloat
from .utils import validate_index, validate_series


def compute_si_ppf(
    series: Series,
    dist: ContinuousDist,
    index: Optional[DatetimeIndex] = None,
    sgi: bool = False,
    prob_zero: bool = False,
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
    sgi : bool, optional
        Whether to caclulate the standardized groundwater index or not, by
        default False
    prob_zero : bool, optional
        Apply logic to observations that have value zero and calculate their
        probability seperately, by default False

    Returns
    -------
    Series
        Series with probability point function, ppf
    """

    if index is None:
        series = validate_series(series)
        index = validate_index(series.index)

    si = Series(index=index, dtype=float)
    for month in range(1, 13):
        data = series[index.month == month].sort_values()
        if not sgi:
            if prob_zero:
                cdf = compute_cdf_probzero(data=data, dist=dist)
            else:
                cdf = compute_cdf(data=data, dist=dist)
        else:
            cdf = compute_cdf_nsf(data=data)
        ppf = norm.ppf(cdf)
        si.loc[data.index] = ppf
    return si


def compute_cdf(
    data: Union[Series, NDArrayFloat], dist: ContinuousDist
) -> NDArrayFloat:
    *pars, loc, scale = dist.fit(data, scale=std(data))
    cdf = dist.cdf(data, pars, loc=loc, scale=scale)
    return cdf


def compute_cdf_probzero(
    data: Union[Series, NDArrayFloat], dist: ContinuousDist
) -> NDArrayFloat:
    p0 = (data == 0.0).sum() / len(data)
    *pars, loc, scale = dist.fit(data[data != 0.0], scale=std(data))
    cdf_sub = dist.cdf(data, pars, loc=loc, scale=scale)
    cdf = p0 + (1 - p0) * cdf_sub
    cdf[data == 0.0] = p0
    return cdf


def compute_cdf_nsf(data: Union[Series, NDArrayFloat]) -> NDArrayFloat:
    """Normal Scores Transform"""
    n = data.size
    cdf = linspace(1 / (2 * n), 1 - 1 / (2 * n), n)
    return cdf


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
    mock_dist = norm  # not used
    return compute_si_ppf(series=series, dist=mock_dist, sgi=True)


def spi(
    series: Series, dist: ContinuousDist = gamma, prob_zero: bool = False
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

    return compute_si_ppf(series=series, dist=dist, prob_zero=prob_zero)


def spei(series: Series, dist: ContinuousDist = fisk) -> Series:
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

    return compute_si_ppf(series=series, dist=dist)


def ssfi(series: Series, dist: Optional[ContinuousDist] = genextreme) -> Series:
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

    return compute_si_ppf(series=series, dist=dist)
