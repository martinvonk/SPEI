from pandas import Series

from spei.rai import mrai, rai


def test_rai(prec: Series) -> None:
    precrs = prec.resample("MS").sum()
    rai_result = rai(precrs)
    assert isinstance(rai_result, Series), "RAI result is not a pandas Series"
    assert len(rai_result) == len(precrs), (
        "RAI result length does not match input length"
    )


def test_mrai(prec: Series) -> None:
    precrs = prec.resample("MS").sum()
    mrai_result = mrai(precrs)
    assert isinstance(mrai_result, Series), "MRAI result is not a pandas Series"
    assert len(mrai_result) == len(precrs), (
        "MRAI result length does not match input length"
    )
