from pandas import Series
from spei import climdex


def test_climdex_rxnday(precmm: Series) -> None:
    climdex.rxnday(series=precmm, interval="10D", period="90D")


def test_climdex_rx1day(precmm: Series) -> None:
    climdex.rx1day(series=precmm)


def test_climdex_rx5day(precmm: Series) -> None:
    climdex.rx5day(series=precmm)


def test_climdex_sdii(precmm: Series) -> None:
    climdex.sdii(series=precmm)


def test_climdex_rnmm(precmm: Series) -> None:
    climdex.rnmm(series=precmm, threshold=5, period="90D")


def test_climdex_r10mm(precmm: Series) -> None:
    climdex.r10mm(series=precmm)


def test_climdex_r20mm(precmm: Series) -> None:
    climdex.r20mm(series=precmm)


def test_climdex_cdd(precmm: Series) -> None:
    climdex.cdd(series=precmm)


def test_climdex_cwd(precmm: Series) -> None:
    climdex.cwd(series=precmm)


def test_climdex_prcptot(precmm: Series) -> None:
    climdex.prcptot(series=precmm)


def test_climdex_rnnp(precmm: Series) -> None:
    climdex.rnnp(series=precmm, quantile=0.5)


def test_climdex_r95p(precmm: Series) -> None:
    climdex.r95p(series=precmm)


def test_climdex_r99p(precmm: Series) -> None:
    climdex.r99p(series=precmm)


def test_climdex_r95ptot(precmm: Series) -> None:
    climdex.r95ptot(series=precmm)


def test_climdex_r99ptot(precmm: Series) -> None:
    climdex.r99ptot(series=precmm)
