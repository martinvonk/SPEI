from pathlib import Path

import pytest
from pandas import Series, read_csv

from spei.si import spi


def read_data(column: str) -> Series:
    df = read_csv(
        Path(__file__).parent / "test_data/B11C0329_EAGMARYP.csv",
        index_col=0,
        parse_dates=True,
        sep=";",
    )
    return df.loc[:, column]


@pytest.fixture
def prec() -> Series:
    prec = read_data("Prec [m/d] 081_JOURE").dropna()
    return prec


@pytest.fixture
def precmm(prec) -> Series:
    return prec.multiply(1e3).rename("Prec [mm/d] 081_JOURE")


@pytest.fixture
def evap() -> Series:
    evap = read_data("Evap [m/d] 235_DE-KOOY").dropna()
    return evap


@pytest.fixture
def head() -> Series:
    head = read_data("Head [m] B11C0329_EAGMARYP").dropna()
    return head


@pytest.fixture
def si() -> Series:
    prec = read_data("Prec [m/d] 081_JOURE").dropna()
    si = spi(prec.rolling("30D", min_periods=30).sum().dropna(), prob_zero=True)
    return si
