from pandas import Series

from spei import sgi, spei, spi, ssfi


def test_spi(prec: Series) -> None:
    precr = prec.rolling("30D", min_periods=30).sum().dropna()
    spi(precr, fit_freq="ME", prob_zero=True)


def test_spei(prec: Series, evap: Series) -> None:
    n = (prec - evap).rolling("30D", min_periods=30).sum().dropna()
    spei(n, fit_freq="ME")


def test_sgi(head: Series) -> None:
    sgi(head, fit_freq="ME")


def test_sffi(prec: Series) -> None:
    sf = prec.rolling("30D", min_periods=30).sum().dropna()
    ssfi(sf)


def test_window(prec: Series, evap: Series) -> None:
    n = (prec - evap).rolling("30D", min_periods=30).sum().dropna()
    spei(n, fit_freq="W", fit_window=3)
