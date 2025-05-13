import numpy as np
import pandas as pd
import pytest

from spei.knmi import (
    deficit_apr1,
    deficit_gdd,
    deficit_max,
    deficit_oct1,
    deficit_wet,
    get_cumulative_deficit,
    get_yearly_temp_date,
)
from spei.plot import deficit_knmi


@pytest.fixture
def temp(deficit: pd.Series) -> pd.Series:
    sine_wave = np.sin(2 * np.pi * np.arange(len(deficit)) / 365) * 15 + 15
    temp = pd.Series(data=sine_wave, index=deficit.index, dtype=float)
    return temp


def test_get_yearly_temp_date(temp):
    threshold = 440.0
    result = get_yearly_temp_date(temp=temp, threshold=threshold)
    assert isinstance(result, pd.Series)


def test_get_cumulative_deficit(deficit):
    startdate = pd.Timestamp("2000-04-01")
    enddate = pd.Timestamp("2000-09-30")
    result = get_cumulative_deficit(
        deficit=deficit, startdate=startdate, enddate=enddate
    )
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


def test_deficit_oct1(deficit):
    result = deficit_oct1(deficit=deficit)
    assert isinstance(result, pd.Series)
    assert result.name == "Doct1"


def test_deficit_max(deficit):
    result = deficit_max(deficit=deficit)
    assert isinstance(result, pd.Series)
    assert result.name == "Dmax"


def test_deficit_apr1(deficit):
    result = deficit_apr1(deficit=deficit)
    assert isinstance(result, pd.Series)
    assert result.name == "DIapr1"


def test_deficit_gdd(deficit, temp):
    threshold = 440
    result = deficit_gdd(
        deficit=deficit,
        temp=temp,
        threshold=threshold,
    )
    assert isinstance(result, pd.Series)
    assert result.name == "DIgdd"


def test_deficit_wet(deficit):
    result = deficit_wet(deficit=deficit)
    assert isinstance(result, pd.Series)
    assert result.name == "DIwet"


def test_plot_knmi_deficit(deficit: pd.Series):
    """Test the plot function for the deficit."""
    startdate = pd.Timestamp("2000-04-01")
    enddate = pd.Timestamp("2000-09-30")
    cumdf = get_cumulative_deficit(
        deficit=deficit,
        startdate=startdate,
        enddate=enddate,
        allow_below_zero=False,
    )
    ax = deficit_knmi(cumdf)
    assert ax is not None
    assert ax.get_ylabel() == "Precipitation deficit (mm)"
