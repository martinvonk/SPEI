from typing import TypeVar

from scipy.stats._continuous_distns import rv_continuous
from matplotlib.axes._base import _AxesBase
from numpy.typing import ArrayLike

ContinuousDist = TypeVar("ContinuousDist", bound=rv_continuous)
Axes = TypeVar("Axes", bound=_AxesBase)
ArrayLike = TypeVar("ArrayLike", bound=ArrayLike)