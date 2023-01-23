import pytest
from scipy.stats import pearson3
from pandas import Series
from spei.plot import si as plot_si
from spei.plot import dist, monthly_density
from .fixtures import prec, si


def test_plot_si(si: Series) -> None:
    _ = plot_si(si)


def test_plot_dist(prec: Series) -> None:
    series = prec.rolling("90D", min_periods=90).sum().dropna()
    _ = dist(series, dist=pearson3, test_dist=False)


def test_plot_dist_cum(prec: Series) -> None:
    series = prec.rolling("90D", min_periods=90).sum().dropna()
    _ = dist(series, dist=pearson3, cumulative=True, test_dist=False)


def test_plot_dist_test(prec: Series) -> None:
    series = prec.rolling("90D", min_periods=90).sum().dropna()
    _ = dist(series, dist=pearson3, test_dist=True, cmap="viridis")


def test_plot_monthly_density(si: Series) -> None:
    _ = monthly_density(si, years=[2011], months=[1, 2, 3, 4, 5])
