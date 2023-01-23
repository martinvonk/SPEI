import pytest
from spei.si import spi
from pandas import read_csv, Series


def read_data(column: str) -> Series:
    df = read_csv(
        "https://raw.githubusercontent.com/pastas/test-datasets/main/vanderspek_bakker_2017/B11C0329_EAGMARYP.csv",
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
