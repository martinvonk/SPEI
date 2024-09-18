from pandas import DataFrame, Series, Timestamp
from scipy.stats import norm
from spei import SI, sgi, spei, spi, ssfi
from spei.dist import Dist


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


def test_SI_post_init_timescale(prec: Series) -> None:
    si = SI(prec, dist=norm, timescale=30, fit_freq="ME")
    assert si.series.equals(
        prec.rolling(30, min_periods=30).sum().dropna()
    ), "Timescale rolling sum not applied correctly"


def test_SI_post_init_fit_freq_infer(prec: Series) -> None:
    si = SI(prec, dist=norm, timescale=0)
    assert si.fit_freq is not None, "Frequency inference failed"


def test_SI_post_init_grouped_year(prec: Series) -> None:
    si = SI(prec, dist=norm, timescale=0, fit_freq="ME")
    assert isinstance(si._grouped_year, DataFrame), "Grouped year DataFrame not created"


def test_SI_post_init_fit_window_adjustment(prec: Series) -> None:
    si = SI(prec, dist=norm, timescale=0, fit_freq="D", fit_window=2)
    assert si.fit_window == 3, "Fit window not adjusted to odd number"


def test_SI_post_init_fit_window_minimum(prec: Series) -> None:
    si = SI(prec, dist=norm, timescale=0, fit_freq="D", fit_window=1)
    assert si.fit_window == 3, "Fit window not adjusted to minimum value"


def test_fit_distribution_normal_scores_transform(prec: Series) -> None:
    si = SI(prec, dist=norm, timescale=30, fit_freq="ME", normal_scores_transform=True)
    si.fit_distribution()
    assert (
        not si._dist_dict
    ), "Distribution dictionary should be empty when using normal scores transform"


def test_fit_distribution_with_fit_window(prec: Series) -> None:
    si = SI(prec, dist=norm, timescale=30, fit_freq="D", fit_window=5)
    si.fit_distribution()
    assert (
        si._dist_dict
    ), "Distribution dictionary should not be empty when using fit window"
    for dist in si._dist_dict.values():
        assert isinstance(
            dist, Dist
        ), "Items in distribution dictionary should be of type Dist"


def test_fit_distribution_with_fit_freq(prec: Series) -> None:
    si = SI(prec, dist=norm, timescale=30, fit_freq="M")
    si.fit_distribution()
    assert (
        si._dist_dict
    ), "Distribution dictionary should not be empty when using fit frequency"
    for dist in si._dist_dict.values():
        assert isinstance(
            dist, Dist
        ), "Items in distribution dictionary should be of type Dist"


def test_fit_distribution_invalid_fit_freq_with_window(prec: Series) -> None:
    si = SI(prec, dist=norm, timescale=30, fit_freq="M", fit_window=5)
    try:
        si.fit_distribution()
    except ValueError as e:
        assert (
            str(e)
            == "Frequency fit_freq must be 'D' or 'W', not 'M', if a fit_window is provided."
        )
    else:
        assert False, "ValueError not raised for invalid fit frequency with fit window"
