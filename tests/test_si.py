from pandas import Series

from spei import sgi, spei, spi, ssfi

from .fixtures import evap, head, prec


def test_spi(prec: Series) -> None:
    spi(prec.rolling("30D", min_periods=30).sum().dropna(), prob_zero=True)


def test_spei(prec: Series, evap: Series) -> None:
    n = (prec - evap).rolling("30D", min_periods=30).sum().dropna()
    spei(n)


def test_sgi(head: Series) -> None:
    sgi(head)


def test_sffi(prec: Series) -> None:
    sf = prec.rolling("30D", min_periods=30).sum().dropna()
    ssfi(sf)
