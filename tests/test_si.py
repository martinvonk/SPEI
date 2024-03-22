from pandas import Series, Timestamp
from scipy.stats import norm

from spei import SI, sgi, spei, spi, ssfi


def test_spi(prec: Series) -> None:
    precr = prec.rolling("30D", min_periods=30).sum().dropna()
    spi(precr, fit_freq="ME", prob_zero=True)


def test_spei(prec: Series, evap: Series) -> None:
    n = (prec - evap).rolling("30D", min_periods=30).sum().dropna()
    spei(n, fit_freq="ME")


def test_sgi(head: Series) -> None:
    sgi(head, fit_freq="ME")


def test_sffi_timescale(prec: Series) -> None:
    ssfi(prec, timescale=30)


def test_window(prec: Series, evap: Series) -> None:
    n = (prec - evap).rolling("30D", min_periods=30).sum().dropna()
    spei(n, fit_freq="W", fit_window=3)


def test_SI(prec: Series) -> None:
    si = SI(prec, dist=norm, timescale=30, fit_freq="ME")
    si.fit_distribution()
    si.pdf()
    dist = si.get_dist(Timestamp("2010-01-01"))
    dist.ks_test()
